from dataclasses import dataclass
from typing import Dict, List, Optional
from datetime import datetime

from src.models.airport import Airport
from src.models.bscFlysTo import BscFlysTo

@dataclass
class AdvFlysTo:
    origin: str
    destination: str
    departureTime: datetime = None
    arrivalTime: datetime = None
    fare: float = None
    flightNumber: str = None
    duration: str = None