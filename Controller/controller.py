from flask import Flask, request, g, redirect, escape, render_template
import psycopg2, psycopg2.extras, time, json, git, smtplib

app = Flask(__name__)

app.config.from_object(__name__)
app.config.update( dict(
	DATABASE="purpletall",
	SECRET_KEY="Lizard Overlords",
	USERNAME="postgres",
	PASSWORD="postgres"
))

def connect_db():
	db = psycopg2.connect(database=app.config["DATABASE"],
	user=app.config["USERNAME"],password=app.config["PASSWORD"],
	host="localhost", cursor_factory=psycopg2.extras.RealDictCursor)
	return db

def get_db():
	if not hasattr(g, "db"):
		g.db = connect_db()
	return g.db.cursor()

@app.teardown_appcontext
def close_db(error):
	if hasattr(g, "db"):
		g.db.close()
	return ''

@app.route("/", methods=["GET", "POST"])
def home():
	#if request.method == "GET":
		#example for other actual functions below,
		#give plain/JSON output here
	#	return "Hello World"
	#else:
		#build web page otherwise, sending what it would need in comma list
	return render_template("/login.html", title = "Login")
		#might need to move file and rename path, jinja looks for templates

#Example url
#http://purpletall.cs.longwood.edu:5000/1/LIST
#Help: https://realpython.com/python-json/
@app.route("/<string:project>/LIST")
def pull_tasks(project):
	json_dict = {}
	json_dict['metadata'] = {}
	json_dict['stages'] = {}
	db = get_db()
	db.execute("SELECT count(projid) AS count FROM stages WHERE projid=%s;"% (project))
	stages = int(db.fetchone()['count'])
	if stages == 0:
		return 'ERROR'

	json_dict['metadata']['project'] = project
	json_dict['metadata']['stagecount'] = stages
	json_dict['metadata']['stages'] = {}
		
	db.execute("SELECT stageorder AS id,stagename AS name FROM stages WHERE projid=%s;"% (project))
	for row in db.fetchall():
		json_dict['metadata']['stages'][row['id']]= row['name']


	db.execute("SELECT id,task.name as name,lab_user,stage,bugged FROM task,projects,users WHERE task.projid = projects.projid AND projects.projid=%s AND contributor=userid;"% (project))
	tasks = db.fetchall()
	for row in tasks:
		json_dict['stages'][row['stage']] = []
	for row in tasks:
		json_dict['stages'][row['stage']].append({
			'id': row['id'],
			'name': row['name'],
			'user': row['lab_user'],
			'is_bug':row['bugged']
		})
	return json.dumps(json_dict)


#Example url
#http://purpletall.cs.longwood.edu:5000/1/add?name={Bug1}&desc={This%20bug%20is%20in%20controller}&time={2019-05-1}&bug={true}
#Help: https://support.clickmeter.com/hc/en-us/articles/211032666-URL-parameters-How-to-pass-it-to-the-destination-URL
@app.route("/<int:project>/add", methods=["GET", "POST"])
def add(project):
	if request.method=="GET":
		name = request.args.get('name','N/A').replace('{','').replace('}','')
		desc = request.args.get('desc','N/A').replace('{','').replace('}','')
		ect = request.args.get('time','N/A').replace('{','').replace('}','')
		bug = request.args.get('bug',False).replace('{','').replace('}','')
		user = request.args.get('user','0')
		start = time.asctime(time.localtime(time.time()))

	db = get_db()
	db.execute("SELECT stagename FROM stages WHERE projid=%d ORDER BY stageorder LIMIT 1;"%(project))
	stage = db.fetchone()['stagename']

	db.execute("INSERT INTO task (name,description,startTime,exptCompTime,stage,projid,bugged,contributor) VALUES ('%s','%s','%s','%s','%s',%d,%s,%s);" % (name,desc,start,ect,stage,project,bug,user))
	g.db.commit()
	return pull_tasks(project)

#Example url
#http://purpletall.cs.longwood.edu:5000/1/move?id=1&stage={complete}
@app.route("/<int:project>/move", methods=["GET", "POST"])
def move(project):
	#if request.method=="GET"
	taskid = request.args.get('id',0)
	stage = request.args.get('stage','N/A').replace('{','').replace('}','')
	user = request.args.get('user','0')

	db = get_db()
	db.execute("SELECT count(*) AS count FROM stages WHERE projid=%d AND stagename ILIKE '%s';"% (project, stage))
	if db.fetchone()['count'] > 0:
		db.execute("UPDATE task SET stage='%s',contributor=%s WHERE id=%s AND projid=%d;" % (stage, user, taskid, project))
		g.db.commit()
	return pull_tasks(project)

#Example url
#http://purpletall.cs.longwood.edu:5000/1/remove?id=1
@app.route("/<int:project>/remove", methods=["GET", "POST"])
def remove(project):
	taskid = request.args.get('id',0)
	db = get_db()
	db.execute("DELETE FROM task WHERE id = '%d' AND projid = '%d'" % (int(taskid),project))
	g.db.commit()
	return pull_tasks(project)

#Example url
#http://purpletall.cs.longwood.edu:5000/1/split?id=1
@app.route("/<int:project>/split", methods=["GET", "POST"]) #post still listed for web
def split(project):
	db = get_db()
	taskid = request.args.get('id',0)
	user = request.args.get('user','0')
	db.execute("SELECT name,description,stage,exptcomptime,actcomptime,lab_user FROM task,users WHERE id = %d AND projid=%d AND userid=contributor;" % (int(taskid),project))
	row = db.fetchone() #should be a single disctionaly/map object list
	name = 'split: ' + row['name']
	desc = row['description']
	stage = row['stage']
	start = time.asctime(time.localtime(time.time()))
	ect = row['exptcomptime']
	act = row['actcomptime']

	if user == None:
		user = 0
	if stage == None:
		stage = 0

	db.execute("INSERT INTO task(projid,name,description,stage,starttime,exptcomptime,actcomptime,contributor) VALUES (%d,'%s','%s','%s','%s','%s','%s',%s)" % (project,name,desc,str(stage),start,ect,act,user))
	g.db.commit()
	#might need to fix to explitly grab each thing in the row list
	return pull_tasks(project)

#Example url
#http://purpletall.cs.longwood.edu:5000/1/modify?id=4&name={Bug1}&desc={This%20bug%20is%20in%20controller}&time={2019-05-1}&bug={true}
@app.route("/<int:project>/modify", methods=["GET", "POST"])
def modify(project):
	#need to expand this to include what sort of modification
	return pull_tasks(project)

#Example url
#http://purpletall.cs.longwood.edu:5000/1/info?id=1
@app.route("/<int:project>/info", methods=["GET", "POST"])
def info(project):
	taskid = request.args.get('id',0)
	if taskid == 0:
		return 'ERROR'
	db = get_db()
	db.execute("SELECT * FROM task WHERE id = %s and projid=%d" % (taskid,project))
	row = db.fetchone()
	json_dict = {}
	for key in row:
		json_dict[key] = row[key]
	return json.dumps(json_dict)

#Example url
#http://purpletall.cs.longwood.edu:5000/1/delcol?name={TEST}
@app.route("/<string:project>/delcol", methods = ["GET","POST"])
def delcol(project):
	stagename = request.args.get('name','').replace('{','').replace('}','')
	db = get_db()
	try:
		db.execute("DELETE FROM stages CASCADE WHERE projid=%s AND stagename='%s';" % (project,stagename))
		g.db.commit()
		return pull_tasks(project)
	except:
		return 'Error'

@app.route("/<int:project>/rename", methods = ["GET","POST"])
def rename(project):
	return pull_tasks(project)

#Example url
#http://purpletall.cs.longwood.edu:5000/ping?user={haddockcl}
@app.route("/ping", methods=["GET", "POST"])
def ping():
	sender = request.args.get('sender',0)
	receiver = request.args.get('receiver',0)
	#SEND EMAIL
	return ''

#Example url
#http://purpletall.cs.longwood.edu:5000/login?user={haddockcl}
@app.route("/login", methods=["GET", "POST"])
def login():
	db = get_db()
	user = "";
	if request.method=="GET":
		user = request.args.get('user','').replace('{','').replace('}','')
	elif "username" in request.form:
		user = escape(request.form['username'])
	db.execute("SELECT userid FROM users WHERE lab_user = '%s';" % (user))
	row = db.fetchone()

	if request.method=="GET":
	    if row:
	        return str(row['userid'])
	    else:
	        return '0'

	isUser = row is not None

	return render_template("/logincheck.html", title = "Purple Tall", loginUser=isUser)


#Example url
#http://purpletall.cs.longwood.edu:5000/1/addcol?name={TEST}
@app.route("/<string:project>/addcol", methods=["GET","POST"])
def addcol(project):
	db = get_db()
	db.execute("SELECT MAX(stageorder)+1 AS order FROM stages WHERE projid=%s;" % (project))

	stagename = request.args.get('name','').replace('{','').replace('}','')
	row = db.fetchone()
	stageorder = 0
	if row is not None:
		stageorder = row['order']

	try:
		db.execute("INSERT INTO stages(projid,stagename,stageorder) VALUES (%s,'%s',%s);" % (project,stagename,str(stageorder)))
		g.db.commit()
		return pull_tasks(project)
	except:
		return 'Error'

#Example url
#http://purpletall.cs.longwood.edu:5000/projlist
@app.route("/projlist", methods=["GET","POST"])
def projlist():
	try:
		data = {}
		data['projects'] = []
		db = get_db()
		db.execute("SELECT count(*) AS count FROM projects;")
		data['count'] = int(db.fetchone()['count'])
		db.execute("SELECT * FROM projects;");
		rows = db.fetchall()
		for row in rows:
			data['projects'].append({
				'projid': row['projid'],
				'name': row['name'],
				'description': row['description']
			})
		return json.dumps(data) 
	except:
		return 'Error'


if __name__ == "__main__":
	app.run(host='0.0.0.0')
