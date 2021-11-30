from scrapy.crawler import CrawlerProcess
from scrapy.utils.project import get_project_settings
from gainers import GainersSpider
 
 
process = CrawlerProcess(get_project_settings())
process.crawl(GainersSpider)
process.start()