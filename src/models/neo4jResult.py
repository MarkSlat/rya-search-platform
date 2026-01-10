from dataclasses import dataclass
from datetime import datetime
from typing import Optional


@dataclass
class Neo4jResultFormatted:
    origin_departure_airport_code: str
    destination_arrival_airport_code: str
    destination_departure_airport_code: str
    origin_arrival_airport_code: str
    origin_departure_date: datetime.date
    destination_departure: datetime.date
    travel_distance_km: Optional[float] = None