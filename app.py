from flask import Flask, flash, redirect, render_template, request, url_for
from datetime import datetime
from neo4j import GraphDatabase
from src.graphRepository import GraphRepository
from src.ryanairApi import getActiveAirports, getDestinationsForAirport
from src.utils import build_trips_from_neo4j_results, distanceForEachAirport
from typing import List


# BASE_AIRPORTS = ["DUB", "SNN", "NOC"]

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

def get_airports_by_codes(airport_codes, airports):
    return [airport for airport in airports if airport.code in airport_codes]


# Flask application setup
app = Flask(__name__)
app.secret_key = "supersecretkey"

@app.route("/", methods=["GET"])
def index():
    airports = GraphRepository(get_neo4j_driver()).getAirports()
    country_set = set(airport.countryName for airport in airports)
    country_options = sorted(list(country_set))

    base_airports_obj = GraphRepository(get_neo4j_driver()).getBaseAirports()
    base_airport_codes = {airport.code for airport in base_airports_obj}
    base_airport_codes = sorted(list(base_airport_codes))

    return render_template("index.jinja2", origin_options=base_airport_codes, country_options=country_options)


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
    trips = build_trips_from_neo4j_results(result, adults, GraphRepository(get_neo4j_driver()).getAirports())
    
    trips.sort(key=lambda t: (t.fullFare))

    return render_template("trips.jinja2", trips=trips)


@app.route("/admin", methods=["GET", "POST"])
def admin():
    airports = getActiveAirports()
    airport_codes = {airport.code for airport in airports}
    
    airport_codes = sorted(list(airport_codes))
    
    driver = get_neo4j_driver()
    base_airports_obj = GraphRepository(driver).getBaseAirports()
    base_airport_codes = {airport.code for airport in base_airports_obj}
    
    # global selected_airports
    if request.method == "POST":
        # Update selected base airports        
        GraphRepository(driver).clearGraph()
        
        selected_airports = request.form.getlist("base_airports")
        
        desinations = set()

        GraphRepository(driver).save_airports(airports)
        
        for selected_airport in selected_airports:
            GraphRepository(driver).setBaseAirport(selected_airport, True)

        for aiport in selected_airports:
            flights = getDestinationsForAirport(aiport, airports)
            GraphRepository(driver).save_flights(flights)
            for flight in flights:
                desinations.add(flight.origin.code)

        airport_objects = get_airports_by_codes(desinations, airports)

        distances = distanceForEachAirport(airport_objects)

        GraphRepository(driver).save_distances(distances)
        
        flash(f"Selected base airports updated: {', '.join(selected_airports)}", "success")
        return redirect(url_for("admin"))

    return render_template("admin.jinja2", 
                           airport_codes=airport_codes,
                           base_airport_codes=base_airport_codes)

@app.route("/update_all_flights", methods=["POST"])
def update_all_flights():
    driver = get_neo4j_driver()
    airports = getActiveAirports()
    
    # Get current base airports
    base_airports_obj = GraphRepository(driver).getBaseAirports()
    base_airport_codes = [airport.code for airport in base_airports_obj]

    destinations = set()
    GraphRepository(driver).save_airports(airports)

    # Update flights for all base airports
    for aiport in base_airport_codes:
        flights = getDestinationsForAirport(aiport, airports)
        GraphRepository(driver).save_flights(flights)
        for flight in flights:
            destinations.add(flight.origin.code)

    airport_objects = get_airports_by_codes(destinations, airports)
    distances = distanceForEachAirport(airport_objects)
    GraphRepository(driver).save_distances(distances)

    flash(f"Flights updated for base airports: {', '.join(base_airport_codes)}", "success")
    return redirect(url_for("admin"))


if __name__ == "__main__":
    app.run(debug=True)
