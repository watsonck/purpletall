from flask import Flask,request,g,redirect,escape,render_template
import psycopg2,psycopg2.extras,time,json,git

app = Flask(__name__)

app.config.from_object(__name__)
app.config.update( dict(
	DATABASE="purpletall",
	SECRET_KEY="Lizard Overlords",
	USERNAME="purpletall",
	PASSWORD="purpletall"
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
def hello_world():
	if request.method == "GET":
		#example for other actual functions below,
		#give plain/JSON output here
		return "Hello World"
	else:
		#build web page otherwise, sending what it would need in comma list
		return render_template("../../Web/login.html")
		#might need to move file and rename path, jinja looks for templates

@app.route("/TASK/<string:task>")
def new_task(task):
	n_task = ""
	for word in task.split():
		n_task = n_task + word + " "
	db = getdb()
	#fetch the task info from Database here
	#todo: parse n_task, or directly use it as 'id'
	#db.execute("SELECT * FROM tasks WHERE taskid = '%s' % (id))
	return n_task


def pull_tasks(project):
	json_string = '{'
	db = get_db()
	db.execute("SELECT id,name,user FROM tasks NATURAL JOIN projects WHERE projid=%d;"% (projid))
	db.fetchall()
	json_string += '}'
	return json.dumps(json_string)


#Example url
#http://purpletall.cs.longwood.edu:5000/<string:project>/add?name={Bug1}&desc={This%20bug%20is%20in%20controller}&time={2019-05-1}&bug={true}
#Help: https://support.clickmeter.com/hc/en-us/articles/211032666-URL-parameters-How-to-pass-it-to-the-destination-URL
@app.route("/<string:project>/add", methods=["GET", "POST"])
def add(project):
	if request.method=="GET":
		name = request.args.get('name','N/A').replace('{','').replace('}','')
		desc = request.args.get('desc','N/A').replace('{','').replace('}','')
		ect = request.args.get('time','N/A').replace('{','').replace('}','')
		bug = request.args.get('bug','false').replace('{','').replace('}','')
		start = time.asctime(time.localtime(time.time()))
	#else:   
		db = get_db()
		db.execute("INSERT INTO task (name,description,start_time,exp_comp_time,is_bug,stage) VALUES ('%s','%s','%s','%s','%s','todo');" % (name,desc,start,ect,bug))
		g.db.commit()
		#why is it returning name? for debug/proof it did something?
		return pull_tasks(project)

#Example url
#http://purpletall.cs.longwood.edu:5000/<string:project>/move?id=1&stage={complete}
@app.route("/<string:project>/move", methods=["GET", "POST"])
def move(project):
	#if request.method=="GET"
	taskid = request.args.get('id',0)
	stage = request.args.get('stage','N/A').replace('{','').replace('}','')

	db = get_db()
	db.execute("UPDATE task SET stage='%s' WHERE id=%s;" % (stage, taskid))
	g.db.commit()
	return pull_tasks(project)

#Example url
#http://purpletall.cs.longwood.edu:5000/<string:project>/remove?id=1
@app.route("/<string:project>/remove", methods=["GET", "POST"])
def remove(project):
	if request.method=="GET":
		taskid = request.args.get('id',0)
		if taskid:
		    db = get_db()
		    db.execute("DELETE FROM task WHERE id = '%s'" % (taskid))
		    db.execute("DELETE FROM logs WHERE taskId = '%s'" % (taskid))
		    #manual cascade'ing till know friegn keys are setup correctly
	return pull_tasks(project)
	#else:
		#return render_template( path to a result web page or default )

#Example url
#http://purpletall.cs.longwood.edu:5000/<string:project>/split?id=1
@app.route("/<string:project>/split", methods=["GET", "POST"]) #post still listed for web
def split(project):
	db = getdb()
	taskid = request.args.get('id',0)
	db.execute("SELECT * FROM task WHERE id = '%s'" % (taskid))
	rows = db.fetchall() #should be a single disctionaly/map object list
	rows['id'] = ""

	db.execute("INSERT INTO task VALUES ('%s', '%s', '%s', '%s', '%s', 'todo')" % (rows))
	#might need to fix to explitly grab each thing in the row list
	return pull_tasks(project)

#Example url
#http://purpletall.cs.longwood.edu:5000/<string:project>/split?id=1
@app.route("/<string:project>/modify", methods=["GET", "POST"])
def modify(project):
		#need to expand this to include what sort of modification
	return pull_tasks(project)

#Example url
#http://purpletall.cs.longwood.edu:5000/<string:project>/info?id=1
@app.route("/<string:project>/info", methods=["GET", "POST"])
def info(project):
	db = getdb()
	taskid = 0;
	if request.method=="GET":
		taskid = request.args.get('id', 0)
		db.execute("SELECT * FROM task WHERE id = '%s'" % (taskid))
		return '' #organized plain text or a JSON
	else:
		taskid = request.form.getValue('id', 0) #might need to wrap in an escape()
		db.execute("SELECT * FROM task WHERE id = '%s'" % (taskid))
		return '' #redirect to view page, which will do displaying

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
