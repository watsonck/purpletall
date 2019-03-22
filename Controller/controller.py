from flask import Flask

app = Flask(__name__)

@app.route("/")
def hello_world():
    return "Hello World"

@app.route("/TODO")
def todo_test():
    return "TODO this is from the flask server"

@app.route("/INPR")
def inpr_test():
    return "INPR 0"

@app.route("/COMP")
def comp_test():
    return "COMP 0"

if __name__ == "__main__":
    app.run()
