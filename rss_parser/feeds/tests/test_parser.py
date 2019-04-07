import time
import unittest
from unittest.mock import patch
from datetime import datetime
from rss_parser.feeds import parser, exc


class TimestructToDatetimeTestCase(unittest.TestCase):
    def test_timestruct_to_datetime(self):
        tm_struct = time.strptime('2019-04-04 11:35:44', '%Y-%m-%d %H:%M:%S')
        expected = datetime(2019, 4, 4, 11, 35, 44)
        actual = parser.timestruct_to_datetime(tm_struct)
        self.assertEqual(actual, expected)


class FeedParserValidationTestCase(unittest.TestCase):
    def test_validate_parsed_data_feed_parser(self):
        with self.assertRaises(exc.FeedParserError):
            data = {
                'bozo': 1,
                'bozo_exception': 'Bad beed',
                'feed': {},
                'entries': [],
            }
            parser.validate_parsed_data(data)

    def test_validate_parsed_data_field_not_recognized(self):
        with self.assertRaises(exc.FeedNotRecognizedError):
            data = {
                'bozo': 0,
                'feed': {},
                'entries': [],
            }
            parser.validate_parsed_data(data)

    def test_validate_parsed_field_ok(self):
        data = {
            'bozo': 0,
            'feed': {
                'link': '/',
                'title': 'Test title',
                'publisher': 'Test publisher',
                'updated_parsed': '2019-02-21',
            },
            'entries': [],
        }
        self.assertTrue(parser.validate_parsed_data(data))


class FeedParserTestCase(unittest.TestCase):
    @patch('rss_parser.feeds.parser.validate_parsed_data')
    @patch('rss_parser.feeds.parser.timestruct_to_datetime')
    @patch('rss_parser.feeds.parser.feedparser.parse')
    def test_parse_ok(self, mocked_parse, mocked_td, mocked_validate):
        mocked_td.return_value = '2019-02-21'
        mocked_parse.return_value = {
            'feed': {
                'link': '/',
                'title': 'Test title',
                'publisher': 'Test publisher',
                'updated_parsed': '2019-02-21',
            },
            'entries': [1, 2, 3],
            'bozo': 0,
        }
        expected = {
                'link': '/',
                'title': 'Test title',
                'publisher': 'Test publisher',
                'rss_link': '/feed',
                'updated_at': '2019-02-21',
                'items': [1, 2, 3],
            }
        actual = parser.parse('/feed')
        self.assertEqual(actual, expected)
        self.assertTrue(mocked_parse.called)
        self.assertTrue(mocked_td.called)
        self.assertTrue(mocked_validate.called)

    @patch('rss_parser.feeds.parser.feedparser.parse')
    def test_parse_error(self, mocked_parse):
        mocked_parse.return_value = {
            'feed': {
                'link': '/',
                'title': 'Test title',
                'publisher': 'Test publisher',
                'updated_parsed': '2019-02-21',
            },
            'entries': [1, 2, 3],
            'bozo': 1,
            'bozo_exception': 'Error',
        }

        with self.assertRaises(exc.FeedParserError):
            parser.parse('/feed')
        self.assertTrue(mocked_parse.called)

    @patch('rss_parser.feeds.parser.timestruct_to_datetime')
    def test_normalize_feed_items(self, mocked):
        raw_items = [
            {'title': 'Test 1', 'summary': 'S', 'link': '/1', 'author': 'A', 'published_parsed': '2019-02-23'},
            {'title': 'Test 2', 'summary': 'S', 'link': '/2', 'author': 'A', 'published_parsed': '2019-02-23'},
            {'title': 'Test 3', 'summary': 'S', 'link': '/3', 'author': 'A', 'published_parsed': '2019-02-23'},
        ]
        mocked.return_value = '2019-02-23'
        expected = [
            {'title': 'Test 1', 'summary': 'S', 'link': '/1', 'author': 'A', 'published_at': '2019-02-23'},
            {'title': 'Test 2', 'summary': 'S', 'link': '/2', 'author': 'A', 'published_at': '2019-02-23'},
            {'title': 'Test 3', 'summary': 'S', 'link': '/3', 'author': 'A', 'published_at': '2019-02-23'},
        ]
        actual = parser.normalize_feed_items(raw_items)
        self.assertEqual(actual, expected)
        self.assertTrue(mocked.called)
