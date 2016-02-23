import unittest
from protector.tests.fixtures.loader import load_fixture
from protector.urlhandler.urlhandler import UrlHandler


class TestUrlHandler(unittest.TestCase):
    def test_url_handling(self):
        """
        Test URL parameter handling
        """
        self.assertIsNone(UrlHandler.get_query(""))
        self.assertIsNone(UrlHandler.get_query("http://www.example.com"))
        self.assertIsNone(UrlHandler.get_query("http://www.example.com/"))
        self.assertIsNone(UrlHandler.get_query("http://www.example.com/bla=1"))
        self.assertIsNone(UrlHandler.get_query("http://www.example.com?bla=1"))
        self.assertEqual(UrlHandler.get_query("http://www.example.com?q=1"), '1')
        self.assertIsNone(UrlHandler.get_query("http://example.com/over/there?name=ferret"))
        self.assertEqual(UrlHandler.get_query("http://example.com/over/there?q=ferret"), 'ferret')
        self.assertIsNone(UrlHandler.get_query("http://www.example.com/dff&q=1"))
        self.assertEqual(UrlHandler.get_query("http://www.example.com/?q=1"), '1')

    def test_query_extraction(self):
        """
        Test extraction of query from URL
        """
        urls = load_fixture("sample_urls.txt")
        queries = load_fixture("sample_queries.txt")

        for url, query in zip(urls, queries):
            url = url.strip()
            query = query.strip()
            if not query:
                query = None
            self.assertEqual(UrlHandler.get_query(url), query)
