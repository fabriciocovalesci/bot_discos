from multiprocessing import Process
import os
from datetime import datetime
from scrapy.crawler import CrawlerRunner
from scrapy.utils.project import get_project_settings
from scrapy.utils.log import configure_logging
from twisted.internet import reactor
from apscheduler.schedulers.blocking import BlockingScheduler
# from bot_ml.bot_ml.spiders.discos_spider import DiscosSpider

from time import sleep


print(get_project_settings())

from scrapy.crawler import CrawlerProcess
from scrapy.utils.project import get_project_settings

process = CrawlerProcess(get_project_settings())

process.crawl('bot_ml')
process.start() 