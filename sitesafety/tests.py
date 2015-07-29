import requests
import unittest
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
    
    def setUp(self):
        sitesafety_app.app.config['TESTING'] = True
        self.app = sitesafety_app.app.test_client()
    
    def test_request_index(self):
        page = self.get_and_assert_status_code('/', 200)
        tree = html.fromstring(page)
        for result in tree.iterlinks():
            link = result[2]
            if not link.startswith('http'):
                self.assert_status_code_200(link)
            else:
                r = requests.head(link, headers={'Connection': 'close'})
                self.assertEqual(r.status_code, 200, link)
    
    def test_valid_search(self):
        self.assert_status_code_200('/check?site=nicovideo.jp')
        self.assert_status_code_200('/check?site=http://www.nicovideo.jp/')
    
    def test_valid_but_strange_search(self):
        self.assert_status_code_200('/check?site=nicovideo.j')
    
    def test_invalid_search(self):
        self.assert_status_code_200('/check?site=nico video.')
        self.assert_status_code_200('/check?site=nicovideo')
    
    def test_no_arguments(self):
        self.assert_status_code_200('/check')
        self.assert_status_code_200('/check?site=')
    
    def test_not_found(self):
        page = self.get_and_assert_status_code('/blah', 404)
        self.assertIn('Home', page)


if __name__ == '__main__':
    unittest.main(verbosity=2)
