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
```
