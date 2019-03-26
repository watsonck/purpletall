from flask import Flask,request,g,redirect,escape
import psycopg2,psycopg2.extras,time

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

@app.route("/")
def hello_world():
	return "Hello World"

@app.route("/TASK/<string:task>")
def new_task(task):
	n_task = ""
	for word in task.split():
		n_task = n_task + word + " "
	return n_task

#Example url
#http://204.111.247.205:5000/add?name={Bug1}&desc={This%20bug%20is%20in%20controller}&time={2019-05-1}&bug={true}
#Help: https://support.clickmeter.com/hc/en-us/articles/211032666-URL-parameters-How-to-pass-it-to-the-destination-URL
@app.route("/add")
def add():
	name = request.args.get('name','N/A').replace('{','').replace('}','')
	desc = request.args.get('desc','N/A').replace('{','').replace('}','')
	ect = request.args.get('time','N/A').replace('{','').replace('}','')
	bug = request.args.get('bug','false').replace('{','').replace('}','')
	start = time.asctime(time.localtime(time.time()))

	db = get_db()
	db.execute("INSERT INTO task(name,description,start_time,exp_comp_time,is_bug,stage) values ('%s','%s','%s','%s','%s','todo');" % (name,desc,start,ect,bug))
	g.db.commit()
	return name

#Example url
#http://204.111.247.205:5000/move?id=1&stage={complete}
@app.route("/move")
def move():
	id = request.args.get('id',0)
	stage = request.args.get('stage','N/A').replace('{','').replace('}','')

	db = get_db()
	db.execute("UPDATE task SET stage='%s' WHERE id=%s;" % (stage,id))
	g.db.commit()
	return id


#Example url
#http://204.111.247.205:5000/remove?id=1
@app.route("/remove")
def remove():
	return ''

#Example url
#http://204.111.247.205:5000/split?id=1
@app.route("/split")
def split():
	return ''

#Example url
#http://204.111.247.205:5000/split?id=1
@app.route("/modify")
def modify():
	return ''

#Example url
#http://204.111.247.205:5000/info?id=1
@app.route("/info")
def info():
	return ''

#Example url
#http://204.111.247.205:5000/ping?user={haddockcl}
@app.route("/ping")
def ping():
	return ''

#Example url
#http://204.111.247.205:5000/login?user={haddockcl}
@app.route("/login")
def login():
	return ''

if __name__ == "__main__":
	app.run(host='0.0.0.0')
