import flask
import unittest
from controller import app

class Test(unittest.TestCase):

    TEST_DB = 'test.db'

    def setUp(self):
        app.config['TESTING'] = True
        app.config['WTF_CSRF_ENABLED'] = False
        app.config['DEBUG'] = False
        #app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + \ os.path.join(app.config['BASEDIR'], TEST_DB)
        self.app = app.test_client()
        ##db.drop_all()
        ##db.create_all()

    def tearDown(self):
        pass

    def test_main_page(self):
        response = self.app.get('/', follow_redirects=True)
        self.assertEqual(response.status_code, 200)
    


    #def test_add(self, task):

    #def test_move(self):
        #return self.app.post(
            #'/move',

    #def test_remove():
        
        

if __name__ == "__main__":
    unittest.main()
