from dataclasses import dataclass
from typing import Optional
from datetime import datetime


@dataclass
class Trip:
    # origin: str
    destination: str
    # date: datetime.date
    originDepartureAirportName: str = None
    destinationArrivalAirportName: str = None
    destinationDepartureAirportName: str = None
    originArrivalAirportName: str = None
    originDepartureTime: datetime = None
    destinationArrivalTime: datetime = None
    destinationDepartureTime: datetime = None
    originArrivalTime: datetime = None
    fullFare: float = None
    transfer: bool = False
    distance:  Optional[float] = None
    originDepartureLat: Optional[float] = None
    originDepartureLon: Optional[float] = None
    destinationArrivalLat: Optional[float] = None
    destinationArrivalLon: Optional[float] = None
    destinationDepartureLat: Optional[float] = None
    destinationDepartureLon: Optional[float] = None
    originArrivalLat: Optional[float] = None
    originArrivalLon: Optional[float] = None

    # transferAirport: Optional[str] = None
    # departureTime: Optional[datetime] = None
    # arrivalTime: Optional[datetime] = None