import rows
from scrapy import Request, Spider


class TCEDownloadFileSpider(Spider):
    name = "tce-downloader"

    def __init__(self, links_filename='links.csv', download_path='download/'):
        self.links_filename = links_filename
        self.download_path = download_path
        self.force_download = False

    def start_requests(self):
        links = rows.import_from_csv(self.links_filename, mode="rb")
        links.order_by('-year')
        download_path = self.crawler.settings.get('DOWNLOAD_PATH')
        for item in links:
            filename = download_path / item.url.split("/")[-1]
            if not filename.exists() or self.force_download:
                yield Request(item.url, meta={"filename": filename})

    def parse(self, response):
        with open(response.request.meta["filename"], mode="wb") as fobj:
            fobj.write(response.body)
