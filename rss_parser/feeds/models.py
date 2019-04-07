from django.db import models


class Feed(models.Model):
    title = models.CharField(max_length=255)
    link = models.URLField()
    rss_link = models.URLField()
    publisher = models.CharField(max_length=100)
    updated_at = models.DateTimeField()


class FeedArticle(models.Model):
    title = models.CharField(max_length=255)
    summary = models.TextField()
    link = models.URLField()
    author = models.CharField(max_length=100)
    published_at = models.DateTimeField()
    feed = models.ForeignKey(Feed, on_delete=models.CASCADE, related_name='aricles')
