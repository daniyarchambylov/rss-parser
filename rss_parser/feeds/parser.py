from datetime import datetime
from calendar import timegm
import feedparser

from . import exc


def timestruct_to_datetime(timestruct):
    return datetime.fromtimestamp(timegm(timestruct))


def validate_parsed_data(data):
    if (data['bozo'] != 0):
        raise exc.FeedParserError(data['bozo_exception'])

    required_fields = ['title', 'link', 'updated_parsed']

    for field in required_fields:
        try:
            data['feed'][field]
        except KeyError as e:
            raise exc.FeedNotRecognizedError(str(e))

    return True


def parse(url):
    feed_parsed = feedparser.parse(url)

    validate_parsed_data(feed_parsed)

    feed = feed_parsed['feed']
    items = feed_parsed['entries']
    return {
        'title': feed['title'],
        'link': feed['link'],
        'publisher': feed.get('publisher', '1'),
        'rss_link': url,
        'updated_at': timestruct_to_datetime(feed['updated_parsed']),
        'items': items,
    }


def normalize_feed_items(raw_items):
    return [{
        'title': i['title'],
        'summary': i['summary'],
        'link': i['link'],
        'author': i['author'],
        'published_at': timestruct_to_datetime(i['published_parsed']),
    } for i in raw_items]
