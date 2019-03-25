from flask import Flask

app = Flask(__name__)


@app.route("/")
def hello_world():
	return "Hello World"

@app.route("/TASK/<string:task>")
def new_task(task):
	n_task = ""
	for word in task.split():
		n_task = n_task + word + " "
	return n_task

@app.route("/add/<string:task_name>/<string:desc>/<string:ect>")
def add(task_name,desc,ect):
	return task_name + "  " + desc + "  " + ect

@app.route("/move/<string:task_id>/<string:dest>")
def move(task_id,dest):
	return task_id + "  " + desc

if __name__ == "__main__":
	app.run(host='0.0.0.0')
