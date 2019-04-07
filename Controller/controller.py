from flask import Flask,request,g,redirect,escape,render_template
import psycopg2,psycopg2.extras,time,json,git

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
	if request.method == "GET":
	    #example for other actual functions below,
	    #give plain/JSON output here
	    return "Hello World"
	else:
	    #build web page otherwise, sending what it would need in comma list
	    return render_template("../../Web/login.html")
	    #might need to move file and rename path, jinja looks for templates


#Example url
#http://purpletall.cs.longwood.edu:5000/1/LIST
#Help: https://realpython.com/python-json/
@app.route("/<int:project>/LIST")
def pull_tasks(project):
	json_dict = {}
	json_dict['metadata'] = {}
	json_dict['stages'] = {}
	db = get_db()
	db.execute("SELECT count(projid) AS count FROM stages WHERE projid=%d;"% (project))
	stages = int(db.fetchone()['count'])
	if stages == 0:
	    return 'Stage Error: No stages on project'

	json_dict['metadata']['project'] = project
	json_dict['metadata']['stagecount'] = stages
	json_dict['metadata']['stages'] = {}
	    
	db.execute("SELECT stageorder AS id,stagename AS name FROM stages WHERE projid=%d;"% (project))
	for row in db.fetchall():
	    json_dict['metadata']['stages'][row['id']]= row['name']


	db.execute("SELECT id,task.name as name,contributor,stage FROM task,projects WHERE task.projid = projects.projid AND projects.projid=%d;"% (project))
	tasks = db.fetchall()
	for row in tasks:
	    json_dict['stages'][row['stage']] = []
	for row in tasks:
	    json_dict['stages'][row['stage']].append({
	        'id': row['id'],
	        'name': row['name'],
	        'user': row['contributor'],
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
	    bug = request.args.get('bug','false').replace('{','').replace('}','')
	    start = time.asctime(time.localtime(time.time()))

	db = get_db()
	db.execute("SELECT stagename FROM stages WHERE projid=%d ORDER BY stageorder LIMIT 1;"%(project))
	stage = db.fetchone()['stagename']

	db.execute("INSERT INTO task (name,description,startTime,exptCompTime,stage,projid) VALUES ('%s','%s','%s','%s','%s',%d);" % (name,desc,start,ect,stage,project))
	g.db.commit()
	return pull_tasks(project)

#Example url
#http://purpletall.cs.longwood.edu:5000/1/move?id=1&stage={complete}
@app.route("/<int:project>/move", methods=["GET", "POST"])
def move(project):
	#if request.method=="GET"
	taskid = request.args.get('id',0)
	stage = request.args.get('stage','N/A').replace('{','').replace('}','')

	db = get_db()
	db.execute("SELECT count(*) AS count FROM stages WHERE projid=%d AND stagename ILIKE '%s';"% (project, stage))
	if db.fetchone()['count'] > 0:
	    db.execute("UPDATE task SET stage='%s' WHERE id=%s AND projid=%d;" % (stage, taskid, project))
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
	db.execute("SELECT name,description,stage,exptcomptime,actcomptime,contributor FROM task WHERE id = %d AND projid=%d;" % (int(taskid),project))
	row = db.fetchone() #should be a single disctionaly/map object list
	name = 'split: ' + row['name']
	desc = row['description']
	stage = row['stage']
	start = time.asctime(time.localtime(time.time()))
	ect = row['exptcomptime']
	act = row['actcomptime']
	user = row['contributor']

	if user == None:
		user = 0
	if stage == None:
		stage = 0

	db.execute("INSERT INTO task(projid,name,description,stage,starttime,exptcomptime,actcomptime,contributor) VALUES (%d,'%s','%s','%s','%s','%s','%s',%s)" % (project,name,desc,str(stage),start,ect,act,str(user)))
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
#http://purpletall.cs.longwood.edu:5000/ping?user={haddockcl}
@app.route("/ping", methods=["GET", "POST"])
def ping():
	return ''

#Example url
#http://purpletall.cs.longwood.edu:5000/login?user={haddockcl}
@app.route("/login", methods=["GET", "POST"])
def login():
	return ''

if __name__ == "__main__":
	app.run(host='0.0.0.0')
