from flask import Flask

app = Flask(__name__)


@app.route("/")
def hello_world():
    return "Hello World"

@app.route("/ADD/<string:task>")
def todo_test(task):
    return "ADD" + " " + task

@app.route("/MOVE/<string:task>")
def inpr_test(task):
    return "MOVE" + " " + task

@app.route("/COMP/<ctask>")
def comp_test(ctask):
    return "COMP" + " " + str(ctask)

if __name__ == "__main__":
    app.run()
