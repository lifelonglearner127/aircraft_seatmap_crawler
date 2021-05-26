import logging

import scrapy
from seatmap.items import SeatMap
from seatmap.loaders import SeatMapLoader

logger = logging.getLogger(__name__)


class SeatMapSpider(scrapy.Spider):
    name = "seatmaps"
    start_urls = ["https://seatguru.com/browseairlines/browseairlines.php"]

    def parse(self, response):
        for airline_detail_page in response.xpath("//div[@class='browseAirlines']//a/@href").getall()[:1]:
            yield response.follow(airline_detail_page, callback=self.parse_airline)

    def parse_airline(self, response):
        airline_code = response.xpath("//div[@class='content-header']//h1/text()").get()
        airline_code = airline_code[-3:-1]
        logger.error(f"Airline {airline_code}")
        for aircraft_detail_page in response.xpath("//div[@class='aircraft_seats']/a/@href").getall()[:1]:
            logger.error(f"Airline {aircraft_detail_page}")
            yield response.follow(
                aircraft_detail_page, callback=self.parse_aircraft, meta={"airline_code": airline_code}
            )

    def parse_aircraft(self, response):
        airline_code = response.meta.get("airline_code")
        air_craft_description = response.xpath("//div[contains(@class, 'content-header')]//h1/text()").get()
        air_craft_code, layout = air_craft_description.split(")")
        air_craft_code = air_craft_code[-3:]
        seatmap = SeatMapLoader(item=SeatMap(), response=response)
        seatmap.add_value("airline_code", airline_code)
        seatmap.add_value("aircraft_code", air_craft_code)
        seatmap.add_value("layout", layout)
        seatmap.add_xpath("seat_map", "//img[@class='plane']/@src")
        seatmap.add_xpath("seat_map_key", "//ul[@class='legend']/li//text()")
        seatmap.add_xpath("overview", "//div[@class='tips-box']/p//text()")
        return seatmap.load_item()
