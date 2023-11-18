# Import the dependencies.
import numpy as np
import pandas as pd
import datetime as dt
import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func
from sqlalchemy import desc
from matplotlib import style
style.use('fivethirtyeight')
import matplotlib.pyplot as plt
from flask import Flask, jsonify


#################################################
# Database Setup
#################################################
engine = create_engine("sqlite:///hawaii.sqlite")

# reflect an existing database into a new model
Base = automap_base()
# reflect the tables
Base.prepare(autoload_with=engine)

# Save references to each table
measurement = Base.classes.measurement
station = Base.classes.station

# Create our session (link) from Python to the DB
session = Session(engine)

#################################################
# Flask Setup
#################################################
app = Flask(__name__)
#################################################
# Flask Routes
#################################################

@app.route('/')
def home():
    #list all available api routes
    return("Welcome! List of all available api routes:<br/>"
           f"/api/v1.0/precipitation<br/>"
           f"/api/v1.0/stations<br/>"
           f"/api/v1.0/tobs<br/>"
           f"from start date onward: /api/v1.0/yyyymmdd<br/>"
           f"between start and end date: /api/v1.0/yyyymmdd/yyyymmdd")

@app.route("/api/v1.0/precipitation")
def precipitation():
    mostrecentdate = dt.datetime(2017, 8, 23)
    # Calculate the date one year from the last date in data set.
    oneyearprevious = mostrecentdate - dt.timedelta(days=365)
    # Perform a query to retrieve the data and precipitation scores
    last12months = session.query(measurement.date,measurement.prcp)\
    .filter(measurement.date >= oneyearprevious).order_by(desc(measurement.date)).all()
    raindata = []
    for date, prcp in last12months:
        rain_dct = {}
        rain_dct[f"{date}"]= prcp
        raindata.append(rain_dct)
    
    return jsonify(raindata)

@app.route("/api/v1.0/stations")
def stations():
    allstations = session.query(station.station).all()
    stationslist = []
    for s in allstations:
        stationslist.append(s[0])
    return jsonify(stationslist)

@app.route("/api/v1.0/tobs")
def tobs():
    mostrecentdate = dt.datetime(2017, 8, 23)
    oneyearprevious = mostrecentdate - dt.timedelta(days=365)
    ma12monthq = session.query(measurement.tobs).filter(measurement.station=='USC00519281').filter(measurement.date >= oneyearprevious).all()
    ma12monthdata = []
    for data in ma12monthq:
        ma12monthdata.append(data[0])
    return jsonify(ma12monthdata)

@app.route("/api/v1.0/<startdate>")
def start(startdate):
    tobsbydate = session.query(func.min(measurement.tobs),func.max(measurement.tobs),func.avg(measurement.tobs))\
              .filter(measurement.date>=startdate).all()
    tobsdata = []
    for data in tobsbydate:
        tobsdata.append(data[0])
        tobsdata.append(data[1])
        tobsdata.append(data[2])
    return jsonify(tobsdata)


@app.route("/api/v1.0/<startdate>/<enddate>")
def startend(startdate,enddate):
    tobsbydate = session.query(func.min(measurement.tobs),func.max(measurement.tobs),func.avg(measurement.tobs))\
              .filter(measurement.date>=startdate).filter(measurement.date<=enddate).all()
    tobsdata = []
    for data in tobsbydate:
        tobsdata.append(data[0])
        tobsdata.append(data[1])
        tobsdata.append(data[2])
    return jsonify(tobsdata)


if __name__ == '__main__':
    app.run(debug=True)