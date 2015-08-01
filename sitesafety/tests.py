import os
import unittest
from eventlet import GreenPool
from eventlet.green.urllib import request as eventlet_request
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
        with eventlet_request.urlopen(url) as resp:
            self.assertEqual(resp.getcode(), 200)
        return True
    
    @classmethod
    def setUpClass(cls):
        sitesafety_app.app.config['TESTING'] = True
        sitesafety_app.app.config['PRESERVE_CONTEXT_ON_EXCEPTION'] = False
        cls.root = sitesafety_app.app.root_path
        cls.cache = sitesafety_app.cache
        cls.yql_cache = sitesafety_app.yql_cache
        cls.cache.clear()
        cls.yql_cache.clear()
        cls.pool = GreenPool()
    
    def setUp(self):
        self.app = sitesafety_app.app.test_client()
    
    def tearDown(self):
        self.cache.clear()
        self.yql_cache.clear()
    
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
        self.assert_status_code_200('/check?site=youtube.com')
        self.assert_status_code_200('/check?site=http://www.nicovideo.jp/')
    
    def test_strange_valid_search(self):
        self.assert_status_code_200('/check?site=nicovideo.j')
    
    def test_invalid_search(self):
        self.assert_status_code_200('/check?site=nico video.')
        self.assert_status_code_200('/check?site=nicovideo')
        self.assert_status_code_200('/check?site=n.i')
    
    def test_no_arguments(self):
        self.assert_status_code_200('/check')
        self.assert_status_code_200('/check?site=')
    
    def test_not_found(self):
        page = self.get_and_assert_status_code('/blah', 404)
        self.assertIn('Home', page)
    
    def test_response_cache(self):
        self.assert_status_code_200('/check?site=www.nicovideo.jp')
        self.assert_status_code_200('/check?site=http://www.nicovideo.jp/')
        self.assertEqual(len(os.listdir(os.path.join(self.root, 'cache'))), 1)
    
    def test_yql_cache(self):
        yql_cache_dir = os.path.join(self.root, 'yql_cache')
        self.assert_status_code_200('/check?site=translate.google.com')
        self.assert_status_code_200('/check?site=drive.google.com')
        self.assertEqual(len(os.listdir(yql_cache_dir)), 0)
        self.yql_cache.clear()
        self.assert_status_code_200('/check?site=sitesafety.pythonanywhere.com')
        self.assert_status_code_200('/check?site=caesarcipher.pythonanywhere.com')
        self.assert_status_code_200('/check?site=pythonanywhere.com')
        self.assert_status_code_200('/check?site=www.pythonanywhere.com')
        self.assertEqual(len(os.listdir(yql_cache_dir)), 1)


if __name__ == '__main__':
    unittest.main(verbosity=2)
