import time
from typing import List
from neo4j import GraphDatabase

from src.models.graphRepository import GraphRepository
from src.models.flysTo import FlysTo
from src.models.airport import Airport
from src.ryanairApi import getActiveAirports, getDestinationsForAirport


def get_neo4j_driver(uri="bolt://localhost:7687", user="neo4j", password="test1234"):
    return GraphDatabase.driver(uri, auth=(user, password))


def populateAirportsAndFlights(driver, airports, flights):
    GraphRepository(driver).save_airports(airports)
    GraphRepository(driver).save_flights(flights)
    print("Airports and flights populated!")


driver = get_neo4j_driver()

# clearGraph(driver)

# GraphRepository(driver).clearGraph()

airports = getActiveAirports()
flights = getDestinationsForAirport("SNN", airports)
populateAirportsAndFlights(driver, airports, flights)
flights = getDestinationsForAirport("NOC", airports)

GraphRepository(driver).save_flights(flights)
# start = time.time()

# end = time.time()
# print(end - start)
# print(flights)

# start = time.time()
# flights = getDestinationsForAirport("DUB", airports)
# end = time.time()
# print(end - start)

# # Connect to Neo4j
# driver = GraphDatabase.driver("bolt://localhost:7687", auth=("neo4j", "test1234"))

# with driver.session() as session:
#     # Create nodes and a relationship
#     session.run("""
#         CREATE (a:Person {name: 'Alice'})
#         CREATE (b:Person {name: 'Bob'})
#         CREATE (a)-[:KNOWS]->(b)
#     """)

#     # Query nodes
#     result = session.run("MATCH (a:Person)-[:KNOWS]->(b:Person) RETURN a.name, b.name")
#     for record in result:
#         print(record["a.name"], "knows", record["b.name"])

