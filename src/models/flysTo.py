from dataclasses import dataclass
from typing import Dict, List, Optional
from datetime import datetime

from src.models.airport import Airport

@dataclass
class FlysTo:
    origin: Airport
    destination: Airport
    date: datetime.date
    depatureTime: Optional[str] = None
    arrivalTime: Optional[str] = None
    fare: Optional[float] = None
    
    def to_dict(self) -> Dict:
        return {
            "date": self.date.isoformat(),
            "departureTime": self.departureTime,
            "arrivalTime": self.arrivalTime,
            "fare": self.fare,
        }