from flask import Flask, request, g, redirect, escape, render_template, current_app
import unittest
import requests, json, git, time
import controller
from controller import app, get_db, connect_db, home, pull_tasks, add, move, remove, split, info, delcol, login, addcol, projlist
import psycopg2
import psycopg2.extras

app_context = app.app_context()
app_context.push()

current_app.name

class Test(unittest.TestCase):

    with app.app_context():
        print(current_app.name)



    def setUp(self):
        app.config['TESTING'] = True
        app.config['WTF_CSRF_ENABLED'] = False
        app.config['DEBUG'] = False
        self.app = app.test_client()

    def tearDown(self):
        pass

#compare the connection's status code to 200, which is "ok"
    def test_connection(self):
        response = self.app.get('/', follow_redirects=True)
        self.assertEqual(response.status_code, 200)

#test if homepage is displaying correctly
    def test_home(self):
        with app.test_request_context():
            self.assertEqual(home(),render_template("/login.html", title = "Login"))

#test if a user is in database
    def test_user_in_db(self):
        db = get_db()
        db.execute("SELECT fname FROM Users WHERE fname = 'Colin' ")
        fname = db.fetchone() 
        db.execute("SELECT lname FROM Users WHERE lname = 'Watson' ")
        lname = db.fetchone()
        db.execute("SELECT email FROM Users WHERE email = 'colin.watson777@yahoo.com'")
        email = db.fetchone()
        db.execute("SELECT gitname FROM Users WHERE gitname = 'watsonck'")
        gitname = db.fetchone() 
        self.assertEqual(fname, [{'fname': 'Colin'}])
        self.assertEqual(lname, [{'lname': 'Watson'}])
        self.assertEqual(email, [{'email': 'colin.watson777@yahoo.com'}])
        self.assertEqual(gitname, [{'gitname': 'watsonck'}])

    def test_project_in_db(self):
        db = get_db()
        db.execute("SELECT projId FROM Projects WHERE projId = 1")
        projId = db.fetchone()
        db.execute("SELECT name FROM Projects WHERE name = 'Testing Project'")
        name = db.fetchone()
        db.execute("SELECT description FROM Projects WHERE description = 'a project made to test program'")
        description = db.fetchone()
        self.assertEqual(projId, [{'projid': 1}])
        self.assertEqual(name, [{'name': 'Testing Project'}])
        self.assertEqual(description, [{'description': 'a project made to test program'}])
    
    #def test_new_task(task):
        #response = self.app.post('/TASK/<string:task>', data=dict()

    def test_add(self, project):
        @app.route("http://purpletall.cs.longwood.edu:5000/1/add?name={unittest1}&desc={This%20is%20a%20unittest}&time={2019-05-1}&bug={true}")
        add(1)
        db = get_db()
        db.execute("SELECT name FROM Tasks WHERE name = 'unittest1' ")
        name = db.fetchone() 
        #db.execute("SELECT lname FROM Users WHERE lname = 'Watson' ")
        #lname = db.fetchone()
        #db.execute("SELECT email FROM Users WHERE email = 'colin.watson777@yahoo.com'")
        #email = db.fetchone()
        #db.execute("SELECT gitname FROM Users WHERE gitname = 'watsonck'")
        #gitname = db.fetchone() 
        self.assertEqual(fnname, [{'name': 'unittest1'}])
        #self.assertEqual(lname, [{'lname': 'Watson'}])
        #self.assertEqual(email, [{'email': 'colin.watson777@yahoo.com'}])
        #self.assertEqual(gitname, [{'gitname': 'watsonck'}])


    #def test_move(self):
        #return self.app.post(
            #'/move',

    #def test_remove():
        
        

if __name__ == "__main__":
    unittest.main()
