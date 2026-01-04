from dataclasses import dataclass
from typing import Dict

from src.models.airport import Airport


@dataclass
class landDistance:
    origin: Airport
    destination: Airport
    distance: float
    
    def to_dict(self) -> Dict:
        return {
            "distance": self.distance,
        }