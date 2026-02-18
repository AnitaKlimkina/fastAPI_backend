from flask import render_template, request
from main import app

@app.route("/api/tweets", methods=["GET"])
def hello():
    data = request.args.getlist("api-key", type=str)
    print(data)
    return render_template("index.html")