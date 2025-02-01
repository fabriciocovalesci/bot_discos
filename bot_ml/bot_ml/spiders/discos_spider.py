from pathlib import Path
import scrapy
from datetime import datetime
import os
import csv
import re
from utils import *


class DiscosSpider(scrapy.Spider):
    name = "bot_ml"

    def __init__(self, search_query, *args, **kwargs):
        super(DiscosSpider, self).__init__(*args, **kwargs)
        self.search_query = search_query  # Exemplo: "Rubinho e Mauro Assumpção"
        self.start_urls_list_ml = "https://lista.mercadolivre.com.br"
        self.url_product = "https://produto.mercadolivre.com.br"
        data_hora = datetime.now().strftime("%d-%m-%Y_%H-%M")
        self.resultados_csv = f'resultados_{data_hora}.csv'
        self.proibidos_csv = 'proibidos.csv'
        self.ja_coletados_csv = 'ja_coletados.csv'
        print(get_project_root())

    def start_requests(self):
        if self.search_query:
            search_url = f"{self.start_urls_list_ml}/{self.search_query}#D[A:{self.search_query}]"
            yield scrapy.Request(url=search_url, callback=self.parse)
        else:
            self.logger.error("Nenhum termo de pesquisa fornecido. Use -a search_query='termo' para especificar.")

    def parse(self, response, **kwargs):
        path_file = os.path.join(get_project_root(), "output", self.resultados_csv)
        is_new_file = not os.path.exists(path_file) or os.stat(path_file).st_size == 0
        palavras_proibidas = self.carregar_palavras_proibidas()
        links_ja_coletados = self.carregar_links_ja_coletados()


        with open(path_file, mode="a", newline='', encoding='utf-8') as file_resultados, \
             open(self.ja_coletados_csv, mode="a", newline='', encoding='utf-8') as file_coletados:

            writer_resultados = csv.writer(file_resultados)
            writer_coletados = csv.writer(file_coletados)

            if is_new_file:
                writer_resultados.writerow(['titulo', 'valor', 'link', 'termo', 'produto_id'])


            for item in response.xpath("//li[@class='ui-search-layout__item shops__layout-item']"):
                title = item.xpath(".//h3[@class='poly-component__title-wrapper']//a[@class='poly-component__title']//text()").get()
                price = item.xpath(".//div[@class='poly-price__current']//span/span[@class='andes-money-amount__fraction']//text()").get()
                links = item.xpath(".//h3[@class='poly-component__title-wrapper']/a/@href").getall()
                link = links[0] if links else None

                processed_link = self.process_link(link)
                produto_id = re.search(r'(MLB-\d+)', processed_link).group(1) if processed_link and re.search(r'(MLB-\d+)', processed_link) else None


                if not processed_link or not title:
                    continue


                if any(palavra.lower() in title.lower() for palavra in palavras_proibidas):
                    self.logger.info(f"❌ Ignorado (palavra proibida): {title}")
                    continue

                if not any(palavra in title.lower() for palavra in self.search_query.lower().split()):
                    self.logger.info(f"❌ Ignorado (título não contém termo de busca): {title}")
                    continue

                if processed_link in links_ja_coletados:
                    self.logger.info(f"🔄 Ignorado (já coletado): {processed_link}")
                    continue

                writer_resultados.writerow([
                    title.strip(),
                    f'{price.strip()}',
                    processed_link,
                    self.search_query.lower().replace(" ", "_"),
                    produto_id
                ])

                # yield {
                #     'titulo': title.strip(),
                #     'valor': f'R$ {price.strip()}' if price else None,
                #     'link': processed_link,
                #     'termo': self.search_query,
                #     'produto_id': produto_id
                # }

                writer_coletados.writerow([processed_link])
                self.logger.info(f"✅ Adicionado: {title}")



    def carregar_palavras_proibidas(self):
        """Lê palavras proibidas do arquivo CSV e retorna uma lista."""
        if not os.path.exists(self.proibidos_csv):
            return []
        with open(self.proibidos_csv, mode="r", encoding='utf-8') as file:
            return [linha.strip() for linha in file]
        

    def carregar_links_ja_coletados(self):
        """Lê links já coletados do CSV e retorna um conjunto."""
        if not os.path.exists(self.ja_coletados_csv):
            return set()
        with open(self.ja_coletados_csv, mode="r", encoding='utf-8') as file:
            return set(linha.strip() for linha in file)
        

    def process_link(self, link):
        """Processa o link, filtrando links que contêm 'MLB' e truncando até o '#'."""
        if link and 'MLB' in link:
            filtered_link = link.split('#')[0]
            return filtered_link
        return None
