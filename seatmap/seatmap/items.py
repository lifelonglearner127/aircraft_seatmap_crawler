# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

from dataclasses import dataclass, field
from typing import Optional


@dataclass
class SeatMap:
    airline_code: Optional[str] = field(default=None)
    airline_name: Optional[str] = field(default=None)
    aircraft_code: Optional[str] = field(default=None)
    layout: Optional[str] = field(default=None)
    aircraft_description: Optional[str] = field(default=None)
    seat_map: Optional[str] = field(default=None)
    traveler_photos: Optional[str] = field(default=None)
    seat_map_key: Optional[str] = field(default=None)
    overview: Optional[str] = field(default=None)
    seats_file: Optional[str] = field(default=None)
