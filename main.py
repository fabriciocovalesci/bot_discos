from multiprocessing import Process
import os
from datetime import datetime
from scrapy.crawler import CrawlerRunner
from scrapy.utils.project import get_project_settings
from scrapy.utils.log import configure_logging
from twisted.internet import reactor
from apscheduler.schedulers.blocking import BlockingScheduler
from bot_ml.bot_ml.spiders.discos_spider import DiscosSpider
from utils import *
from time import sleep


folder_path = get_specific_folder("resource")
csv_files = [f for f in os.listdir(folder_path) if f.endswith('.csv') and f.startswith('input')]

words = read_file_csv(csv_files, folder_path)


class CrawlerRunnerProcess(Process):
    def __init__(self, spider):
        super().__init__()
        self.spider = spider
        self.runner = CrawlerRunner(get_project_settings())

    def run(self):
        deferred = self.runner.crawl(self.spider_cls, search_query=self.search_query)
        deferred.addBoth(lambda _: reactor.stop())

        try:
            reactor.run(installSignalHandlers=False)
        except RuntimeError:
            print("Reactor já estava rodando.")


def run_spider(search_query):
    """Executa o scrapy para uma palavra específica"""
    try:
        crawler = CrawlerRunnerProcess(DiscosSpider, search_query)
        crawler.start()
        crawler.join()
    except KeyboardInterrupt as err:
        print(f"Execução interrompida: {err}")
        os._exit(1)


def job_function():
    print(f"Job executado às {datetime.now().time().strftime('%H:%M')}")
    run_spider(DiscosSpider)


if __name__ == '__main__':
    os.environ['TZ'] = 'America/Sao_Paulo'
    configure_logging()

    for word in words:
        print(f"🔍 Buscando por: {word}")
        sleep(5)
        run_spider(word.strip())

    # scheduler = BlockingScheduler(timezone="America/Sao_Paulo")
    # scheduler.add_job(job_function, 'cron', day_of_week='mon-sat', hour='21-23', minute='5,15,25,35,45,55')
    try:
        pass
        # scheduler.start()
    except (KeyboardInterrupt, SystemExit):
        print("Scheduler encerrado.")
