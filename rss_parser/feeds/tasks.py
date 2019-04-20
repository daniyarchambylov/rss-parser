from celery import shared_task
from celery.exceptions import MaxRetriesExceededError
from django_celery_beat.models import PeriodicTask
from django.conf import settings
from .models import Feed, FeedArticle
from .parser import parse, normalize_feed_items


@shared_task(
    bind=True,
    default_retry_delay=settings.FETCH_FEEDS_RETRY_INTERVAL,
    max_retries=settings.FETCH_FEEDS_MAX_RETRIES)
def update_feed(self, url):
    task = PeriodicTask.objects.get(name=url)
    if not task.enabled:
        return None
    try:
        data = parse(url)
        items = normalize_feed_items(data['items'])
        feed = Feed.create_from_feedparser(data)
        [FeedArticle.create_from_feedparser(feed, item) for item in items]
        return feed
    except Exception:
        pass

    try:
        self.retry()
    except MaxRetriesExceededError:
        task.enabled = False
        task.save()
