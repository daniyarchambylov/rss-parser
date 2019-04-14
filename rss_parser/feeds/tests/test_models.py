from django.test import TestCase
from django.contrib.auth import get_user_model
from datetime import datetime
from rss_parser.feeds.models import Feed, FeedArticle


User = get_user_model()


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


class FeedArticleCreateTestCase(TestCase):
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


class FeedArticleMethodsTestCase(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.user1 = User.objects.create(username='test1', first_name="Test", last_name="First")
        cls.user2 = User.objects.create(username='test2', first_name="Test", last_name="Second")

        cls.feed1 = Feed.objects.create(
            title='Test',
            link='https://test.com',
            rss_link='https://test.com',
            publisher='Test',
            updated_at=datetime(2019, 3, 22)
        )

        cls.feed2 = Feed.objects.create(
            title='Test2',
            link='https://test2.com',
            rss_link='https://test2.com',
            publisher='Test2',
            updated_at=datetime(2019, 3, 22)
        )

        feed1_article_data = [{
            'title': 'Test 1',
            'summary': 'Summary',
            'link': 'https://feed1.test/1',
            'author': 'Test publisher',
            'published_at': datetime.now(),
        }, {
            'title': 'Test 2',
            'summary': 'Summary',
            'link': 'https://feed1.test/3',
            'author': 'Test publisher',
            'published_at': datetime.now(),
        }]

        feed2_article_data = [{
            'title': 'Test 4',
            'summary': 'Summary',
            'link': 'https://feed2.test/1',
            'author': 'Test publisher',
            'published_at': datetime.now(),
        }]

        user1_feeds = list(map(lambda x: FeedArticle.create_from_feedparser(cls.feed1, x), feed1_article_data))
        user2_feeds = list(map(lambda x: FeedArticle.create_from_feedparser(cls.feed2, x), feed2_article_data))

        cls.user1.feeds.add(cls.feed1)
        cls.user2.feeds.add(cls.feed2)

        cls.user1.bookmarked_articles.add(user1_feeds[0])
        cls.user1.bookmarked_articles.add(user2_feeds[0])

    def test_list_user_feed_items(self):
        artilces = FeedArticle.list_user_feed_items(self.user1)
        artilces2 = FeedArticle.list_user_feed_items(self.user2)
        self.assertEqual(artilces.count(), 2)
        self.assertEqual(artilces2.count(), 1)

    def test_list_bookmarked(self):
        artilces = FeedArticle.list_bookmarked(self.user1)
        artilces2 = FeedArticle.list_bookmarked(self.user2)
        self.assertEqual(artilces.count(), 2)
        self.assertEqual(artilces2.count(), 0)
