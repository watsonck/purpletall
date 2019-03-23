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


if __name__ == "__main__":
    app.run()
