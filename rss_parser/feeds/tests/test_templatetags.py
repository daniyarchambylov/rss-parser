from django.test import TestCase
from rss_parser.feeds.templatetags import feeds


class FeedsTemplateTagsTestCase(TestCase):
    def test_markdown(self):
        source = "**Test String**\n"
        html = feeds.markdown(source)
        self.assertEquals(html, '<p><strong>Test String</strong></p>')
