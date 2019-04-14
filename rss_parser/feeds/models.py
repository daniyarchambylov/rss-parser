from django.db import models
from django.conf import settings


class Feed(models.Model):
    title = models.CharField(max_length=255)
    link = models.URLField(unique=True)
    rss_link = models.URLField(unique=True)
    publisher = models.CharField(max_length=100)
    updated_at = models.DateTimeField()

    @classmethod
    def create_from_feedparser(cls, data):
        get_or_create_data = {
            'title': data['title'],
            'link': data['link'],
            'rss_link': data['rss_link'],
            'publisher': data['publisher'],
        }
        try:
            feed = cls.objects.get(**get_or_create_data)
        except cls.DoesNotExist:
            feed = cls(**get_or_create_data)

        feed.updated_at = data['updated_at']
        feed.save()
        return feed


class FeedArticle(models.Model):
    title = models.CharField(max_length=255)
    summary = models.TextField()
    link = models.URLField(unique=True)
    author = models.CharField(max_length=100)
    published_at = models.DateTimeField()
    feed = models.ForeignKey(Feed, on_delete=models.CASCADE, related_name='aricles')

    @classmethod
    def create_from_feedparser(cls, feed, feed_item):
        if (cls.objects.filter(link=feed_item['link']).exists()):
            return None

        feed_article = cls(
            title=feed_item['title'],
            summary=feed_item['summary'],
            link=feed_item['link'],
            author=feed_item['author'],
            published_at=feed_item['published_at'],
            feed=feed
        )
        feed_article.save()
        return feed_article

    @classmethod
    def list_user_feed_items(cls, user):
        return cls.objects.filter(feed__users=user)

    @classmethod
    def list_bookmarked(cls, user):
        return cls.objects.filter(users=user)


class FeedArticleComments(models.Model):
    article = models.ForeignKey(FeedArticle, on_delete=models.CASCADE, related_name='comments')
    comment = models.TextField()
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='article_comments')
    created_at = models.DateTimeField(auto_now_add=True)

    @classmethod
    def filter_by_feed_article(cls, article, order_by='-id'):
        return cls.objects.filter(article=article).order_by(order_by)
