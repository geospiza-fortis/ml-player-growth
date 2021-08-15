"""Get the leveling history."""
from pathlib import Path
import json
import scrapy


class MapleLegendsLevelingHistorySpider(scrapy.Spider):
    name = "leveling_history"
    dont_redirect = True
    handle_httpstatus_list = [301, 302]
    custom_settings = {
        "DOWNLOAD_DELAY": 0.25,
        "CONCURRENT_REQUESTS_PER_DOMAIN": 2,
    }

    def __init__(self, ranking, *args, **kwargs):
        super(MapleLegendsLevelingHistorySpider, self).__init__(*args, **kwargs)
        path = Path(ranking)
        if not path.exists():
            raise RuntimeError(f"{path} does not exist")
        data = json.loads(path.read_text())

        self.start_urls = [
            f"https://maplelegends.com/levels?name={row['name']}" for row in data
        ]

    def parse(self, response):
        for row in response.xpath("//tr")[1:]:
            yield dict(
                name=response.url.split("=")[-1],
                level=int(row.xpath("td[1]/text()").get()),
                timestamp=row.xpath("td[2]/text()").get(),
            )
