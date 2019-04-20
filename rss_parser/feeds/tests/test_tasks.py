from django.test import TestCase
from django_celery_beat.models import IntervalSchedule, PeriodicTask
from celery.exceptions import MaxRetriesExceededError
from unittest.mock import patch
from datetime import datetime
from rss_parser.feeds.models import Feed
from rss_parser.feeds.tasks import update_feed
from rss_parser.feeds.exc import FeedParserError
import json


class UpdateFeedTaskTestCase(TestCase):
    @classmethod
    def setUpTestData(cls):
        schedule = IntervalSchedule.objects.create(
            every=600000,
            period=IntervalSchedule.SECONDS
        )
        cls.task = PeriodicTask.objects.create(
            interval=schedule,
            name='https://test-task.com',
            task='test-task',
            args=json.dumps(['https://test-task.com']),
        )

    @patch('rss_parser.feeds.tasks.parse')
    def test_ok(self, mocked_parse):
        timetuple = datetime(2019, 2, 21).timetuple()
        mocked_parse.return_value = {
            'link': 'https://test-task.com',
            'title': 'Test title',
            'publisher': 'Test publisher',
            'updated_at': datetime(2019, 2, 21),
            'rss_link': 'https://test-task.com',
            'items': [
                {'title': 'Test 1', 'summary': 'S', 'link': '/1', 'author': 'A', 'published_parsed': timetuple},
                {'title': 'Test 2', 'summary': 'S', 'link': '/2', 'author': 'A', 'published_parsed': timetuple},
            ],
        }
        res = update_feed('https://test-task.com')
        self.assertIsInstance(res, Feed)

    @patch('rss_parser.feeds.tasks.parse')
    @patch('rss_parser.feeds.tasks.update_feed.retry')
    def test_raises_retry(self, task_retry, mocked_parse):
        mocked_parse.side_effect = FeedParserError()
        task_retry.side_effect = MaxRetriesExceededError()
        update_feed('https://test-task.com')

        task = PeriodicTask.objects.get(name='https://test-task.com')
        self.assertFalse(task.enabled)

    def test_disabled(self):
        self.task.enabled = False
        self.task.save()
        self.assertIsNone(update_feed('https://test-task.com'))
