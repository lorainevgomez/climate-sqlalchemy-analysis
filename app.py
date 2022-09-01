import numpy as np

import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func
import datetime as dt

from flask import Flask, jsonify


#################################################
# Database Setup
#################################################
engine = create_engine("sqlite:///hawaii.sqlite")

# reflect an existing database into a new model
Base = automap_base()
# reflect the tables
Base.prepare(engine, reflect=True)

# Save reference to the table
Measurement = Base.classes.measurement
Station = Base.classes.station

#################################################
# Flask Setup
#################################################
app = Flask(__name__)


#################################################
# Flask Routes
#################################################

@app.route("/")
def Homepage():
    """List all available api routes."""
    return (
        f"Available Routes:<br/>"
        f"/api/v1.0/precipitation<br/>"
        f"/api/v1.0/stations<br/>"
        f"/api/v1.0/tobs<br/>"
        f"/api/v1.0/<start><br/>"
        f"/api/v1.0/<start>/<end>"
    )


@app.route("/api/v1.0/precipitation")
def precipitation():
    # Create our session (link) from Python to the DB
    session = Session(engine)

    """Return a list of all precipitation"""
    # Query all precipitation
    results = session.query(Measurement.date, Measurement.prcp).all()

    session.close()

    #Convert the query results to a dictionary using `date` as the key and `prcp` as the value.
    all_precipitation = []
    for date, prcp in results:
        precipitation_dict = {}
        precipitation_dict["date"] = date
        precipitation_dict["prcp"] = prcp
        all_precipitation.append(precipitation_dict)
    #Return the JSON representation of your dictionary.
    return jsonify(all_precipitation)



@app.route("/api/v1.0/stations")
def stations():

    # Create our session (link) from Python to the DB
    session = Session(engine)


    
    # Query all stations
    results = session.query(Station.id, Station.station, Station.name).all()

    #Always close the session
    session.close()

    all_stations = []
    for id, station, name in results:
        stations_dict = {}
        stations_dict["id"] = id
        stations_dict["station"] = station
        all_stations.append(stations_dict)

    # Return a JSON list of stations from the dataset.
    return jsonify(all_stations)

@app.route("/api/v1.0/tobs")

def tobs():

    # Create our session (link) from Python to the DB
    session = Session(engine)

    #Finding most active station, reference climate_starter
    most_active_stations = session.query(Measurement.station,func.count(Measurement.station)).\
        group_by(Measurement.station).\
        order_by(func.count(Measurement.station).desc()).first()[0]

    #Query the dates and temperature observations of the most active station for the previous year of data. (reference climate_starter)
    most_recent = session.query(Measurement.date).order_by(Measurement.date.desc()).first()[0]
    previous_year = (dt.datetime.strptime(most_recent, "%Y-%m-%d") - dt.timedelta(days=365))

    #Return a JSON list of temperature observations (TOBS) for the previous year.
    temp_o = session.query(Measurement.tobs).filter(Measurement.date >= previous_year).\
                    filter(Measurement.station == most_active_stations).all()


    #Always Close Session
    session.close()
    # Return a JSON list of temperature observations (TOBS) for the previous year.
    return jsonify(temp_o)

    #Return a JSON list of the minimum temperature, the average temperature, and the maximum temperature for a given start or start-end range.

    # When given the start only, calculate `TMIN`, `TAVG`, and `TMAX` for all dates greater than or equal to the start date.

    #When given the start and the end date, calculate the `TMIN`, `TAVG`, and `TMAX` for dates from the start date through the end date (inclusive).





if __name__ == '__main__':
    app.run(debug=True)
