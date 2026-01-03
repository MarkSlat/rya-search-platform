from datetime import datetime
from typing import List
import requests

from src.models.airport import Airport
from src.models.flysTo import FlysTo


GET_ALL_ACTIVE_AIRPORTS_URL = "https://www.ryanair.com/api/views/locate/5/airports/en/active"
GET_ALL_ROUTES_FOR_AIRPORT_URL = "https://www.ryanair.com/api/views/locate/searchWidget/routes/en/airport/{airportCode}"
GET_DATES_FOR_FLIGHT_URL = "https://www.ryanair.com/api/farfnd/v4/oneWayFares/{origin}/{destination}/availabilities"
GET_FARE_FOR_NO_ADULTS_URL ="https://www.ryanair.com/api/booking/v4/en-gb/availability?ADT={adult}&DateOut={departDate}&Destination={destination}&Origin={origin}&IncludeConnectingFlights=false&RoundTrip=false&ToUs=AGREED"


def getActiveAirports() -> List[Airport]:
    response = requests.get(GET_ALL_ACTIVE_AIRPORTS_URL)
    response.raise_for_status()
    
    data = response.json()

    airports: List[Airport] = []

    for item in data:
        airport = Airport(
            code=item["code"],
            name=item["name"],
            cityName=item["city"]["name"],
            countryName=item["country"]["name"],
            latitude=item["coordinates"]["latitude"],
            longitude=item["coordinates"]["longitude"]
        )
        airports.append(airport)
    
    return airports

def getFareForTrip(adult: int, departDate: str, origin: str, destination: str) -> List[FlysTo]:
    print()

def getDestinationsForAirport(airportCode: str, airportList: List[Airport], getFare: bool) -> List[FlysTo]:
    # Build internal lookup by code
    airports = {airport.code: airport for airport in airportList}

    url = GET_ALL_ROUTES_FOR_AIRPORT_URL.format(airportCode=airportCode)
    response = requests.get(url)
    response.raise_for_status()
    data = response.json()

    flys_to_list: List[FlysTo] = []

    origin_airport = airports.get(airportCode)
    if not origin_airport:
        raise ValueError(f"Airport {airportCode} not found in the provided list")

    for item in data:
        dest_data = item["arrivalAirport"]
        dest_code = dest_data["code"]

        destination_airport = airports.get(dest_code)
        if not destination_airport:
            # Create destination Airport if missing
            # destination_airport = Airport(
            #     code=dest_code,
            #     name=dest_data["name"],
            #     cityName=dest_data["city"]["name"],
            #     countryName=dest_data["country"]["name"],
            #     latitude=dest_data["coordinates"]["latitude"],
            #     longitude=dest_data["coordinates"]["longitude"],
            #     flysTo=[]
            # )
            # airports[dest_code] = destination_airport
            # airportList.append(destination_airport)  # keep the list updated
            print("WARNING aiport not in list")
            
        url = GET_DATES_FOR_FLIGHT_URL.format(origin=origin_airport.code, destination=destination_airport.code)
        response = requests.get(url)
        response.raise_for_status()
        data = response.json()
        
        for item in data:
            # Create FlysTo object
            flys_to = FlysTo(
            origin=origin_airport,
            destination=destination_airport,
            date=datetime.strptime(item, "%Y-%m-%d").date()
        )
        flys_to_list.append(flys_to)
        
        temp_orgin = destination_airport # Reverse
        temp_destination = origin_airport # Reverse
        
        url = GET_DATES_FOR_FLIGHT_URL.format(origin=temp_orgin.code, destination=temp_destination.code)
        response = requests.get(url)
        response.raise_for_status()
        data = response.json()
        
        for item in data:
            # Create FlysTo object            
            flys_to = FlysTo(
            origin=temp_orgin,
            destination=temp_destination,
            date=datetime.strptime(item, "%Y-%m-%d").date(),
            departureTime=None,
            arrivalTime=None,
            fare=None
        )
        flys_to_list.append(flys_to)

    return flys_to_list

    
    