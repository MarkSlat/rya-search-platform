from datetime import datetime
import math
from typing import Dict, List

import requests

from src.models.landDistance import landDistance
from src.models.airport import Airport
from src.models.neo4jResult import Neo4jResultFormatted
from src.models.trip import Trip
from src.ryanairApi import getAdvFlights

@staticmethod
def haversine(lat1, lon1, lat2, lon2) -> float:
    # Radius of the Earth in kilometers
    R = 6371.0

    # Convert latitude and longitude from degrees to radians
    lat1 = math.radians(lat1)
    lon1 = math.radians(lon1)
    lat2 = math.radians(lat2)
    lon2 = math.radians(lon2)

    # Difference in coordinates
    dlat = lat2 - lat1
    dlon = lon2 - lon1

    # Haversine formula
    a = math.sin(dlat / 2)**2 + math.cos(lat1) * math.cos(lat2) * math.sin(dlon / 2)**2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))

    # Distance in kilometers
    distance = R * c

    return distance

@staticmethod
def distanceForEachAirport(airports: List[Airport]) -> List[landDistance]:
    distances: List[landDistance] = []
    
    for origin_airport in airports:
        
        for destination_airport in airports:
            if origin_airport == destination_airport:
                continue
            
            distances.append(
                        landDistance(
                            origin=origin_airport,
                            destination=destination_airport,
                            distance=haversine(origin_airport.latitude, origin_airport.longitude, destination_airport.latitude, destination_airport.longitude)
                        )
                    )
        
    return distances

def neo4j_date_to_str(d) -> str:
    """Convert neo4j.time.Date → YYYY-MM-DD"""
    return f"{d.year:04d}-{d.month:02d}-{d.day:02d}"


def build_trips_from_neo4j_results(
    results: List[Neo4jResultFormatted],
    adults: int = 1
) -> List[Trip]:

    trips: List[Trip] = []

    for result in results:
        outboundflights = getAdvFlights(
            adult=adults,
            departDate=neo4j_date_to_str(result.origin_departure_date),
            origin_airport=result.origin_departure_airport_code,
            destination_airport=result.destination_arrival_airport_code,
        )
        
        returnflights = getAdvFlights(
            adult=adults,
            departDate=neo4j_date_to_str(result.destination_departure),
            origin_airport=result.destination_departure_airport_code,
            destination_airport=result.origin_arrival_airport_code,
        )
        
        for outbound in outboundflights:
            for ret in returnflights:
                fare = None
                if outbound.fare is not None and ret.fare is not None:
                    fare = outbound.fare + ret.fare
                    
                # if outbound.destinationName == destinationName
                
                

                trip = Trip(
                    destination=outbound.destinationName,
                    originDepartureAirportName=result.origin_departure_airport_code,
                    destinationArrivalAirportName=result.destination_arrival_airport_code,
                    destinationDepartureAirportName=result.destination_departure_airport_code,
                    originArrivalAirportName=result.origin_arrival_airport_code,
                    originDepartureTime=result.origin_departure_date,
                    destinationDepartureTime=result.destination_departure,
                    fullFare=fare,
                    distance=result.travel_distance_km
                )

                trips.append(trip)

        # trip = Trip(
        #     destination=result.destination_arrival_airport_code,
        #     originDepartureAirportName=result.origin_departure_airport_code,
        #     destinationArrivalAirportName=result.destination_arrival_airport_code,
        #     destinationDepartureAirportName=result.destination_departure_airport_code,
        #     originArrivalAirportName=result.origin_arrival_airport_code,
        #     originDepartureTime=result.origin_departure_date,
        #     destinationDepartureTime=result.destination_departure,
        #     fullFare=fare,
        #     distance=result.travel_distance_km
        # )

        # trips.append(trip)


    return trips

