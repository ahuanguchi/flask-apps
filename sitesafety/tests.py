import os
import unittest
from eventlet import GreenPool
from eventlet.green.urllib.request import urlopen
from lxml import html

import sitesafety_app


class SiteTestCase(unittest.TestCase):
    
    def assert_status_code_200(self, url):
        with self.app.head(url) as resp:
            self.assertEqual(resp.status_code, 200, url)
    
    def get_and_assert_status_code(self, url, code):
        with self.app.get(url) as resp:
            self.assertEqual(resp.status_code, code, url)
            data = resp.get_data(as_text=True)
        return data
    
    def external_assert_status_code_200(self, url):
        with urlopen(url) as resp:
            self.assertEqual(resp.getcode(), 200)
        return True
    
    @classmethod
    def setUpClass(cls):
        sitesafety_app.app.config['TESTING'] = True
        sitesafety_app.app.config['PRESERVE_CONTEXT_ON_EXCEPTION'] = False
        cls.root = sitesafety_app.app.root_path
        cls.cache = sitesafety_app.cache
        cls.cache.clear()
        cls.pool = GreenPool()
    
    def setUp(self):
        self.app = sitesafety_app.app.test_client()
    
    def tearDown(self):
        self.cache.clear()
    
    def test_request_index(self):
        page = self.get_and_assert_status_code('/', 200)
        tree = html.fromstring(page)
        external_links = []
        for result in tree.iterlinks():
            link = result[2]
            if not link.startswith('http'):
                self.assert_status_code_200(link)
            else:
                external_links.append(link)
        feedback = self.pool.imap(self.external_assert_status_code_200, external_links)
        self.assertGreater(len([x for x in feedback]), 0)
    
    def test_valid_search(self):
        urls = ('/check?site=youtube.com', '/check?site=http://www.nicovideo.jp/',
                '/check?site=nicovideo.j', '/check?site= python.org ')
        for url in urls:
            page = self.get_and_assert_status_code(url, 200)
            self.assertIn('Results for', page)
    
    def test_invalid_search(self):
        urls = ('/check?site=nico vi.deo', '/check?site=nicovideo',
                '/check?site=n.i', '/check?site=.nicovideo.',
                '/check', '/check?site=', r'/check?site=nicovdieo.jp\user')
        for url in urls:
            page = self.get_and_assert_status_code(url, 200)
            self.assertIn('class="warning"', page)
    
    def test_not_found(self):
        page = self.get_and_assert_status_code('/blah', 404)
        self.assertIn('Home', page)
    
    def test_response_cache(self):
        self.assert_status_code_200('/check?site=www.nicovideo.jp')
        self.assert_status_code_200('/check?site=http://www.nicovideo.jp/')
        self.assertEqual(len(os.listdir(os.path.join(self.root, '_cache'))), 1)
    
    def test_cache_without_path(self):
        self.assert_status_code_200('/check?site=http://www.nicovideo.jp/user/16253346')
        page = self.get_and_assert_status_code('/check?site=www.nicovideo.jp', 200)
        self.assertNotIn('nicovideo.jp/user</a>', page)


if __name__ == '__main__':
    unittest.main(verbosity=2)
