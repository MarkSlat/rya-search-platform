from flask import Flask, render_template, request
from datetime import datetime
from neo4j import GraphDatabase
from src.graphRepository import GraphRepository
from src.utils import build_trips_from_neo4j_results
from typing import List


BASE_AIRPORTS = ["DUB", "SNN", "NOC"]

# Example function to parse dates
def parse_dates(date_string: str) -> List[datetime]:
    return [
        datetime.strptime(d.strip(), "%Y-%m-%d").date()
        for d in date_string.split(",")
        if d.strip()
    ]

# Parse comma-separated input into lists
def parse_list(value: str) -> List[str]:
    return [v.strip() for v in value.split(",") if v.strip()]

# Neo4j driver setup
def get_neo4j_driver(uri="bolt://localhost:7687", user="neo4j", password="test1234"):
    return GraphDatabase.driver(uri, auth=(user, password))

# Flask application setup
app = Flask(__name__)


@app.route("/", methods=["GET"])
def index():
    airports = GraphRepository(get_neo4j_driver()).getAirports()
    country_set = set(airport.countryName for airport in airports)
    country_options = sorted(list(country_set))

    return render_template("index.jinja2", origin_options=BASE_AIRPORTS, country_options=country_options)


@app.route("/submit", methods=["POST"])
def submit():
    origin_departure_airports = request.form.getlist("origin_departure_airports[]")
    origin_arrival_airports = request.form.getlist("origin_arrival_airports[]")

    r1_dates = parse_dates(request.form["r1_dates"])
    r2_dates = parse_dates(request.form["r2_dates"])

    lengths_of_stay = [int(x) for x in parse_list(request.form["lengths_of_stay"])]
    adults = int(request.form["adults"])
    
    blacklist_countries = request.form.getlist("blacklist_countries[]")
    whitelist_countries = request.form.getlist("whitelist_countries[]")

    same_airport_return = "same_airport_return" in request.form
    max_distance = int(request.form["max_distance"]) if request.form.get("max_distance") else None

   # Run the query
    result = GraphRepository(get_neo4j_driver()).query_flights(
        origin_departure_airports,
        origin_arrival_airports,
        r1_dates,
        r2_dates,
        lengths_of_stay,
        blacklist_countries,
        whitelist_countries,
        same_airport_return,
        max_distance
    )

    # Build trips from the query result
    trips = build_trips_from_neo4j_results(result, adults)
    
    trips.sort(key=lambda t: (t.fullFare))

    return render_template("trips.jinja2", trips=trips)

if __name__ == "__main__":
    app.run(debug=True)
