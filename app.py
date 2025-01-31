import os
from twisted.internet import reactor
from twisted.internet.defer import DeferredList
from scrapy.crawler import CrawlerRunner
from scrapy.utils.project import get_project_settings
from scrapy.utils.log import configure_logging
from bot_ml.bot_ml.spiders.discos_spider import DiscosSpider
from utils import get_specific_folder, read_file_csv


def run_spider():
    """
    Executa o Scrapy para uma lista de palavras específicas.
    """
    # Carrega as configurações do Scrapy
    settings = get_project_settings()

    # Configurações personalizadas para evitar bloqueios
    settings.set("USER_AGENT", "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36")
    settings.set("DOWNLOAD_DELAY", 2)  # Atraso de 2 segundos entre as requisições
    settings.set("AUTOTHROTTLE_ENABLED", True)  # Habilita o AutoThrottle
    settings.set("AUTOTHROTTLE_START_DELAY", 5)  # Atraso inicial de 5 segundos
    settings.set("AUTOTHROTTLE_MAX_DELAY", 60)  # Atraso máximo de 60 segundos
    settings.set("RETRY_TIMES", 3)  # Número de tentativas em caso de falha
    settings.set("RETRY_HTTP_CODES", [500, 502, 503, 504, 403, 408])  # Códigos HTTP para tentar novamente
    print(f"🔍 Pipelines configurados: {settings.get('ITEM_PIPELINES')}")
    runner = CrawlerRunner(settings)
    deferreds = []

    # for search_query in search_queries:
    #     search_query = search_query.strip()
    #     if not search_query:
    #         continue  # Ignora consultas vazias

    #     print(f"🔍 Buscando por: {search_query}")
    deferred = runner.crawl(DiscosSpider)
    deferreds.append(deferred)

    # Espera todos os crawlers terminarem
    dlist = DeferredList(deferreds)
    dlist.addBoth(lambda _: reactor.stop())  # Para o reactor quando todos os crawlers terminarem




if __name__ == '__main__':
    # Configura o fuso horário e o logging
    os.environ['TZ'] = 'America/Sao_Paulo'
    configure_logging()

    try:
        # Lê os arquivos CSV
        folder_path = get_specific_folder("resource")
        if not os.path.exists(folder_path):
            raise FileNotFoundError(f"Pasta de recursos não encontrada: {folder_path}")

        csv_files = [f for f in os.listdir(folder_path) if f.endswith('.csv') and f.startswith('input')]
        if not csv_files:
            raise FileNotFoundError("Nenhum arquivo CSV encontrado na pasta de recursos.")

        words = read_file_csv(csv_files, folder_path)
        if not words:
            raise ValueError("Nenhuma palavra de busca encontrada nos arquivos CSV.")

        # Executa o spider
        run_spider()
        reactor.run()  # Executa o reactor para processar as requisições
    except Exception as e:
        print(f"🚨 Erro: {e}")
        reactor.stop()  # Para o reactor em caso de erro