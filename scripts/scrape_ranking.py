import scrapy
import datetime
import requests
from bs4 import BeautifulSoup
import math


def parse_total(resp):
    soup = BeautifulSoup(resp.text)
    ranking_table = soup.find(id="rankingTable")
    return int(ranking_table.p.b.getText())


def get_ranking(page, category):
    url = f"https://maplelegends.com/ranking/{category}?page={page}"
    return requests.get(url)


class MapleLegendsRankingSpider(scrapy.Spider):
    name = "ranking"
    dont_redirect = True
    handle_httpstatus_list = [301, 302]
    custom_settings = {
        "DOWNLOAD_DELAY": 0.25,
        "CONCURRENT_REQUESTS_PER_DOMAIN": 2,
    }

    def __init__(self, pages=1, page_offset="0", category="all", *args, **kwargs):
        super(MapleLegendsRankingSpider, self).__init__(*args, **kwargs)
        first = get_ranking(1, category)
        total = parse_total(first)
        print(f"{total} rows")
        self.start_urls = [
            f"https://maplelegends.com/ranking/{category}?page={page+1}"
            for page in range(math.ceil(total / 5))
            # for starting off again
            if page >= int(page_offset)
        ]

    # useful link: https://stackoverflow.com/a/43497095
    def parse(self, response):
        category = response.url.split("/")[-1].split("?")[0]
        for row in response.xpath("//tr")[1:]:
            level = int(row.xpath("td[6]/b/text()").get())
            href = row.xpath("td[4]/a/@href").get()
            yield dict(
                timestamp=datetime.datetime.utcnow().isoformat(),
                category=category,
                rank=int(row.xpath("td[1]/b/text()").get()),
                name=row.xpath("td[3]//a/text()").get(),
                guild=row.xpath("td[3]/a/text()").get().strip(),
                job=row.xpath("td[4]//img/@src").get().split("/")[-1].split(".")[0],
                specialization=href.split("/")[-1] if href else None,
                mastery=row.xpath("td[4]//text()").get().lower().strip(),
                fame=int(row.xpath("td[5]/b/text()").get()),
                # damn... this was missing in the first dump
                level=level,
            )
