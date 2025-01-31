from multiprocessing import Process
import os
from datetime import datetime
from bot_ml.bot_ml.spiders.discos_spider import DiscosSpider
from scrapy.crawler import CrawlerRunner
from scrapy.crawler import CrawlerProcess
from scrapy.crawler import Crawler
from scrapy.settings import Settings
from twisted.internet import reactor
from scrapy.utils.project import get_project_settings
from scrapy.utils.log import configure_logging
from twisted.internet import reactor
from apscheduler.schedulers.blocking import BlockingScheduler

from utils import *
from time import sleep


class CrawlerRunnerProcess(Process):
    def __init__(self, spider):
        Process.__init__(self)
        self.runner = CrawlerRunner(get_project_settings())
        self.spider = spider

    def run(self):
        deferred = self.runner.crawl(self.spider)
        deferred.addBoth(lambda _: reactor.stop())
        reactor.run(installSignalHandlers=False)

# The wrapper to make it run multiple spiders, multiple times
def run_spider(spider):
    try:
        crawler = CrawlerRunnerProcess(spider)
        crawler.start()
        crawler.join()
    except KeyboardInterrupt as err:
        print(f"Parou {err}")
        os._exit()

def job_function():
    print(datetime.now().time().strftime('%H:%M'))


if __name__ == '__main__': 
    os.environ['TZ'] = 'America/Sao_Paulo'    
    configure_logging()
    # scheduler = BlockingScheduler(timezone="America/Sao_Paulo")
    # # scheduler.add_job(job_function, 'cron', day_of_week='mon-sat',  hour='16-17', minute='5,15,25,35,45,55', timezone="America/Sao_Paulo")
    # scheduler.add_job(run_spider, 'cron', args=[Loterias], day_of_week='mon-sat',  hour='21-23', minute='5,15,25,35,45,55', timezone="America/Sao_Paulo")
    # scheduler.start()
    # run_spider(DiscosSpider)

    # spider = DiscosSpider()
    # crawler = Crawler(Settings())
    # crawler.configure()
    # crawler.crawl(spider)
    # crawler.start()
    # reactor.run()
    settings = get_project_settings()

    # Configurações personalizadas para evitar bloqueios
    settings.set("USER_AGENT", "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36")
    settings.set("DOWNLOAD_DELAY", 2)  # Atraso de 2 segundos entre as requisições
    settings.set("AUTOTHROTTLE_ENABLED", True)  # Habilita o AutoThrottle
    settings.set("AUTOTHROTTLE_START_DELAY", 5)  # Atraso inicial de 5 segundos
    settings.set("AUTOTHROTTLE_MAX_DELAY", 60)  # Atraso máximo de 60 segundos
    settings.set("RETRY_TIMES", 3)  # Número de tentativas em caso de falha
    settings.set("RETRY_HTTP_CODES", [500, 502, 503, 504, 403, 408]) 
    process = CrawlerProcess()
    process.crawl(DiscosSpider)
    process.start()


