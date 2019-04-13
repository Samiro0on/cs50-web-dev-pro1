# set FLASK_ENV = development
# set FLASK_APP = applicationRelease.py

import csv
import os
from flask import Flask, session, render_template, request
from flask_session import Session

from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker

app = Flask(__name__)
# FLASK_DEBUG = True
# app.run(debug=True)
engine = create_engine("postgres://rvzxecodqleyqr:c2975f151f1a185f4cf731daf810bceab48cc2fa85a636391d239a1246ccfb6f@ec2-50-17-246-114.compute-1.amazonaws.com:5432/deomrc7gugeggb")
									# user       :password                                                         @host                                     :port/database

db = scoped_session(sessionmaker(bind=engine))
app.config['ENV'] = 'development'
app.config['DEBUG'] = True

@app.route("/")
def index():
    flights = db.execute("SELECT * FROM flights").fetchall()
    return render_template("index.html", flights=flights)
@app.route("/book", methods=["POST"])
def book():
    '''Book a flight'''
    name = request.form.get("name")
    try:
        flight_id = int(request.form.get("flight_id"))
    except ValueError:
        return render_template("error.html", message="Invalid flight number.")

    # Make sure the flight exists.
    if db.execute("SELECT * FROM flights WHERE id = :id", {"id": flight_id}).rowcount == 0:
        return render_template("error.html", message="No such flight with that id.")
    db.execute("INSERT INTO Passangers (name, flight_id) VALUES (:name, :flight_id)",
               {"name": name, "flight_id": flight_id})
    db.commit()
    return render_template("success.html")

@app.route("/flights")
def flights():
    '''list of all flights'''
    flights = db.execute("SELECT * FROM flights").fetchall()
    return render_template("flights.html", flights=flights)

@app.route("/flights/<int:flight_id>")
def flight(flight_id):
    '''list details about a single flight'''

    flight = db.execute("SELECT * FROM flights WHERE id = :id",
                        {"id":flight_id }).fetchone()
    if flight is None:
        return render_template("error.html", message = "No such a flight")

    passangers = db.execute("SELECT * FROM Passangers WHERE flight_id = :flight_id",
                            {"flight_id": flight_id}).fetchall()
    # print(passangers)
    return render_template("flight.html", passangers = passangers, flight = flight)

app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)
if __name__ == "__main__":

    app.run(debug=True)

