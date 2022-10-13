import numpy as np
import datetime as dt
import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func

from flask import Flask, jsonify

#################################################
# Database Setup
#################################################
engine = create_engine("sqlite:///hawaii.sqlite")
Base = automap_base()
Base.prepare(engine, reflect=True)


# Base.metadata.tables # Check tables, not much useful
# Base.classes.keys() # Get the table names

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
def welcome():
    """List all available api routes."""
    return (
        f"Available Routes:<br/>"
        f"Precipitation: /api/v1.0/precipitation<br/>"
        f"List of Stations: /api/v1.0/stations<br/>"
        f"Temperature for one year: /api/v1.0/tobsall<br/>"
        f"Temperature for one year: /api/v1.0/tobs<br/>"
        f"Start date:/api/v1.0/startdate<br/>"
        f"Start date to end date:/api/v1.0/startdate/enddate")


@app.route('/api/v1.0/precipitation')
def precipitation():
    session = Session(engine)
    sel = [Measurement.date,Measurement.prcp]
    queryresult = session.query(*sel).all()
    session.close()

    precipitation = []
    for date, prcp in queryresult:
        prcp_dict = {}
        prcp_dict["date"] = date
        prcp_dict["precipitation"] = prcp
        precipitation.append(prcp_dict)

    return jsonify(precipitation)

@app.route('/api/v1.0/stations')
def stations():
    session = Session(engine)
    station_results = session.query(Station.station, Station.name).all()
    session.close()

    stations_list = []
    for station,name in station_results:
        station_dict = {}
        station_dict["station"] = station
        station_dict["Name"] = name
        stations_list.append(station_dict)

    return jsonify(stations_list)

@app.route('/api/v1.0/tobsall')
def tobsall():
    session = Session(engine)
    lateststr = session.query(Measurement.date).order_by(Measurement.date.desc()).first()[0]
    latestdate = dt.datetime.strptime(lateststr, '%Y-%m-%d')
    querydate = dt.date(latestdate.year -1, latestdate.month, latestdate.day)
    sel = [Measurement.date,Measurement.tobs]
    queryresult = session.query(*sel).filter(Measurement.date >= querydate).all()
    session.close()

    tobsall = []
    for date, tobs in queryresult:
        tobs_dict = {}
        tobs_dict["Date"] = date
        tobs_dict["Tobs"] = tobs
        tobsall.append(tobs_dict)

    return jsonify(tobsall)

@app.route('/api/v1.0/tobs')
def tobs():
    session = Session(engine)
    prev_year = dt.date(2016, 8, 23) - dt.timedelta(days=365)
    results = session.query(Measurement.tobs).\
        filter(Measurement.station == "USC00519281").\
        filter(Measurement.date >= prev_year).all()
    temps = list(np.ravel(results))
    session.close()
    return jsonify(temps=temps)

@app.route("/api/v1.0/<start>")
def start_date(start):
    # Create our session (link) from Python to the DB
    session = Session(engine)

    """Return a list of minimum, average and max temperature for a given date"""
    # Query of min, max and avg temperature for all dates greater than and equal to the given date.
    results = session.query(Measurement.date,func.min(Measurement.tobs),\
         func.avg(Measurement.tobs), func.max(Measurement.tobs)).\
             filter(Measurement.date >= start).all()
             
    session.close()
    
# Create a dictionary from the row data and append to a list of info
    info = []
    for date, min, avg, max in results:
        info_dict = {}
        info_dict["DATE"] = date
        info_dict["TMIN"] = min
        info_dict["TAVG"] = avg
        info_dict["TMAX"] = max
        info.append(info_dict)

    return jsonify(info)


@app.route("/api/v1.0/<start>/<end>")
def start_end_date(start, end):
    # Create our session (link) from Python to the DB
    session = Session(engine)
    
    """Return a list of minimum, average and max temperature for a given start date and end date"""
    # Query of min, max and avg temperature for dates between given start and end date.
    results = session.query(func.min(Measurement.tobs),\
         func.avg(Measurement.tobs), func.max(Measurement.tobs)).\
             filter(Measurement.date >= start).filter(Measurement.date <= end).all()

    session.close()        
    
# Create a dictionary from the row data and append to a list of info
    info = []

    for min, avg, max in results:
        info_dict = {}
        info_dict["TMIN"] = min
        info_dict["TAVG"] = avg
        info_dict["TMAX "] = max
        info.append(info_dict)



    return jsonify(info)



if __name__ == "__main__":
    app.run(debug=True)
