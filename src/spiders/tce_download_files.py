from pathlib import Path

import rows
import scrapy
from rows.utils import open_compressed

from settings import DOWNLOAD_PATH, OUTPUT_PATH


class TCEDownloadFileSpider(scrapy.Spider):
    name = "tce-download-file"

    def start_requests(self):
        # TODO: add option to change filename via parameter
        links_filename = OUTPUT_PATH / "tce-link.csv"
        links = rows.import_from_csv(open_compressed(links_filename, mode="rb"))
        links.order_by('-year')

        for item in links:
            filename = DOWNLOAD_PATH / item.url.split("/")[-1]
            if not filename.exists():  # TODO: add option to force redownload
                yield scrapy.Request(url=item.url, meta={"filename": filename})

    def parse(self, response):
        with open(response.request.meta["filename"], mode="wb") as fobj:
            fobj.write(response.body)
