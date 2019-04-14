from django.test import TestCase
from django.contrib.auth import get_user_model
from datetime import datetime
from unittest.mock import patch
from rss_parser.feeds.models import Feed, FeedArticle
from rss_parser.feeds.forms import NewRssFeedForm

User = get_user_model()


class NewRssFeedFormTestCase(TestCase):
    def test_url_is_required(self):
        form = NewRssFeedForm()
        self.assertFalse(form.is_valid())

    def test_url_is_invalid(self):
        form = NewRssFeedForm(data={'url': 'test'})
        self.assertFalse(form.is_valid())

    @patch('rss_parser.feeds.forms.parse')
    def test_url_format_error(self, mocked_parse):
        mocked_parse.side_effect = TypeError('Format error.')
        form = NewRssFeedForm(data={'url': 'https://test.com/rss'})
        self.assertFalse(form.is_valid())
        self.assertTrue(mocked_parse.called)

    @patch('rss_parser.feeds.forms.parse')
    def test_ok(self, mocked_parse):
        user = User.objects.create(username='test', first_name='Test', last_name='User')
        timetuple = datetime(2019, 2, 21).timetuple()
        mocked_parse.return_value = {
            'link': '/',
            'title': 'Test title',
            'publisher': 'Test publisher',
            'updated_at': datetime(2019, 2, 21),
            'rss_link': '/',
            'items': [
                {'title': 'Test 1', 'summary': 'S', 'link': '/1', 'author': 'A', 'published_parsed': timetuple},
                {'title': 'Test 2', 'summary': 'S', 'link': '/2', 'author': 'A', 'published_parsed': timetuple},
            ],
        }

        form = NewRssFeedForm(data={'url': 'https://test.com/rss'})
        is_valid = form.is_valid()
        feed = form.save(user)
        self.assertTrue(is_valid)
        self.assertIsInstance(feed, Feed)
        self.assertEqual(FeedArticle.objects.filter(feed=feed).count(), 2)
        self.assertEqual(user.feeds.count(), 1)
