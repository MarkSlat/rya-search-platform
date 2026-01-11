from dataclasses import dataclass
from typing import Dict

@dataclass
class Airport:
    code: str
    name: str
    cityName: str
    countryName: str
    latitude: float
    longitude: float
    base: bool = False
    
    def to_dict(self) -> Dict:
        return {
            "code": self.code,
            "name": self.name,
            "cityName": self.cityName,
            "countryName": self.countryName,
            "latitude": self.latitude,
            "longitude": self.longitude,
            "base": self.base,
        }
