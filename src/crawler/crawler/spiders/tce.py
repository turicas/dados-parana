# -*- coding: utf-8 -*-
import scrapy
import rows
import io
import itertools
from collections import OrderedDict


class TceSpider(scrapy.Spider):
    name = 'tce'
    allowed_domains = ['tce.pr.gov.br']

    BASE_URL = "http://servicos.tce.pr.gov.br/TCEPR/Tribunal/Relacon/Dados"
    LIST_URL = f'{BASE_URL}/DadosConsulta/Consulta'
    SEARCH_URL = f'{BASE_URL}/DadosConsulta/Pesquisa'

    start_urls = [LIST_URL]

    def parse(self, response):
        for year, (city, ibge_code) in itertools.product(
                self.extract_years(response),
                self.extract_cities(response).items()):
            yield self.make_search_url(ibge_code, city, year)

    def parse_search_result(self, response):
        meta = response.request.meta
        links = rows.import_from_xpath(
            io.BytesIO(response.body),
            encoding=response.encoding,
            rows_xpath="//a",
            fields_xpath=OrderedDict(
                [("document_type", ".//text()"), ("url", ".//@href")]
            ),
        )
        if not links:
            self.logger.warning(
                f'Não há resultados para {meta["city"]}/{meta["year"]}')
            return

        for link in links:
            link = link._asdict()
            link.update({
                "city": meta["city"],
                "ibge_code": meta["ibge_code"],
                "year": meta["year"],
            })
            yield link

    def extract_cities(self, response):
        """ Return a dict of available cities in the search form """
        table = rows.import_from_xpath(
            io.BytesIO(response.body),
            encoding=response.encoding,
            rows_xpath='//select[@id="cdMunicipio"]/option',
            fields_xpath=OrderedDict(
                [("municipio", "./text()"), ("codigo_ibge", "./@value")]
            ),
            force_types={"codigo_ibge": rows.fields.TextField},
        )
        return {
            row.municipio.strip(): row.codigo_ibge
            for row in table
            if row.codigo_ibge != 0
        }

    def extract_years(self, response):
        """ Return a list of years available in the search form """
        table = rows.import_from_xpath(
            io.BytesIO(response.body),
            encoding=response.encoding,
            rows_xpath='//select[@id="nrAno"]/option',
            fields_xpath=OrderedDict([("year", "./@value")]),
        )
        return [row.year for row in table if row.year != 0]

    def make_search_url(self, ibge_code, city, year):
        """ Return the download URL along with the post data """
        post_data = {
            "cdMunicipio": ibge_code,
            "municipio": city,
            "nrAno": str(year),
        }
        return scrapy.FormRequest(
            self.SEARCH_URL,
            method="POST",
            formdata=post_data,
            meta={"city": city, "ibge_code": ibge_code, "year": year},
            callback=self.parse_search_result,
        )
