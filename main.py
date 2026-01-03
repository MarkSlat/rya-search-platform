import time
from typing import List
from neo4j import GraphDatabase

from src.models.flysTo import FlysTo
from src.models.airport import Airport
from src.ryanairApi import getActiveAirports, getDestinationsForAirport


def get_neo4j_driver(uri="bolt://localhost:7687", user="neo4j", password="test1234"):
    return GraphDatabase.driver(uri, auth=(user, password))


def clearGraph(driver):
    with driver.session() as session:
        session.run("MATCH (n) DETACH DELETE n")
    print("Graph cleared!")


def populateAirportsAndFlights(driver, airports: List[Airport], flights: List[FlysTo]):
    with driver.session() as session:
        # Create airport nodes
        for airport in airports:
            session.run(
                """
                MERGE (a:Airport {code: $code})
                SET a.name = $name,
                    a.cityName = $cityName,
                    a.countryName = $countryName,
                    a.latitude = $latitude,
                    a.longitude = $longitude
                """,
                code=airport.code,
                name=airport.name,
                cityName=airport.cityName,
                countryName=airport.countryName,
                latitude=airport.latitude,
                longitude=airport.longitude
            )

        # Create flight relationships
        for flight in flights:
            session.run(
                """
                MATCH (origin:Airport {code: $originCode})
                MATCH (dest:Airport {code: $destCode})
                MERGE (origin)-[r:FLYS_TO]->(dest)
                SET r.date = $date,
                    r.departureTime = $depTime,
                    r.arrivalTime = $arrTime,
                    r.fare = $fare
                """,
                originCode=flight.origin.code,
                destCode=flight.destination.code,
                date=flight.date.isoformat(),
                depTime=flight.depatureTime,
                arrTime=flight.arrivalTime,
                fare=flight.fare
            )
    print("Airports and flights populated!")


driver = get_neo4j_driver()

# clearGraph(driver)



airports = getActiveAirports()
flights = getDestinationsForAirport("SNN", airports)
populateAirportsAndFlights(driver, airports, flights)

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

