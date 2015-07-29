import unittest

import sitesafety_app


class SiteTestCase(unittest.TestCase):
    
    def setUp(self):
        sitesafety_app.app.config['TESTING'] = True
        self.app = local_app.app.test_client()
    
    def test_request_index(self):
        with self.app.head('/') as resp:
            self.assertEqual(resp.status_code, 200)
    
    # including rate limit message
    def test_valid_search(self):
        pass
    
    # ' ', no '.'
    def test_invalid_search(self):
        pass
    
    def test_valid_but_strange_search(self):
        pass
    
    def test_no_arguments(self):
        pass


if __name__ == '__main__':
    unittest.main(verbosity=2)
