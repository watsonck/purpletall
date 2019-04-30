from flask import Flask, request, g, redirect, escape, render_template
from git import Git
import psycopg2, psycopg2.extras, time, requests, json, smtplib, re

#TODO *maybe* IMPLEMENT CONFIG FILE LOADING

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
	db.autocommit = True
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

def pick_source(which):
	if which=="POST":
		return request.form
	return request.args

@app.route("/", methods=["GET", "POST"])
def home():
	#if request.method == "GET":
		#example for other actual functions below,
		#give plain/JSON output here
#	   return "Hello World"
	#else:
		#build web page otherwise, sending what it would need in comma list
	return render_template("/login.html", title = "Login",loginUser = 0)
		#might need to move file and rename path, jinja looks for templates

@app.route("/addingauser", methods=["POST"])
def web_add_user():
	return render_template("/addUser.html")

#Example url
#http://purpletall.cs.longwood.edu:5000/1/LIST
#Help: https://realpython.com/python-json/
@app.route("/<string:project>/list", methods=["GET","POST"])
def pull_tasks(project):
	try:
		gitpull()
	except:
		pass
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
			
	db.execute("SELECT stageorder AS id,stagename AS name FROM stages WHERE projid=%s ORDER BY stageorder;"% (project))
	rows = db.fetchall();
	temp = []
	if rows is None:
		return ''
	for row in rows:
		temp.append(row['name']);
	for i in range(0,len(temp)):
		json_dict['metadata']['stages'][i] = temp[i]
	

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
	close_db('')
	if request.method=="POST":
		current = request.form.get("userid","0");
		return render_template("/home.html", title = "Project Kanban", data = json_dict, tasklist=tasks, userid=current)
	return json.dumps(json_dict)

#Example url
#http://purpletall.cs.longwood.edu:5000/1/add?name={Bug1}&desc={This%20bug%20is%20in%20controller}&time={2019-05-1}&bug={true}
#Help: https://support.clickmeter.com/hc/en-us/articles/211032666-URL-parameters-How-to-pass-it-to-the-destination-URL
@app.route("/<int:project>/add", methods=["GET", "POST"])
def add(project):
	source = pick_source(request.method)
	name = source.get('name','N/A').replace('{','').replace('}','')
	desc = source.get('desc','N/A').replace('{','').replace('}','')
	ect = source.get('time','1-1-2019').replace('{','').replace('}','')
	bug = source.get('bug',False)
	user = source.get('user','0')
	start = time.asctime(time.localtime(time.time()))

	db = get_db()
	db.execute("SELECT stagename FROM stages WHERE projid=%d ORDER BY stageorder LIMIT 1;" % (project))
	row = db.fetchone()
	if row is None:
		return 'Error'
	stage = row['stagename']

	db.execute("INSERT INTO task (name,description,startTime,exptCompTime,stage,projid,bugged,contributor) VALUES ('%s','%s','%s','%s','%s',%d,%s,%s);" % (name,desc,start,ect,stage,project,bug,user))
	g.db.commit()

	db.execute("SELECT MAX(id) AS taskid FROM task;")
	row = db.fetchone()
	if row is not None:
		updateLog(user,row['taskid'],project,'Add',False,'Created in stage: ' + stage)

	return pull_tasks(project)

#Example url
#http://purpletall.cs.longwood.edu:5000/1/move?id=1&stage={complete}
@app.route("/<string:project>/move", methods=["GET", "POST"])
def move(project):
	#TODO *maybe* ADD/REMOVE COLUMNS AS NEEDED
	source = pick_source(request.method)
	taskid = source.get('id',0)
	stage = source.get('stage','N/A').replace('{','').replace('}','')
	user = source.get('user','0')

	db = get_db()
	db.execute("SELECT count(*) AS count FROM stages WHERE projid=%s AND stagename ILIKE '%s'"% (project, stage))
	if db.fetchone()['count'] > 0:
		db.execute("UPDATE task SET stage='%s',contributor=%s WHERE id=%s AND projid=%s" % (stage, user, taskid, project))
		g.db.commit()

	updateLog(user,taskid,project,'Move',False,'Moved to stage: ' + str(stage))
	return pull_tasks(project)

#Example url
#http://purpletall.cs.longwood.edu:5000/1/remove?id=1
@app.route("/<int:project>/remove", methods=["GET", "POST"])
def remove(project):
	source = pick_source(request.method)
	taskid = source.get('id','-1')
	db = get_db()
	try:
		db.execute("DELETE FROM logs WHERE taskid = %s AND projid = %s" % (taskid, project))
		g.db.commit()
		db.execute("DELETE FROM task WHERE id = %s AND projid = %s" % (taskid,project))
		g.db.commit()
	except:
		pass
	return pull_tasks(project)

#Example url
#http://purpletall.cs.longwood.edu:5000/1/split?id=1
@app.route("/<int:project>/split", methods=["GET", "POST"])
def split(project):
	db = get_db()
	source = pick_source(request.method)
	taskid = source.get('id',0)
	user = source.get('user','0')
	db.execute("SELECT name,description,stage,exptcomptime,actcomptime,lab_user FROM task,users WHERE id = %d AND projid=%d AND userid=contributor;" % (int(taskid),project))
	row = db.fetchone() #should be a single disctionaly/map object list
	if row is not None:
		return pull_tasks(project)
	name = row['name'] + '.s'
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

	db.execute("SELECT MAX(id) AS taskid FROM task;")
	row = db.fetchone()
	if row is not None:
		updateLog(user,row['taskid'],project,'Split',False,'Split from: ' + taskid)

	return pull_tasks(project)

#Example url
#http://purpletall.cs.longwood.edu:5000/1/modify?id=4&name={Bug1}&desc={This%20bug%20is%20in%20controller}&time={2019-05-1}&bug={true}
@app.route("/<int:project>/modify", methods=["GET", "POST"])
def modify(project):
	#TODO *maybe* IMPLEMENT MODIFY
	return pull_tasks(project)

#Example url
#http://purpletall.cs.longwood.edu:5000/1/info?id=1
@app.route("/<int:project>/info", methods=["GET", "POST"])
def info(project):
	source = pick_source(request.method)
	taskid = source.get('id',0)
	if taskid == 0:
		return 'ERROR'
	db = get_db()
	db.execute("SELECT name,id as task_id,projid as project_id,description,stage,starttime as start_time,exptcomptime,actcomptime,contributor as recent_contributor,bugged AS is_bugged FROM task WHERE id = %s and projid=%d" % (taskid,project))
	row = db.fetchone()
	if row is None:
		return 'Error'
	json_dict = {}
	for key in row:
		json_dict[key] = str(row[key])
	if request.method=="POST":
		current = source.get("curUser","michael messed up");
		return render_template("info.html", dump=json_dict)
	return json.dumps(json_dict)

#Example url
#http://purpletall.cs.longwood.edu:5000/1/delcol?name={TEST}
@app.route("/<string:project>/delcol", methods = ["GET","POST"])
def delcol(project):
	source = pick_source(request.method)
	stagename = source.get('name','').replace('{','').replace('}','')
	db = get_db()
	db.execute("DELETE FROM task WHERE projid=%s AND stage ILIKE '%s';" % (project,stagename))
	g.db.commit()
	db.execute("DELETE FROM stages WHERE projid=%s AND stagename ILIKE '%s';" % (project,stagename))
	g.db.commit()
	return pull_tasks(project)

#Example url
#http://purpletall.cs.longwood.edu:5000/2/rename?id=5&name={TESTING}
@app.route("/<string:project>/rename", methods = ["GET","POST"])
def rename(project):
	source = pick_source(request.method)
	taskid = source.get('id','0')
	name = source.get('name','').replace('{','').replace('}','')
	
	db = get_db()
	db.execute("UPDATE task SET name = '%s' WHERE id = %s AND projid=%s" % (name,str(taskid),str(project)))
	g.db.commit()
	return pull_tasks(project)


def updateLog(userID,taskID,projID,action,isGit,comments):
	logtime = time.asctime(time.localtime(time.time()))
	db = get_db()
	db.execute("SELECT count(*) AS count FROM task WHERE id=%s AND projid=%s" % (taskID,projID))
	row = db.fetchone()
	if row is None:
		return
	if row['count'] == 0:
		return
	db.execute("INSERT INTO logs(taskid,projid,contributor,action,time,git,comments) VALUES (%s,%s,%s,'%s','%s',%s,'%s');" % (str(taskID),str(projID),str(userID),str(action),str(logtime),str(isGit),str(comments)))
	

#http://purpletall.cs.longwood.edu/log/1/2
@app.route("/log/<string:project>/<string:taskid>",methods = ["GET","POST"])
def pullLog(taskid,project):
	db = get_db()

	db.execute("SELECT lab_user AS contributor, TO_CHAR(time, 'dd-MM-yyyy HH24:MI:SS') AS time,comments FROM logs JOIN users ON users.userid=logs.contributor WHERE taskid=%s AND projid=%s ORDER BY time DESC" % (str(taskid),str(project)))
	log = db.fetchall()
	return json.dumps(log)

#Pull all git log since last update and make a new update
@app.route("/git", methods=["GET","POST"])
def gitpull():
	g = Git('/home/purpletall/purpletall')
	datetime = '0-0-0 00:00:00'
	db = get_db()
	db.execute("SELECT time FROM logs WHERE git=true ORDER BY time DESC LIMIT 1")
	row = db.fetchone()
	if row is not None:
		datetime = str(row['time'])
	loginfo = g.log('--since=' + datetime,"--format=format:{\"contributor\":\"%an\",\"message\":\"%B\",\"timestamp\":%ct},")
	loginfo = loginfo.replace('\n','').replace('},{','},\n{').rstrip(',')
	loginfo = '[' + loginfo + ']'
	
	temp_list = json.loads(loginfo)
	data = sorted(temp_list, key=lambda k: k['timestamp']) 
	data[:] = [item for item in data if re.search("<[^<>]+>",item['message'])]

	for item in data:
		item['flags'] = list(re.findall("<[^<>]+>",item['message']))
		item['timestamp'] = str(time.strftime("%Y-%m-%d %H:%M:%S", time.gmtime(int(item['timestamp']))))
		del item['message']

		user = 0
		db.execute("SELECT userid FROM users WHERE lab_user='%s'" % (item['contributor']))
		result = db.fetchone()
		if result is not None:
			user = result['userid']
		item['contributor'] = user
		for flag in item['flags']:
			flag = flag.replace('<','').replace('>','')
			command = flag[:4].upper()
			print(command)
			print(flag)
			if command == 'ADD ':
				args = flag.split(' ',5)
				if len(args) is not 6:
					continue;
				proj = args[1]
				name = args[2]
				dttm = args[3]
				bugs = args[4]
				desc = args[5]
				strt = time.asctime(time.localtime(time.time()))

				db.execute("SELECT stagename FROM stages WHERE projid=%s ORDER BY stageorder LIMIT 1;" % (str(proj)))
				row = db.fetchone()
				if row is None:
					continue
				stage = row['stagename']
				db.execute("INSERT INTO task (name,description,startTime,exptCompTime,stage,projid,bugged,contributor) VALUES ('%s','%s','%s','%s','%s','%s',%s,0);" % (name,desc,strt,dttm,stage,proj,bugs))
				db.execute("SELECT MAX(id) AS taskid FROM task;")
				row = db.fetchone()
				if row is not None:
					updateLog(0,row['taskid'],proj,'Add',True,'Created in stage: ' + stage)
			elif command == 'MOVE':
				args = flag.split(' ',4)
				if len(args) is not 4:
					continue
				proj = args[1]
				task = args[2]
				clmn = args[3]
				db.execute("SELECT count(*) AS count FROM stages WHERE projid=%s AND stagename ILIKE '%s'"% (proj, clmn))
				count = db.fetchone()['count']
				if count > 0:
					db.execute("UPDATE task SET stage='%s',contributor=0 WHERE id=%s AND projid=%s" % (clmn, task, proj))
				updateLog(0,task,proj,'Move',True,'Moved to stage: ' + str(clmn))
			elif command == 'REMV':
				args = flag.split(' ',2)
				if len(args) is not 3:
					continue
				proj = args[1]
				task = args[2]
				db.execute("DELETE FROM logs WHERE taskid = %s AND projid = %s;" % (task, proj))
				db.execute("DELETE FROM task WHERE id = %s AND projid = %s;" % (task,proj))

				t = time.asctime(time.localtime(time.time()))
				db.execute("SELECT time FROM logs WHERE taskid=-1 AND projid=-1 AND comments='DELETED'")
				row = db.fetchone()
				if row is None:
					db.execute("INSERT INTO logs(taskid,projid,contributor,time,git,comments) VALUES (-1,-1,0,'%s',true,'DELETED')" % t)
				else:
					db.execute("UPDATE logs SET time='%s' WHERE comments='PINGED'" % t)
			elif command == 'PING':
				args = flag.split(' ',2)
				if len(args) is not 3:
					print(args)
					continue
				user = args[1]
				message = args[2]
				t = time.asctime(time.localtime(time.time()))
				url = 'http://purpletall.cs.longwood.edu:5000/ping?user=0&rcvr={' + user + '}&msg={' + message + '}'
				print(requests.get(url))
				db.execute("SELECT time FROM logs WHERE taskid=-1 AND projid=-1 AND comments='PINGED'")
				row = db.fetchone()
				if row is None:
					db.execute("INSERT INTO logs(taskid,projid,contributor,time,git,comments) VALUES (-1,-1,0,'%s',true,'PINGED')" % t)
				else:
					db.execute("UPDATE logs SET time='%s' WHERE comments='PINGED'" % t)
			else:
				continue
	return ''

#Example url
#http://purpletall.cs.longwood.edu:5000/ping?user=2&rcvr={haddockcl}&msg={This%20is%20a%20ping}
@app.route("/ping", methods=["GET", "POST"])
def ping():
	source = pick_source(request.method)
	user = source.get('user','0')
	rcvr = source.get('rcvr',None)
	if rcvr is None:
		return 'Error'
	else:
		rcvr = rcvr.replace('{','').replace('}','')

	db = get_db()
	db.execute("SELECT fname,lname,email FROM users WHERE lab_user='%s'" % (rcvr))
	result1 = db.fetchone();
	if result1 is None:
		return 'Error'
	rcvr = result1['email']
	getter = result1['fname'] + ' ' + result1['lname']

	pinger = ''
	if user == '0':
		pinger = 'an unknown user'
	else:
		db.execute("SELECT fname,lname FROM users WHERE userid=%s" % (str(user)))
		result2 = db.fetchone();
		if result2 is None:
			return 'Error'
		pinger = result2['fname'] + ' ' + result2['lname']

	msg = source.get('msg','').replace('{','').replace('}','')
	unk = ''
	if msg == '':
		unk = 'n empty'
	else:
		msg = ' It said:\n' + msg

	message = """From Purple Tall <purpletall@outlook.com>
To: {0} <{1}> 
Subject: You have been pinged!

You just got a{2} ping from {3}.{4}
""".format(getter,rcvr,unk,pinger,msg)
	
	rcvr = [rcvr]
	server = smtplib.SMTP('smtp.office365.com', 587)
	server.connect('smtp.office365.com', 587)
	server.ehlo()
	server.starttls()
	server.ehlo()
	server.login("purpletall@outlook.com", "ProjectManager8")

	try:
		server.sendmail('purpletall@outlook.com', rcvr, message)
	except:
		return 'Error'
	server.quit()
	print(rcvr,message)
	return ''


#Example url
#http://purpletall.cs.longwood.edu:5000/login?user={haddockcl}
@app.route("/login", methods=["GET", "POST"])
def login():
	db = get_db()
	source = pick_source(request.method)
	user = source.get('user','').replace('{','').replace('}','')
	db.execute("SELECT userid FROM users WHERE lab_user = '%s';" % (user))
	row = db.fetchone()
	userid = 0
	if row is not None:
	    userid = row['userid']
	if request.method=="GET":
		return str(userid)
	if userid == 0: #if wasn't found AND source is web/post
		return render_template("/login.html", title = "Purple Tall", loginUser = -1)
	return render_template("/valid.html", iduser = userid, username= user)	
	#return projlist()

#Example url
#http://purpletall.cs.longwood.edu:5000/1/addcol?name={TEST}
@app.route("/<string:project>/addcol", methods=["GET","POST"])
def addcol(project):
	db = get_db()
	db.execute("SELECT COALESCE(MAX(stageorder),0)+1 AS order FROM stages WHERE projid=%s;" % (project))

	source = pick_source(request.method)
	stagename = source.get('name','').replace('{','').replace('}','').upper()
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
#http://purpletall.cs.longwood.edu:5000/newproj?name={Project%20Manager}&desc={This%20is%20a%20project%20management%20system}
@app.route("/newproj",methods=["GET","POST"])
def addproj():
	db = get_db()
	source = pick_source(request.method)
	name = source.get('name','').replace('{','').replace('}','')
	desc = source.get('desc','').replace('{','').replace('}','')
	db.execute("INSERT INTO projects(name,description) VALUES ('%s','%s')" % (name,desc))
	g.db.commit()
	db.execute("SELECT Max(projid) AS max FROM projects")
	projid = db.fetchone()['max']

	db.execute("INSERT INTO stages(projid,stagename,stageorder) VALUES (%s,'TODO',0)" % projid)
	g.db.commit()
	db.execute("INSERT INTO stages(projid,stagename,stageorder) VALUES (%s,'DOING',1)" % projid)
	g.db.commit()
	db.execute("INSERT INTO stages(projid,stagename,stageorder) VALUES (%s,'DONE',2)" % projid)
	g.db.commit()
	return projlist()

#Example url
#http://purpletall.cs.longwood.edu:5000/delproj?id=3
@app.route("/delproj",methods=["GET","POST"])
def delproj():
	source = pick_source(request.method)
	projid = source.get('id',0)
	if projid is 0:
		return projlist()
	try:
		db = get_db()
		db.execute("DELETE FROM projects WHERE projid=%s" % (projid))
		g.db.commit()
	except:	
		return projlist()
	return projlist()

#Example url
#http://purpletall.cs.longwood.edu:5000/user?fname={Cameron}&lname={Haddock}&uname={haddockcl}&email={cameron.haddock%40live.longwood.edu}
@app.route("/user",methods=["GET","POST"])
def adduser():
	db = get_db()
	source = pick_source(request.method)
	fname = source.get('fname','').replace('{','').replace('}','')
	lname = source.get('lname','').replace('{','').replace('}','')
	user = source.get('uname','').replace('{','').replace('}','')
	email = source.get('email','').replace('{','').replace('}','').replace('%40','@')

	db.execute("SELECT count(lab_user) AS count FROM users WHERE lab_user='%s'" % (user))
	if db.fetchone()['count'] != 0:
		return 'Error'

	db.execute("INSERT INTO users(fname,lname,lab_user,email) VALUES ('%s','%s','%s','%s');" % (fname,lname,user,email))
	g.db.commit()
	db.execute("SELECT MAX(userid) AS userid FROM users;")
	row = db.fetchone()
	if row is None:
		return 'Error'
	userid = row['userid']
	if request.method=="POST":
		return home()
	return str(userid)


def username():
	#TODO change username
	return ''	

#Example url
#http://purpletall.cs.longwood.edu:5000/1/swap?stage1={todo}&stage2={Done}
@app.route("/<string:project>/swap", methods=["GET","POST"])
def swpcol(project):
	source = pick_source(request.method)
	stage1 = source.get('stage1','').replace('{','').replace('}','')
	stage2 = source.get('stage2','').replace('{','').replace('}','')
	
	db = get_db()
	db.execute("SELECT stageorder FROM stages WHERE projid=%s AND stagename ILIKE '%s'" % (project,stage1))
	row=db.fetchone()
	if row is None:
		return 'Error'
	order1 = row['stageorder']

	db.execute("SELECT stageorder FROM stages WHERE projid=%s AND stagename ILIKE '%s'" % (project,stage2))
	row = db.fetchone()
	if row is None:
		return 'Error'
	order2 = row['stageorder']

	db.execute("UPDATE stages SET stageorder=%s WHERE projid=%s AND stagename ILIKE '%s'" % (order1,project,stage2))
	g.db.commit()

	db.execute("UPDATE stages SET stageorder=%s WHERE projid=%s AND stagename ILIKE '%s'" % (order2,project,stage1))
	g.db.commit()

	return pull_tasks(project)

#Example url
#http://purpletall.cs.longwood.edu:5000/projlist
@app.route("/projlist", methods=["GET","POST"])
def projlist():
	#with get_db() as db: #same as try, but with no "else" like exception catch
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
		close_db('')
		if request.method == "GET":
			return json.dumps(data) 
		else:
			current = request.form.get("user","back!")
			number = request.form.get("userid","0")
			return render_template("/list.html", List = data['projects'], curUser = current, uid=number)
	except:
		return 'Error'

if __name__ == "__main__":
	app.run(host='0.0.0.0')
