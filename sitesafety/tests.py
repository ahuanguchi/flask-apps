import unittest

import sitesafety_app


class SiteTestCase(unittest.TestCase):
    
    def setUp(self):
        sitesafety_app.app.config['TESTING'] = True
        self.app = sitesafety_app.app.test_client()
    
    def test_request_index(self):
        with self.app.head('/') as resp:
            self.assertEqual(resp.status_code, 200)
    
    def test_valid_search(self):
        with self.app.head('/check?site=nicovideo.jp') as resp:
            self.assertEqual(resp.status_code, 200)
        with self.app.head('/check?site=http://www.nicovideo.jp/') as resp:
            self.assertEqual(resp.status_code, 200)
    
    def test_valid_but_strange_search(self):
        with self.app.head('/check?site=nicovideo.j') as resp:
            self.assertEqual(resp.status_code, 200)
    
    def test_invalid_search(self):
        with self.app.head('/check?site=nico video.') as resp:
            self.assertEqual(resp.status_code, 200)
        with self.app.head('/check?site=nicovideo') as resp:
            self.assertEqual(resp.status_code, 200)
    
    def test_no_arguments(self):
        with self.app.head('/check') as resp:
            self.assertEqual(resp.status_code, 200)
        with self.app.head('/check?site=') as resp:
            self.assertEqual(resp.status_code, 200)


if __name__ == '__main__':
    unittest.main(verbosity=2)
