from flask import Flask

app = Flask(__name__)

@app.route("/")
def hello_world():
    return "Hello World"

@app.route("/TODO/<string:task>")
def todo_test(task):
    return "TODO" + " " + task

@app.route("/INPR/<itask>")
def inpr_test(itask):
    return "INPR" + " " + str(itask)

@app.route("/COMP/<ctask>")
def comp_test(ctask):
    return "COMP" + " " + str(ctask)

if __name__ == "__main__":
    app.run()
