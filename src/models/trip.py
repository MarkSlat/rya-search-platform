from dataclasses import dataclass
from typing import Dict, List, Optional
from datetime import datetime

from src.models.airport import Airport

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
    # transferAirport: Optional[str] = None
    # departureTime: Optional[datetime] = None
    # arrivalTime: Optional[datetime] = None