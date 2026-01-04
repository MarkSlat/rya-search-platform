import math
from typing import List

from src.models.landDistiance import landDistiance
from src.models.airport import Airport

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
def distanceForEachAirport(airports: List[Airport]) -> List[landDistiance]:
    distances: List[landDistiance] = []
    
    for origin_airport in airports:
        
        for destination_airport in airports:
            if origin_airport == destination_airport:
                continue
            
            distances.append(
                        landDistiance(
                            origin=origin_airport,
                            destination=destination_airport,
                            distinace=haversine(origin_airport.latitude, origin_airport.longitude, destination_airport.latitude, destination_airport.longitude)
                        )
                    )
        
    return distances