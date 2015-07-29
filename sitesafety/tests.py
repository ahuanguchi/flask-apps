import unittest

import sitesafety_app


class SiteTestCase(unittest.TestCase):
    
    def assert_status_code_200(self, url):
        with self.app.head(url) as resp:
            self.assertEqual(resp.status_code, 200)
    
    def setUp(self):
        sitesafety_app.app.config['TESTING'] = True
        self.app = sitesafety_app.app.test_client()
    
    def test_request_index(self):
        self.assert_status_code_200('/')
    
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


if __name__ == '__main__':
    unittest.main(verbosity=2)
