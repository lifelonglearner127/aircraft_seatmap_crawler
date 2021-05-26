# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html


import csv

# useful for handling different item types with a single interface
from itemadapter import ItemAdapter


class SeatmapPipeline:
    def open_spider(self, spider):
        self.csvfile = open("eggs.csv", "a", newline="")
        self.seatmap_writer = csv.writer(self.csvfile, delimiter=";")

    def close_spider(self, spider):
        self.csvfile.close()

    def process_item(self, item, spider):
        line = ItemAdapter(item).asdict()
        self.seatmap_writer.writerow(
            [
                line["airline_code"],
                line["aircraft_code"],
                line["layout"],
                line["seat_map"],
                line["seat_map_key"],
                line["overview"],
            ]
        )
        return item
