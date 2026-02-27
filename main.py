from flask import Flask, redirect, jsonify, request
import flask
import functions

app = Flask(__name__)

@app.route("/", methods=["GET"])
def select_timetable():
    timetables = functions.get_subjects()

    return flask.render_template("index.html",
                                 timetables=timetables)

if __name__ == "__main__":
    app.run(debug=True)