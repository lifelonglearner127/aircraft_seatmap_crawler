from itemloaders.processors import Join, MapCompose, TakeFirst
from scrapy.loader import ItemLoader


class SeatMapLoader(ItemLoader):
    default_output_processor = TakeFirst()
    airline_code_in = MapCompose(str.strip)
    aircraft_code_in = MapCompose(str.strip)
    layout_in = MapCompose(str.strip)
    overview_in = MapCompose(str.strip)
    seat_map_key_out = Join(separator=",")
    traveler_photos_out = Join(separator=",")
