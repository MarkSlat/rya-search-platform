from datetime import datetime
import math
from typing import Dict, List

from src.models.landDistance import landDistance
from src.models.airport import Airport
from src.models.trip import Trip
from src.ryanairApi import getFareForTrip

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
    results: List[Dict],
    adults: int = 1
) -> List[Trip]:

    trips: List[Trip] = []

    for row in results:
        origin = row["origin"]
        destination = row["destination"]
        outbound_date_str = f"{row['outboundDate'].year:04d}-{row['outboundDate'].month:02d}-{row['outboundDate'].day:02d}"
        outbound_date = datetime.fromisoformat(outbound_date_str).date()

        transfer_airport = row.get("transferAirport")
        land_distance = row.get("landDistance")

        # -------------------------
        # DIRECT FLIGHTS
        # -------------------------
        if not transfer_airport:
            flights = getFareForTrip(
                adult=adults,
                departDate=outbound_date_str,
                origin_airport=origin,
                destination_airport=destination
            )

            for f in flights:
                if f.fare is None:
                    continue

                trips.append(
                    Trip(
                        origin=origin,
                        destination=destination,
                        date=outbound_date,
                        originDepartureTime=f.departureTime,
                        destinationArrivalTime=f.arrivalTime,
                        fullFare=f.fare,
                        transfer=False,
                        distance=None
                    )
                )

        # -------------------------
        # NON-TEMPORAL "TRANSFER"
        # -------------------------
        else:
            leg1_flights = getFareForTrip(
                adult=adults,
                departDate=outbound_date_str,
                origin_airport=origin,
                destination_airport=transfer_airport
            )

            leg2_flights = getFareForTrip(
                adult=adults,
                departDate=outbound_date_str,
                origin_airport=transfer_airport,
                destination_airport=destination
            )

            for f1 in leg1_flights:
                if f1.fare is None:
                    continue

                for f2 in leg2_flights:
                    if f2.fare is None:
                        continue

                    trips.append(
                        Trip(
                            origin=origin,
                            destination=destination,
                            date=outbound_date,
                            originDepartureTime=f1.departureTime,
                            originArrivalTime=f1.arrivalTime,
                            destinationDepartureTime=f2.departureTime,
                            destinationArrivalTime=f2.arrivalTime,
                            fullFare=f1.fare + f2.fare,
                            transfer=True,
                            distance=land_distance
                        )
                    )

    # -------------------------
    # SORT CHEAPEST FIRST
    # -------------------------
    trips.sort(key=lambda t: math.inf if t.fullFare is None else t.fullFare)

    return trips