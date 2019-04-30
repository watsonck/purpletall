from flask import Flask, request, g, redirect, escape, render_template, current_app
import unittest
import requests, json, git, time
from controller import app, get_db

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
#    def test_home(self):
#        with app.test_request_context():
#            self.assertEqual(home(),render_template("/login.html", title = "Login"))

#test if a user is in database
    def test_user_in_db(self):
        db = get_db()
        db.execute("SELECT fname FROM Users WHERE fname = 'Colin' ")
        fname = db.fetchone() 
        db.execute("SELECT lname FROM Users WHERE lname = 'Watson' ")
        lname = db.fetchone()
        db.execute("SELECT email FROM Users WHERE email = 'colin.watson777@yahoo.com'")
        email = db.fetchone()
        db.execute("SELECT lab_user FROM Users WHERE lab_user = 'watsonck'")
        gitname = db.fetchone() 
        self.assertEqual(fname, {'fname': 'Colin'})
        self.assertEqual(lname, {'lname': 'Watson'})
        self.assertEqual(email, {'email': 'colin.watson777@yahoo.com'})
        self.assertEqual(gitname, {'lab_user': 'watsonck'})

    def test_project_in_db(self):
        db = get_db()
        db.execute("SELECT projId FROM Projects WHERE projId = 2")
        projId = db.fetchone()
        db.execute("SELECT name FROM Projects WHERE name = 'Switching Project'")
        name = db.fetchone()
        db.execute("SELECT description FROM Projects WHERE description = 'a project made to test switching'")
        description = db.fetchone()
        self.assertEqual(projId, {'projid': 2})
        self.assertEqual(name, {'name': 'Switching Project'})
        self.assertEqual(description, {'description': 'a project made to test switching'})

    def test_add_and_del(self):
        resp = requests.get("http://purpletall.cs.longwood.edu:5000/1/add?name={unittest1}&desc={This%20is%20a%20unittest}&time={2019-05-1}&bug=true").text
        self.assertNotEqual(json.loads(resp), "ERROR")
        db = get_db()
        db.execute("SELECT id FROM Task WHERE name = 'unittest1' AND description = 'This is a unittest' AND exptCompTime = '2019-05-1' AND bugged = True")
        name = db.fetchone() 
        resp = json.loads(resp)
        taskid = -1
        for key1, stage in resp['stages'].items():
            for task in stage:
                if task['name'] == 'unittest1' and task['is_bug'] == True:
                    taskid = task['id']
        self.assertEqual(taskid, name['id'])
        resp =  requests.get("http://purpletall.cs.longwood.edu:5000/1/remove?id="+str(taskid)).text
        resp = json.loads(resp)
        ids = []
        for key1, stage in resp['stages'].items():
            for task in stage:
                    ids.append(task['id'])
        self.assertNotIn(taskid, ids)

    def test_move(self): 
        resp = requests.get("http://purpletall.cs.longwood.edu:5000/1/move?id=3&stage={start}").text
        self.assertNotEqual(json.loads(resp), "ERROR")
        db = get_db()
        db.execute("SELECT id FROM task WHERE projid = 1 AND stage ILIKE 'start'")
        result = db.fetchone()
        resp = json.loads(resp)
        stageName = ''
        for key1, stage in resp['stages'].items():
            for task in stage:
                if task['name'] == 'unittest1' and task['is_bug'] == True:
                    taskid = task['id']
        self.assertEqual(stageName, taskid)



        
if __name__ == "__main__":
	unittest.main()
