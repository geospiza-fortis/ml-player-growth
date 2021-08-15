# player growth

See [this thread](https://forum.maplelegends.com/index.php?threads/exploring-player-growth-via-rankings-page.39996) for analysis and links to pre-scraped data.

## scrape log

Please be responsible when using the scripts.

```bash
scrapy runspider scripts/scrape_ranking.py -a category=islander -o data/islander_ranking_20210521.json
scrapy runspider scripts/scrape_ranking.py -a category=magician -o data/magician_ranking_20210521.json

# d'oh, I forgot to add levels...
scrapy runspider scripts/scrape_levels.py -a ranking=data/islander_ranking_20210521.json -o data/islander_levels_20210521.json

scrapy runspider scripts/scrape_levels.py -a ranking=data/magician_ranking_20210521.json -o data/magician_levels_20210521.json

# 2021-07-31 full scrape
scrapy runspider scripts/scrape_ranking.py -a category=all -o data/all_ranking_20210731.json

# had to stop, trying to figure out how to restart...

scrapy runspider scripts/scrape_ranking.py -a category=all -a page_offset=14506 -o data/all_ranking_20210731.json -s JOBDIR=data/crawl/all_ranking_20210731

# and another scrape to cover up missing rankings, hardcoded value
scrapy runspider scripts/scrape_ranking.py -a category=all -o data/all_ranking_20210731.json

scrapy runspider scripts/scrape_levels.py -a ranking=data/all_ranking_20210731_deduped.json -o data/all_levels_20210801.json -s JOBDIR=data/crawl/all_levels_20210801
```

```
{'downloader/exception_count': 4,
 'downloader/exception_type_count/twisted.internet.error.TimeoutError': 4,
 'downloader/request_bytes': 64043799,
 'downloader/request_count': 201518,
 'downloader/request_method_count/GET': 201518,
 'downloader/response_bytes': 1570777540,
 'downloader/response_count': 201514,
 'downloader/response_status_count/200': 201514,
 'elapsed_time_seconds': 66826.864186,
 'feedexport/success_count/FileFeedStorage': 1,
 'finish_reason': 'finished',
 'finish_time': datetime.datetime(2021, 8, 3, 0, 35, 56, 568529),
 'httpcompression/response_bytes': 5730961738,
 'httpcompression/response_count': 201514,
 'item_scraped_count': 6768398,
 'log_count/DEBUG': 6969916,
 'log_count/INFO': 1124,
 'response_received_count': 201514,
 'retry/count': 4,
 'retry/reason_count/twisted.internet.error.TimeoutError': 4,
 'scheduler/dequeued': 201518,
 'scheduler/dequeued/disk': 201518,
 'scheduler/enqueued': 201518,
 'scheduler/enqueued/disk': 201518,
 'start_time': datetime.datetime(2021, 8, 2, 6, 2, 9, 704343)}
 ```




