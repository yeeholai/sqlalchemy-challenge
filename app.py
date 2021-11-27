import numpy as np

import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func

from flask import Flask, jsonify

# Database Setup
engine = create_engine("sqlite:///../Resources/hawaii.sqlite")

# reflect an existing database into a new model
Base = automap_base()
# reflect the tables
Base.prepare(engine, reflect=True)
# save reference to the table
Measurement = Base.classes.measurement
Station = Base.classes.station

# Flask Setup

app = Flask(__name__)

# Flast Routes

@app.route("/")
def home():
	print("Server received request for 'Home' page..")
	return(f"Welcome to the Homepage:<br/>"
		f"/api/v1.0/precipitation<br/>"
		f"/api/v1.0/stations<br/>"
		f"/api/v1.0/tobs<br/>"
		f"/api/v1.0/[start_date format:yyyy-mm-dd]<br/>"
		f"/api/v1.0/[start_date format:yyyy-mm-dd]/[end_date format:yyyy-mm-dd]")

@app.route("/api/v1.0/precipitation")
def precipitation():
	session = Session(engine)
	results = session.query(Measurement.date, Measurement.prcp).\
  		filter(Measurement.date>="2016-08-23").\
    	order_by(Measurement.date.desc()).all()
	session.close()
	all_precip = []

	for date,prcp in results:
		dictionary = {}
		dictionary["date"] = date
		dictionary["prcp"] = prcp
		all_precip.append(dictionary) 


	return jsonify(all_precip)


@app.route("/api/v1.0/stations")
def stations():
	session = Session(engine)
	results = session.query(Station.station).all()
	session.close()
	all_stations = list(np.ravel(results))

	return jsonify(all_stations)

@app.route("/api/v1.0/tobs")
def tobs():
	session = Session(engine)
	results = session.query(Measurement.date, Measurement.tobs).\
		filter(Measurement.date>="2016-08-23").\
		filter(Station.station==Measurement.station).\
		filter(Station.id==7).\
		order_by(Measurement.date).all()
	session.close()
	all_tobs = list(np.ravel(results))

	return jsonify(all_tobs)

@app.route("/api/v1.0/<date>")
def daily_normals(date):
    session = Session(engine)
    results = session.query(func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)).\
    filter(Measurement.date >= date).all()
    session.close()
    one_date_filter = []
    for min,avg,max in results:
        dictionary ={}
        dictionary["Min Temp"] = min
        dictionary["Avg Temp"] = avg  
        dictionary["Max Temp"] = max
        one_date_filter.append(dictionary)

    return jsonify(one_date_filter)

@app.route("/api/v1.0/<start_date>/<end_date>")
def calc_temps(start_date, end_date):

    session = Session(engine)

    results = session.query(func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)).\
        filter(Measurement.date >= start_date).filter(Measurement.date <= end_date).all()

    session.close()

    date_filter = []

    for min,avg,max in results:
    	dictionary ={}
    	dictionary["Min Temp"] = min
    	dictionary["Avg Temp"] = avg  
    	dictionary["Max Temp"] = max
    	date_filter.append(dictionary)

    return jsonify(date_filter)

if __name__=="__main__":
	app.run(debug=True)