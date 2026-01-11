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
GET_CURRENCY_EXCHANGE_RATE_URL = "https://api.exchangerate-api.com/v4/latest/{from_currency}"

def get_exchange_rate(from_currency: str, to_currency: str) -> float:
    """
    Fetch exchange rate from one currency to another.
    You can use a free API like exchangerate-api.com or similar.
    """
    if from_currency == to_currency:
        return 1.0
    
    # Example using exchangerate-api.com (free tier available)
    url = GET_CURRENCY_EXCHANGE_RATE_URL.format(from_currency=from_currency)
    response = requests.get(url)
    response.raise_for_status()
    data = response.json()
    
    if to_currency not in data.get("rates", {}):
        raise ValueError(f"Currency {to_currency} not found in exchange rates")
    
    return data["rates"][to_currency]


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

def getAdvFlights(
    adult: int, 
    departDate: str, 
    origin_airport: str, 
    destination_airport: str,
    currency: str = "EUR"
) -> List[AdvFlysTo]:
    url = GET_FARE_FOR_NO_ADULTS_URL.format(
        adult=adult,
        departDate=departDate,
        origin=origin_airport,
        destination=destination_airport
    )
    
    response = requests.get(url)
    response.raise_for_status()
    data = response.json()
    
    # Get the response currency
    response_currency = data.get("currency", "EUR")
    
    # Determine if conversion is needed
    needs_conversion = response_currency != currency
    conversion_rate = 1.0
    
    if needs_conversion:
        # Fetch conversion rate
        try:
            conversion_rate = get_exchange_rate(response_currency, currency)
            print(f"Converting from {response_currency} to {currency} at rate {conversion_rate}")
        except Exception as e:
            print(f"Warning: Could not fetch exchange rate. Using original currency {response_currency}. Error: {e}")
            needs_conversion = False
    
    flights_list: List[AdvFlysTo] = []
    trips = data.get("trips", [])
    
    
    originName = trips[0].get("originName", "")
    destinationName = trips[0].get("destinationName", "")
    
    originName = originName.strip()
    destinationName = destinationName.strip()
    
    for trip in trips:
        for trip_date in trip.get("dates", []):
            for flight in trip_date.get("flights", []):
                segment = flight["segments"][0]  # first segment (direct flight)
                
                fare_amount = None
                fares = flight.get("regularFare", {}).get("fares", [])
                if fares:
                    fare_amount = fares[0].get("amount")
                    # Apply conversion if needed
                    if fare_amount is not None and needs_conversion:
                        fare_amount = round(fare_amount * conversion_rate, 2)
                
                # Parse departure and arrival datetime
                departure_dt = datetime.fromisoformat(segment["time"][0]) if segment.get("time") else None
                arrival_dt = datetime.fromisoformat(segment["time"][1]) if segment.get("time") else None

                flights_list.append(
                    AdvFlysTo(
                        origin=origin_airport,
                        destination=destination_airport,
                        originName=originName,
                        destinationName=destinationName,
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
            )
            flys_to_list.append(flys_to)

    return flys_to_list