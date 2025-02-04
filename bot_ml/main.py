from multiprocessing import Process
import csv
from bot_ml.pipelines import BotMlPipeline
from utils import get_project_root, get_latest_csv
from bot_ml.spiders.discos_spider import DiscosSpider
from scrapy.crawler import CrawlerRunner
from scrapy.utils.project import get_project_settings
from scrapy.utils.log import configure_logging
from twisted.internet import reactor
from datetime import datetime
from apscheduler.schedulers.blocking import BlockingScheduler
import os

class CrawlerRunnerProcess(Process):
    def __init__(self, spider, search_query):
        Process.__init__(self)
        
        settings = get_project_settings()
        settings.set("USER_AGENT", "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36")
        settings.set("DOWNLOAD_DELAY", 2)
        settings.set("AUTOTHROTTLE_ENABLED", True)
        settings.set("AUTOTHROTTLE_START_DELAY", 5)
        settings.set("AUTOTHROTTLE_MAX_DELAY", 60)
        settings.set("RETRY_TIMES", 3)
        settings.set("RETRY_HTTP_CODES", [500, 502, 503, 504, 403, 408])
        
        self.spider = spider
        self.search_query = search_query
        self.runner = CrawlerRunner(settings)

    def run(self):
        deferred = self.runner.crawl(self.spider, search_query=self.search_query)
        deferred.addBoth(lambda _: reactor.stop())
        reactor.run(installSignalHandlers=False)

def run_spider(search_query):
    try:
        crawler = CrawlerRunnerProcess(DiscosSpider, search_query)
        crawler.start()
        # crawler.join()
        return crawler
    except KeyboardInterrupt as err:
        print(f"Parou {err}")
        os._exit()

def job_function():
    print(datetime.now().time().strftime('%H:%M'))
    os.environ['TZ'] = 'America/Sao_Paulo'
    configure_logging()

    project_root = get_project_root()
    resource_path = os.path.join(project_root, "resource")
    output_path = os.path.join(project_root, "output")
    if not os.path.exists(output_path):
        os.makedirs(output_path)
    csv_file_path = os.path.join(resource_path, "input.csv")

    processos = []
    with open(csv_file_path, mode="r", newline='', encoding='utf-8') as file:
        reader = csv.reader(file)
        for row in reader:
            search_query = row[0].strip()
            print(search_query)
            run_spider(search_query)
            processo = run_spider(search_query)
            processos.append(processo)

    for processo in processos:
        processo.join()

    latest_csv = get_latest_csv(output_path)
    if latest_csv:
        print(f"📂 Convertendo {latest_csv} para Excel...")
        pipeline = BotMlPipeline()
        pipeline.close_spider(None)
    else:
        print("⚠ Nenhum CSV encontrado para conversão.")

    print("✅ Processo finalizado!")
