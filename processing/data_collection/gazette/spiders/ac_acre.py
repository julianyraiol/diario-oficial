from datetime import date, datetime
from dateparser import parse
from dateutil.relativedelta import relativedelta

from scrapy import FormRequest

from gazette.items import Gazette
from gazette.spiders.base import BaseGazetteSpider


class AcreSpider(BaseGazetteSpider):
    START_URLS = "http://www.diario.ac.gov.br/"
    START_DATE = date(2017, 1, 1)

    name = "ac_acre"

    def start_requests(self):
        current_date = date.today()

        while current_date >= self.START_DATE:
            data = dict(mesano=current_date.strftime("%m/%Y"))

            yield FormRequest(
                self.START_URLS, formdata=data, callback=self.parse_executive
            )

            current_date = current_date - relativedelta(months=1)

    def parse_executive(self, response):
        gazzete_table = list(
            response.xpath('//div[@class="resultados_busca"]//table//tbody//tr')
        )

        for gazzete in gazzete_table:
            gazzete_date = gazzete.css("td:first-child::text").extract_first()
            gazzete_url = gazzete.css("td:nth-child(2) a::attr(href)").extract_first()

            yield Gazette(
                date=parse(gazzete_date, languages=["pt"]).date(),
                file_urls=[gazzete_url],
                is_extra_edition=False,
                power="executive_legislature",
                scraped_at=datetime.utcnow(),
            )
