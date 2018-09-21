import io
from collections import OrderedDict

import rows
import scrapy


class TCEFileListSpider(scrapy.Spider):
    """Scrape TCE-PR form to define cities and years available"""

    name = "tce-file-list"

    def start_requests(self):
        url = "http://servicos.tce.pr.gov.br/TCEPR/Tribunal/Relacon/Dados/DadosConsulta/Consulta/"
        yield scrapy.Request(url=url, callback=self.parse_list)

    def parse_list(self, response):
        url = "http://servicos.tce.pr.gov.br/TCEPR/Tribunal/Relacon/DadosConsulta/Pesquisa"
        table = rows.import_from_xpath(
            io.BytesIO(response.body),
            encoding=response.encoding,
            rows_xpath='//select[@id="cdMunicipio"]/option',
            fields_xpath=OrderedDict(
                [("municipio", "./text()"), ("codigo_ibge", "./@value")]
            ),
            force_types={"codigo_ibge": rows.fields.TextField},
        )
        cities = {
            row.municipio.strip(): row.codigo_ibge
            for row in table
            if row.codigo_ibge != 0
        }

        table = rows.import_from_xpath(
            io.BytesIO(response.body),
            encoding=response.encoding,
            rows_xpath='//select[@id="nrAno"]/option',
            fields_xpath=OrderedDict([("year", "./@value")]),
        )
        years = [row.year for row in table if row.year != 0]

        for year in years:
            for city, ibge_code in cities.items():
                post_data = {
                    "cdMunicipio": ibge_code,
                    "municipio": city,
                    "nrAno": str(year),
                }
                yield scrapy.FormRequest(
                    url,
                    method="POST",
                    formdata=post_data,
                    meta={"city": city, "ibge_code": ibge_code, "year": year},
                    callback=self.parse_result,
                )

    def parse_result(self, response):
        meta = response.request.meta
        links = rows.import_from_xpath(
            io.BytesIO(response.body),
            encoding=response.encoding,
            rows_xpath="//a",
            fields_xpath=OrderedDict(
                [("document_type", ".//text()"), ("url", ".//@href")]
            ),
        )
        # TODO: what if 'links' is empty? Probably wrong ibge_code passed
        for link in links:
            link = link._asdict()
            link.update(
                {
                    "city": meta["city"],
                    "ibge_code": meta["ibge_code"],
                    "year": meta["year"],
                }
            )
            yield link
