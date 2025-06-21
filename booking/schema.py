from typing import Literal, Optional
from ninja import Schema, ModelSchema
from .models import Flight

class FlightSchemaIn(Schema):
    from_city: str
    to_city: str
    departure_date: str
    arrival_date: Optional[str] = None
    boarding_class: Literal['economy', 'business', 'first'] = 'economy'
    trip_type: Literal['oneway', 'return', 'multi'] = 'oneway'
    passenger: int

class VisaSchemaIn(Schema):
    visa_type: Literal['student', 'tourist', 'work']
    country: str
    nationality: str
    travel_date: str
    reason: str
    duration: str
    confirm: bool = False
    