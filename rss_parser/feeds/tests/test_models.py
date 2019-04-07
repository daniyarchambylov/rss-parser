from django.test import TestCase
from datetime import datetime
from rss_parser.feeds.models import Feed, FeedArticle


class FeedTestCase(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.input_data = {
            'title': 'Test title',
            'link': 'https://feed.test',
            'rss_link': 'https://feed.test',
            'publisher': 'Test publisher',
            'updated_at': datetime(2019, 3, 22),
        }

    def test_create_from_feedparser_new(self):
        feed = Feed.create_from_feedparser(self.input_data)
        self.assertIsInstance(feed, Feed)
        self.assertEqual(Feed.objects.count(), 1)

    def test_create_from_feedparser_updated(self):
        new_data = self.input_data.copy()
        new_data['updated_at'] = datetime(2019, 3, 24)
        Feed.create_from_feedparser(self.input_data)
        feed = Feed.create_from_feedparser(new_data)
        self.assertEqual(feed.updated_at, new_data['updated_at'])
        self.assertEqual(Feed.objects.count(), 1)


class FeedArticleTestCase(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.feed = Feed.objects.create(
            title='Test',
            link='https://test.com',
            rss_link='https://test.com',
            publisher='Test',
            updated_at=datetime(2019, 3, 22)
        )
        cls.article_data = {
            'title': 'Test 1',
            'summary': 'Summary',
            'link': 'https://feed.test/1',
            'author': 'Test publisher',
            'published_at': datetime.now(),
        }

    def test_create_from_feedparser_new(self):
        article = FeedArticle.create_from_feedparser(self.feed, self.article_data)
        self.assertIsInstance(article, FeedArticle)

    def test_create_from_feedparser_duplicate(self):
        article = FeedArticle.create_from_feedparser(self.feed, self.article_data)
        duplicate = FeedArticle.create_from_feedparser(self.feed, self.article_data)

        self.assertIsInstance(article, FeedArticle)
        self.assertIsNone(duplicate)
