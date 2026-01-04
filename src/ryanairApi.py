from datetime import datetime
from typing import List
import requests

from src.models.advFlysTo import AdvFlysTo
from src.models.airport import Airport
from src.models.bscFlysTo import BscFlysTo


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

def getFareForTrip(adult: int, departDate: str, origin_airport: Airport, destination_airport: Airport) -> List[AdvFlysTo]:
    url = GET_FARE_FOR_NO_ADULTS_URL.format(
        adult=adult,
        departDate=departDate,
        origin=origin_airport.code,
        destination=destination_airport.code
    )
    
    response = requests.get(url)
    response.raise_for_status()
    data = response.json()
    
    # Check currency
    currency = data.get("currency", "EUR")
    if currency != "EUR":
        print(f"Warning: fare currency is {currency}, not EUR!")

    flights_list: List[AdvFlysTo] = []

    trips = data.get("trips", [])
    for trip in trips:
        for trip_date in trip.get("dates", []):
            date_obj = datetime.fromisoformat(trip_date["dateOut"].split("T")[0]).date()
            for flight in trip_date.get("flights", []):
                segment = flight["segments"][0]  # first segment (direct flight)
                
                fare_amount = None
                fares = flight.get("regularFare", {}).get("fares", [])
                if fares:
                    fare_amount = fares[0].get("amount")

                # Parse departure and arrival datetime
                departure_dt = datetime.fromisoformat(segment["time"][0]) if segment.get("time") else None
                arrival_dt = datetime.fromisoformat(segment["time"][1]) if segment.get("time") else None
                
                bscFlysTo = BscFlysTo(
                            origin=origin_airport,
                            destination=destination_airport,
                            date=date_obj,
                            )

                flights_list.append(
                    AdvFlysTo(
                        bscFlysTo=bscFlysTo,
                        departureTime=departure_dt,
                        arrivalTime=arrival_dt,
                        fare=fare_amount,
                        flightNumber=segment.get("flightNumber"),
                        duration=segment.get("duration")
                    )
                )

    return flights_list

def getDestinationsForAirport(airportCode: str, airportList: List[Airport]) -> List[BscFlysTo]:
    # Build internal lookup by code
    airports = {airport.code: airport for airport in airportList}

    url = GET_ALL_ROUTES_FOR_AIRPORT_URL.format(airportCode=airportCode)
    response = requests.get(url)
    response.raise_for_status()
    data = response.json()

    flys_to_list: List[BscFlysTo] = []

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
            #     BscFlysTo=[]
            # )
            # airports[dest_code] = destination_airport
            # airportList.append(destination_airport)  # keep the list updated
            print("WARNING aiport not in list")
            
        url = GET_DATES_FOR_FLIGHT_URL.format(origin=origin_airport.code, destination=destination_airport.code)
        response = requests.get(url)
        response.raise_for_status()
        data = response.json()
        
        for item in data:
            # Create BscFlysTo object
            flys_to = BscFlysTo(
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
            # Create BscFlysTo object            
            flys_to = BscFlysTo(
            origin=temp_orgin,
            destination=temp_destination,
            date=datetime.strptime(item, "%Y-%m-%d").date(),
            departureTime=None,
            arrivalTime=None,
            fare=None
            )
            flys_to_list.append(flys_to)

    return flys_to_list