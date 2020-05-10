from flask import Flask, jsonify
import numpy as np
import pandas as pd
import datetime as dt
import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func

engine = create_engine("sqlite:///Resources/hawaii.sqlite")

# reflect an existing database into a new model
Base = automap_base()
Base.prepare(engine, reflect=True)

# Save references to each table
Measurement = Base.classes.measurement
Station = Base.classes.station

app = Flask(__name__)

@app.route("/")
def home():
    return (
        f"Honolulu, Hawaii Weather Temperatures<br/>"
        f"Available Routes:<br/>"
        f"/api/v1.0/precipitation<br/>"
        f"/api/v1.0/stations<br/>"
        f"/api/v1.0/tobs<br/>"
        f"/api/v1.0/start_date ---date format should be YYYY-MM-DD<br/>"
        f"/api/v1.0/start_date/end_date ---start and end date format should be YYYY-MM-DD"
        )

@app.route("/api/v1.0/precipitation")
def precipitation():
    # Create our session (link) from Python to the DB
    session = Session(engine)

    #Retrieve the date and precipitation scores for the past year
    prec_results = session.query(Measurement.date, Measurement.prcp).\
        filter(func.strftime("%Y-%m-%d", Measurement.date) >= dt.date(2016, 8, 23)).all()
    
    session.close()

 # Create a dictionary from the row data and append to a list of precipitation data
    precipitation = []
    for date, prcp in prec_results:
        precipitation_dict = {date:prcp}

        #precipitation_dict["date"] = prcp
        #precipitation_dict["precipitation"] = prcp
        precipitation.append(precipitation_dict)

    return jsonify(precipitation)

@app.route("/api/v1.0/stations")
def station():
    session = Session(engine)

#Retrieve station data
    st_results = session.query(Station.station,Station.name).all()
    session.close()

# Create a dictionary from the row data and append to a list of station data
    all_stations = []
    for station, name in st_results:
        station_dict = {}
        station_dict["station"] = station
        station_dict["station name"] = name
        all_stations.append(station_dict)

    return jsonify(all_stations)

@app.route("/api/v1.0/tobs")
def temperature():
    # Create our session (link) from Python to the DB
    session = Session(engine)

    #Retrieve the date and temperature for the most active station
    temp_results = session.query(Measurement.date, Measurement.tobs).\
    filter(func.strftime("%Y-%m-%d", Measurement.date) >= dt.date(2016, 8, 23)).\
    filter(Measurement.station == 'USC00519281').all()
    
    session.close()

# Create a dictionary from the row data and append to a list of date and temperature data
    temperature = []
    for date, tobs in temp_results:
        temperature_dict = {}
        temperature_dict["date"] = date
        temperature_dict["temperature"] = tobs
        temperature.append(temperature_dict)

    return jsonify(temperature)

@app.route("/api/v1.0/<start>")
def temperature_by_date(start):
    """Fetch the min,max,and avg temperature whose date matches
       the path variable supplied by the user, or a 404 if not."""
    session = Session(engine)

#Retrieve the min, max, avg temperature for a given start range.
    start_results = session.query(Measurement.date,func.max(Measurement.tobs),func.min(Measurement.tobs),func.avg(Measurement.tobs)).\
        filter(Measurement.date >= start).group_by(Measurement.date).all()

    session.close

    temp_dates = []
    for date, max_temp,min_temp,avg_temp in start_results:
        temp_by_date_dict = {}
        temp_by_date_dict["date"] = date
        temp_by_date_dict["max_temperature"] = max_temp
        temp_by_date_dict["min_temperature"] = min_temp
        temp_by_date_dict["avg_temperature"] = avg_temp
        temp_dates.append(temp_by_date_dict)

        
    return jsonify(temp_dates)
            

    
@app.route("/api/v1.0/<start>/<end>")
def temperature_by_start_end_date(start,end):
    """Fetch the min,max,and avg temperature whose start and end date matches
       the path variable supplied by the user, or a 404 if not."""
    session = Session(engine)

#Retrieve the min, max, avg temperature for a given start and end range.
    start_end_results = session.query(Measurement.date,func.max(Measurement.tobs),func.min(Measurement.tobs),func.avg(Measurement.tobs)).\
        filter(Measurement.date >= start).\
        filter(Measurement.date <= end).group_by(Measurement.date).all()

    session.close

    temp_st_end_dates = []
    for date, max_temp,min_temp,avg_temp in  start_end_results:
        temp_by_st_end_date_dict = {}
        temp_by_st_end_date_dict["date"] = date
        temp_by_st_end_date_dict["max_temperature"] = max_temp
        temp_by_st_end_date_dict["min_temperature"] = min_temp
        temp_by_st_end_date_dict["avg_temperature"] = avg_temp
        temp_st_end_dates.append(temp_by_st_end_date_dict)

     
    return jsonify(temp_st_end_dates)
    


if __name__ == '__main__':
    app.run(debug=True)