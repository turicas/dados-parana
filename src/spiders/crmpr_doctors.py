import json

import rows
import scrapy


class PtBrDateField(rows.fields.DateField):
    INPUT_FORMAT = "%d/%m/%Y"


class CRMPRSpider(scrapy.Spider):
    name = "crm-pr"
    base_url = "http://servicos.crmpr.org.br/portal/api/busca/profissionais?cidade=&especialidade=&proximo={proximo}"

    def start_requests(self):
        yield scrapy.Request(
            self.base_url.format(proximo=0), callback=self.start_requests_2
        )

    def start_requests_2(self, response):
        total = json.loads(response.body)["quantidade"]

        for proximo in range(0, total + 1, 12):
            yield scrapy.Request(
                self.base_url.format(proximo=proximo), callback=self.parse_items
            )

    def parse_items(self, response):
        data = json.loads(response.body_as_unicode())
        for item in data["lista"]:
            data = item["data"]
            sexo = item["sexo"]
            item["data"] = PtBrDateField.deserialize(data) if data else None
            item["sexo"] = sexo[0].upper() if sexo else None
            yield item
