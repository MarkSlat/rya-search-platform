from datetime import date
from neo4j import GraphDatabase

from src.graphRepository import GraphRepository
from src.utils import build_trips_from_neo4j_results


def get_neo4j_driver(uri="bolt://localhost:7687", user="neo4j", password="test1234"):
    return GraphDatabase.driver(uri, auth=(user, password))


def populateAirportsAndFlights(driver, airports, flights):
    GraphRepository(driver).save_airports(airports)
    GraphRepository(driver).save_flights(flights)
    print("Airports and flights populated!")


driver = get_neo4j_driver()

# # GraphRepository(driver).clearGraph()

# airports = getActiveAirports()

# # baseAirports = ["DUB", "SNN", "NOC"]
# # baseAirports = ["SNN", "NOC"]
# # baseAirports = ["SNN"]
# baseAirports = ["DUB", "SNN"]

# desinations = set()

# GraphRepository(driver).save_airports(airports)
# for aiport in baseAirports:
#     flights = getDestinationsForAirport(aiport, airports)
#     GraphRepository(driver).save_flights(flights)
#     for flight in flights:
#         desinations.add(flight.origin.code)

# def get_airports_by_codes(airport_codes, airports):
#     return [airport for airport in airports if airport.code in airport_codes]

# airport_objects = get_airports_by_codes(desinations, airports)

# distances = distanceForEachAirport(airport_objects)

# GraphRepository(driver).save_distances(distances)

origin_airports = ["SNN"]

# r1_dates = [
#     date(2026, 2, 6),  # First Friday in February
#     date(2026, 2, 13), # Second Friday in February
#     date(2026, 2, 20), # Third Friday in February
#     date(2026, 2, 27)  # Fourth Friday in February
# ]
# r2_dates = [
#     date(2026, 2, 8),  # First Sunday in February
#     date(2026, 2, 15), # Second Sunday in February
#     date(2026, 2, 22), # Third Sunday in February
#     date(2026, 3, 1)  # Fourth Sunday in February
# ]\

r1_dates = [date(2026, 3, 25)]
r2_dates = [date(2026, 3, 29)]

lengths_of_stay = [2, 3, 4, 5, 6]  # Length of stay in days (e.g., 3 days, 4 days)
blacklist_countries = [
    "Ireland",
    "Poland",
    # "United Kingdom",
]  # Exclude destinations in Ireland and Spain

# Run the query
result = GraphRepository(driver).query_flights(
    origin_arrival_airports=origin_airports,
    origin_departure_airports=origin_airports,
    r1_dates=r1_dates,
    r2_dates=r2_dates,
    lengths_of_stay=lengths_of_stay,
    blacklist_countries=blacklist_countries,
    max_distance=100,
)

# print(result)

trips = build_trips_from_neo4j_results(result, adults=1)

# Print the result
# for row in result:
#     print(row)

print("Trips built:", len(trips))
for trip in trips:
    print(trip)
