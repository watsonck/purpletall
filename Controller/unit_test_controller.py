import flask
import unittest
import controller

class Test(unittest.TestCase):
    def setUp(self):
        app.config['TESTING'] = True
        app.config['WTF_CSRF_ENABLED'] = False
        app.config['DEBUG'] = False
        self.app = app.test_client()

    def tearDown(self):
        pass

    def test_route(self):

    def test_add(self):

    def test_move(self):
        
if __name__ == "__main__":
    unittest.main()
