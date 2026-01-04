import time
from typing import List
from neo4j import GraphDatabase

from src.graphRepository import GraphRepository
from src.models.airport import Airport
from src.ryanairApi import getActiveAirports, getDestinationsForAirport
from src.utils import distanceForEachAirport


def get_neo4j_driver(uri="bolt://localhost:7687", user="neo4j", password="test1234"):
    return GraphDatabase.driver(uri, auth=(user, password))


def populateAirportsAndFlights(driver, airports, flights):
    GraphRepository(driver).save_airports(airports)
    GraphRepository(driver).save_flights(flights)
    print("Airports and flights populated!")


driver = get_neo4j_driver()

GraphRepository(driver).clearGraph()

airports = getActiveAirports()

# baseAirports = ["DUB", "SNN", "NOC"]
# baseAirports = ["SNN", "NOC"]
baseAirports = ["SNN"]

desinations = set() 

GraphRepository(driver).save_airports(airports)
for aiport in baseAirports:
    flights = getDestinationsForAirport(aiport, airports)
    GraphRepository(driver).save_flights(flights)
    for flight in flights:
        desinations.add(flight.origin.code)

def get_airports_by_codes(airport_codes, airports):
    return [airport for airport in airports if airport.code in airport_codes]

airport_objects = get_airports_by_codes(desinations, airports)

distances = distanceForEachAirport(airport_objects)

GraphRepository(driver).save_distances(distances)

