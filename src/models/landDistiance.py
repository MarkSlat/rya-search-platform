from dataclasses import dataclass
from typing import Dict

from src.models.airport import Airport


@dataclass
class landDistiance:
    origin: Airport
    destination: Airport
    distinace: float
    
    def to_dict(self) -> Dict:
        return {
            "distinace": self.distinace,
        }