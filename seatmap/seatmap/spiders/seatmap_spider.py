import scrapy
from seatmap.items import SeatMap
from seatmap.loaders import SeatMapLoader


class SeatMapSpider(scrapy.Spider):
    name = "seatmaps"
    start_urls = ["https://seatguru.com/browseairlines/browseairlines.php"]

    def parse(self, response):
        for airline_detail_page in response.xpath("//div[@class='browseAirlines']//a/@href").getall()[:1]:
            yield response.follow(airline_detail_page, callback=self.parse_airline)

    def parse_airline(self, response):
        airline_code = response.xpath("//div[@class='content-header']//h1/text()").get()
        airline_code = airline_code[-3:-1]
        for aircraft_detail_page in response.xpath("//div[@class='aircraft_seats']/a/@href").getall()[:2]:
            yield response.follow(
                aircraft_detail_page, callback=self.parse_aircraft, meta={"airline_code": airline_code}
            )

    def parse_aircraft(self, response):
        airline_code = response.meta.get("airline_code")
        aircraft_description = response.xpath("//div[contains(@class, 'content-header')]//h1/text()").get()
        if all(c in aircraft_description for c in ["(", ")"]):
            aircraft_code, layout = aircraft_description.split(")")
            aircraft_code = aircraft_code[-3:]
        else:
            aircraft_code = ""
            layout = ""

        seatmap = SeatMapLoader(item=SeatMap(), response=response)
        seatmap.add_value("airline_code", airline_code)
        seatmap.add_value("aircraft_code", aircraft_code)
        seatmap.add_value("aircraft_description", aircraft_description)
        seatmap.add_value("layout", layout)
        seatmap.add_xpath("seat_map", "//img[@class='plane']/@src")
        seatmap.add_xpath("seat_map_key", "//ul[@class='legend']/li//text()")
        seatmap.add_xpath("overview", "//div[@class='tips-box']/p//text()")
        gallery_link = response.xpath('//div[@class="aside-gallery-bottom"]//a[@class="view_gallery"]/@href').get()
        if gallery_link:
            yield response.follow(gallery_link, callback=self.parse_traveler_photos, meta={"seatmap": seatmap})
        else:
            yield seatmap.load_item()

    def parse_traveler_photos(self, response):
        seatmap = response.meta.get("seatmap")
        traveler_photos = response.xpath("//ul[@id='carousel']/li//img/@src").extract()
        seatmap.add_value("traveler_photos", traveler_photos)
        yield seatmap.load_item()
