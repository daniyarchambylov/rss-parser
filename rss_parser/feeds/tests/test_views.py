from django.contrib.auth import get_user_model
from django.test import TestCase
from django_celery_beat.models import PeriodicTask
from datetime import datetime
from unittest.mock import patch
from rss_parser.feeds.models import Feed, FeedArticle, FeedArticleComments


User = get_user_model()


class BaseTestDataTestCase(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.user1 = User.objects.create(username='test1', first_name="Test", last_name="First")

        feed1 = Feed.objects.create(
            title='Test',
            link='https://test.com',
            rss_link='https://test.com',
            publisher='Test',
            updated_at=datetime(2019, 3, 22)
        )

        feed2 = Feed.objects.create(
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
            'link': 'https://feed1.test/2',
            'author': 'Test publisher',
            'published_at': datetime.now(),
        }, {
            'title': 'Test 3',
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
        }, {
            'title': 'Test 5',
            'summary': 'Summary',
            'link': 'https://feed2.test/2',
            'author': 'Test publisher',
            'published_at': datetime.now(),
        }]

        list(map(lambda x: FeedArticle.create_from_feedparser(feed1, x), feed1_article_data))
        user2_feeds = list(map(lambda x: FeedArticle.create_from_feedparser(feed2, x), feed2_article_data))

        cls.user1.feeds.add(feed1)
        cls.user1.bookmarked_articles.add(user2_feeds[0])


class AllFeedsViewTestCase(BaseTestDataTestCase):
    def test_all_feeds_redirect_anonymous(self):
        response = self.client.get('/')
        self.assertRedirects(response, '/login/?next=/')

    def test_all_feeds_ok(self):
        self.client.force_login(self.user1)
        response = self.client.get('/')
        ctx = response.context
        self.assertEquals(response.status_code, 200)
        self.assertEquals(ctx['page_title'], 'Feeds')
        self.assertEquals(len(ctx['object_list']), 5)


class SubscribedFeedsViewTestCase(BaseTestDataTestCase):
    def test_all_feeds_redirect_anonymous(self):
        response = self.client.get('/my-feeds/')
        self.assertRedirects(response, '/login/?next=/my-feeds/')

    def test_all_feeds_ok(self):
        self.client.force_login(self.user1)
        response = self.client.get('/my-feeds/')
        ctx = response.context
        self.assertEquals(response.status_code, 200)
        self.assertEquals(ctx['page_title'], 'My Feeds')
        self.assertEquals(len(ctx['object_list']), 3)


class BookmarkedFeedsViewTestCase(BaseTestDataTestCase):
    def test_all_feeds_redirect_anonymous(self):
        response = self.client.get('/bookmarks/')
        self.assertRedirects(response, '/login/?next=/bookmarks/')

    def test_all_feeds_ok(self):
        self.client.force_login(self.user1)
        response = self.client.get('/bookmarks/')
        ctx = response.context
        self.assertEquals(response.status_code, 200)
        self.assertEquals(ctx['page_title'], 'Bookmarks')
        self.assertEquals(len(ctx['object_list']), 1)


class AddRssFeedViewTestCase(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.user = User.objects.create(first_name='Test', last_name='User', username='test')

    def test_anonymous_redirect(self):
        response = self.client.get('/settings/')
        self.assertRedirects(response, '/login/?next=/settings/')

    def test_render_page(self):
        self.client.force_login(self.user)
        response = self.client.get('/settings/')
        self.assertEquals(response.status_code, 200)
        self.assertTemplateUsed(response, 'feeds/new_feed.html')

    @patch('rss_parser.feeds.forms.parse')
    def test_post_ok(self, mocked_parse):
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
        self.client.force_login(self.user)
        response = self.client.post('/settings/', {
            'url': 'https://rss.com/valid-rss-url/'
        })
        self.assertEquals(response.status_code, 302)
        self.assertRedirects(response, '/')
        self.assertTrue(mocked_parse.called)


class ArticleCommentView(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.user = User.objects.create(first_name='Test', last_name='User', username='test')

        feed = Feed.objects.create(
            title='Test',
            link='https://test.com',
            rss_link='https://test.com',
            publisher='Test',
            updated_at=datetime.now()
        )

        cls.article = FeedArticle.objects.create(
            feed=feed,
            title='Test 1',
            summary='Summary',
            link='https://feed1.test/1',
            author='Test publisher',
            published_at=datetime.now(),
        )

        FeedArticleComments.objects.create(article=cls.article, user=cls.user, comment='Comment 1')
        FeedArticleComments.objects.create(article=cls.article, user=cls.user, comment='Comment 2')

    def test_anonymous_redirect(self):
        response = self.client.get('/articles/{}/'.format(self.article.id))
        self.assertRedirects(response, '/login/?next=/articles/{}/'.format(self.article.id))

    def test_display_page(self):
        self.client.force_login(self.user)
        response = self.client.get('/articles/{}/'.format(self.article.id))
        ctx = response.context
        self.assertEquals(response.status_code, 200)
        self.assertEquals(len(ctx['comments']), 2)
        self.assertTemplateUsed('feeds/feed_details.html')

    def test_display_page_404(self):
        self.client.force_login(self.user)
        response = self.client.get('/articles/{}/'.format(0))
        self.assertEquals(response.status_code, 404)

    def test_add_comment(self):
        self.client.force_login(self.user)
        response = self.client.post('/articles/{}/'.format(self.article.id), {
            'comment': 'Comment 3',
            'user': self.user.id,
            'article': self.article.id
        })
        self.assertEquals(response.status_code, 302)
        self.assertRedirects(response, '/articles/{}/'.format(self.article.id))

    def test_add_comment_error(self):
        self.client.force_login(self.user)
        response = self.client.post('/articles/{}/'.format(self.article.id), {
            'user': self.user.id,
            'article': self.article.id
        })
        ctx = response.context
        self.assertEquals(response.status_code, 200)
        self.assertEquals(list(ctx['form'].errors.keys()), ['comment'])


class ToggleBookmarkViewTestCase(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.user = User.objects.create(first_name='Test', last_name='User', username='test')

        feed = Feed.objects.create(
            title='Test',
            link='https://test.com',
            rss_link='https://test.com',
            publisher='Test',
            updated_at=datetime.now()
        )

        cls.article = FeedArticle.objects.create(
            feed=feed,
            title='Test 1',
            summary='Summary',
            link='https://feed1.test/1',
            author='Test publisher',
            published_at=datetime.now(),
        )

    def test_toggle_405(self):
        response = self.client.get('/toggle-bookmark/{}/'.format(self.article.id))
        self.assertEquals(response.status_code, 405)

    def test_login_required(self):
        response = self.client.post('/toggle-bookmark/{}/'.format(self.article.id))
        self.assertEquals(response.status_code, 302)

    def test_article_does_not_exist(self):
        self.client.force_login(self.user)
        response = self.client.post('/toggle-bookmark/0/')
        res = response.json()
        self.assertEquals(response.status_code, 200)
        self.assertEquals(res['status'], 'error')

    def test_article_toggle(self):
        self.client.force_login(self.user)
        response = self.client.post('/toggle-bookmark/{}/'.format(self.article.id))
        res = response.json()
        self.assertEquals(response.status_code, 200)
        self.assertEquals(res['status'], 'success')


class ResumeFeedUpdateViewTestCase(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.user = User.objects.create(first_name='Test', last_name='User', username='test')

        cls.feed = Feed.objects.create(
            title='Test',
            link='https://test.com',
            rss_link='https://test.com',
            publisher='Test',
            updated_at=datetime.now()
        )

        cls.task = PeriodicTask.objects.create(name=cls.feed.rss_link, task='task', enabled=False)

    def test_toggle_405(self):
        response = self.client.get('/resume-feed-update/{}/'.format(self.task.id))
        self.assertEquals(response.status_code, 200)

    def test_login_required(self):
        response = self.client.post('/resume-feed-update/{}/'.format(self.task.id))
        self.assertEquals(response.status_code, 200)

    def test_task_does_not_exist(self):
        self.client.force_login(self.user)
        response = self.client.post('/resume-feed-update/0/')
        self.assertEquals(response.status_code, 200)

    def test_403(self):
        self.client.force_login(self.user)
        response = self.client.post('/resume-feed-update/{}/'.format(self.task.id))
        self.assertEquals(response.status_code, 200)

    def test_success(self):
        self.client.force_login(self.user)
        self.user.feeds.add(self.feed)
        response = self.client.post('/resume-feed-update/{}/'.format(self.task.id))
        res = response.json()
        self.assertEquals(response.status_code, 200)
        self.assertEquals(res['status'], 'success')
        task = PeriodicTask.objects.get(id=self.task.id)
        self.assertTrue(task.enabled)
