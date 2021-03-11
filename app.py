import numpy as np

import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func

from flask import Flask, jsonify
from sqlalchemy.sql.expression import union


#################################################
# Database Setup
#################################################
engine = create_engine("sqlite:///Resources/hawaii.sqlite")

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
def hawaii ():
    """List all available api routes."""
    return (
        f"Available Routes:<br/>"
        f"/api/v1.0/prcp<br/>"
        f"/api/v1.0/station<br/>"
        f"/api/v1.0/tobs<br/>"
        f"/api/v1.0/start<br/>"
        f"/api/v1.0/start/end"
    )

@app.route("/api/v1.0/prcp")
def precipitation():
    # Create our session (link) from Python to the DB
    session = Session(engine)

    # Query all using date as key and prcp as value

    query_date = "2016-8-23"

    results_precip = session.query(Measurement.date, Measurement.prcp).\
            filter(func.strftime("%Y-%m-%d", Measurement.date) >= query_date).\
                order_by(Measurement.date).all()
    session.close()
    
    #return jsonify(results_precip)

    # Create a dictionary from the row data and append the precipitation data
    precipitation_data = []
    for date, prcp in results_precip:
        precipitation_dict = {}
        precipitation_dict["date"] = date
        precipitation_dict["prcp"] = prcp
        precipitation_data.append(precipitation_dict)
    
    return jsonify(precipitation_data)

@app.route("/api/v1.0/station")
def station():
    # Create our session (link) from Python to the DB
    session = Session(engine)

    station_name = session.query(Station.station, Station.name).all()
    # station_list = session.query(Measurement.station).all()
    # station_query = station_name.union(station_list)

    station_query = list(np.ravel(station_name))

    session.close()

    return jsonify(station_query)

@app.route("/api/v1.0/tobs")
def tobs():
    # Create our session (link) from Python to the DB
    session = Session(engine)

    # Query the dates and temperature observations of the most active station for the last year of data.

    # most_active = session.query(Measurement.station, func.count(Measurement.station)).\
    # group_by(Measurement.station).\
    #     order_by(func.count(Measurement.station).desc()).\
    #         all()
    # session.close()
    
    query_date = "2016-8-23"

    tobs_query = session.query(Measurement.station, Measurement.tobs).\
    filter(Measurement.station == 'USC00519281').\
        filter(func.strftime("%Y-%m-%d", Measurement.date) >= query_date).\
            group_by(Measurement.date).order_by(Measurement.date).all()
    
    tobs_result = list(np.ravel(tobs_query))

    session.close()

    return jsonify(tobs_result)

# Return a JSON list of the minimum temperature, the average temperature, and the max temperature for a given start or start-end range.
# When given the start only, calculate TMIN, TAVG, and TMAX for all dates greater than and equal to the start date.
# When given the start and the end date, calculate the TMIN, TAVG, and TMAX for dates between the start and end date inclusive.

@app.route("/api/v1.0/<start>", methods = ["GET"])
def start_date_only(start):

    session = Session(engine)

    start_date_only_results = session.query(func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)).\
        filter(Measurement.date >= start).all()

    result_list = list(np.ravel(start_date_only_results))

    session.close()

    return jsonify(result_list)

@app.route("/api/v1.0/<start_date>/<end_date>", methods = ["GET"])
def start_end_date(start_date=None, end_date=None):

    session = Session(engine)

    start_end_results = session.query(func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)).\
        filter(Measurement.date >= start_date).\
            filter(Measurement.date <= end_date).all()

    result_list_startend = list(np.ravel(start_end_results))
    
    session.close()

    return jsonify(result_list_startend)

if __name__ == '__main__':
    app.run(debug=True)