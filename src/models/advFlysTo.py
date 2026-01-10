from dataclasses import dataclass
from datetime import datetime


@dataclass
class AdvFlysTo:
    origin: str
    destination: str
    originName: str = None
    destinationName: str = None
    departureTime: datetime = None
    arrivalTime: datetime = None
    fare: float = None
    flightNumber: str = None
    duration: str = None