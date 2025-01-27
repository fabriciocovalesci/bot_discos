from pathlib import Path

import scrapy


## PAEBIRU
## RONNIE VON MISTERIOSA
## AMADO MAITA

class DiscosSpider(scrapy.Spider):
    name = "bot"

    def __init__(self, search_query=None, *args, **kwargs):
        super(DiscosSpider, self).__init__(*args, **kwargs)
        self.search_query = search_query
        self.start_urls_list_ml = "https://lista.mercadolivre.com.br"
        self.url_product = "https://produto.mercadolivre.com.br"


    def start_requests(self):
        if self.search_query:
            search_url = f"{self.start_urls_list_ml}/{self.search_query}#D[A:{self.search_query}]"
            yield scrapy.Request(url=search_url, callback=self.parse)
        else:
            self.logger.error("Nenhum termo de pesquisa fornecido. Use -a search_query='termo' para especificar.")



    def parse(self, response, **kwargs):
        for item in response.xpath("//li[@class='ui-search-layout__item shops__layout-item']"):
            title = item.xpath(".//h3[@class='poly-component__title-wrapper']//a[@class='poly-component__title']//text()").get()
            price = item.xpath(".//div[@class='poly-price__current']//span/span[@class='andes-money-amount__fraction']//text()").get()
            links = item.xpath(".//h3[@class='poly-component__title-wrapper']/a/@href").getall()
            link = links[0] if links else None

            processed_link = self.process_link(link)
            title_exists = processed_link.split(f"{self.base}/", 1)[1]

            if processed_link:
                yield {
                    'titulo': title.strip() if title else None,
                    'valor': price.strip() if f'R$ {price}' else None,
                    'link': processed_link
                }

        # pagination_links = response.xpath('//nav[@aria-label="Paginação"]//a/@href').getall()

        # for link in pagination_links:
        #     yield response.follow(link, self.parse)
        

    def process_link(self, link):
        """Processa o link, filtrando links que contêm 'MLB' e truncando até o '#'."""
        if link and 'MLB' in link:
            filtered_link = link.split('#')[0]
            return filtered_link
        return None
    