from dataclasses import dataclass
from typing import Dict, List, Optional
from datetime import datetime

from src.models.airport import Airport

@dataclass
class FlysTo:
    origin: Airport
    destination: Airport
    date: datetime.date
    departureTime: Optional[datetime] = None
    arrivalTime: Optional[datetime] = None
    fare: Optional[float] = None
    flightNumber: Optional[str] = None
    duration: Optional[str] = None
    
    def to_dict(self) -> Dict:
        return {
            "date": self.date #.isoformat(),
            # "departureTime": self.departureTime,
            # "arrivalTime": self.arrivalTime,
            # "fare": self.fare,
            # "flightNumber": self.flightNumber,
            # "duration": self.duration
        }