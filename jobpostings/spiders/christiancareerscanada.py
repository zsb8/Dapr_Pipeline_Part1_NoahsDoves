import scrapy
import re
from datetime import datetime
from jobpostings.items import JobpostingsItem
from utils import functions


class ChristiancareerscanadaSpider(scrapy.Spider):
    name = 'christiancareerscanada'
    allowed_domains = ['christiancareerscanada.com']
    start_urls = ['https://christiancareerscanada.com/careers']
    total_num = 0

    def parse(self, response):
        node_list = response.xpath('.//*[@class="view-careers-front-block"]')
        for node in node_list:
            item = JobpostingsItem()
            pattern = r'<span class="field-content"><a href=\"(?P<url>.+?)\"\>\w'
            url = functions.extract_by_re(pattern, 'url', node.extract())
            if url:
                # to the detail page
                yield scrapy.Request(url=response.urljoin(url), callback=self.parse_detail, meta={'item': item})
        # change to other page
        if self.total_num == 0:
            pattern = r'<a title="Go to last page" href="/careers\?page=(?P<lastpage>.+?)">last'
            match = re.search(pattern, str(response.body), re.S)
            self.total_num = int(match.group("lastpage"))
            print(f"All pages number is {self.total_num}")
        if self.total_num > 0:
            for i in range(1, self.total_num+1):
                next_url = "https://christiancareerscanada.com/careers?page=" + str(i)
                print(f"URL address is:{next_url}")
                yield scrapy.Request(url=next_url, callback=self.parse)

    @staticmethod
    def parse_detail(response):
        item = response.meta['item']
        body = str(response.body)
        item['website'] = "christiancareerscanada"
        item['url'] = str(response.url)
        # get the jobTitle
        pattern = r'<h1 class="title" id="page-title">(?P<title>.+?)</h1>'
        item['jobTitle'] = functions.extract_by_re(pattern, 'title', body)
        # get the location and street
        pattern = r'<div class="c-address">(?P<location>.+?)</div>'
        location = functions.extract_by_re(pattern, 'location', body)
        location = location.replace("<br />", ",").replace("</br />", ",").strip()
        item['location'] = functions.clean_address(location)
        # get the street
        pattern = r'<div class="c-address">(?P<street>.+?)<br />'
        street = functions.extract_by_re(pattern, 'street', body)
        item['street'] = functions.clean_address(street)
        # get the region_locality and postcode
        pattern = r'<div class="c-address">.+<br />(?P<region_locality_postcode>.+?)</br />'
        region_locality_postcode = functions.extract_by_re(pattern, 'region_locality_postcode', body)
        item['postalCode'] = functions.extract_postcode(region_locality_postcode)
        item['regionLocality'] = functions.extract_city_province(region_locality_postcode, item['postalCode'])
        # get the issuer
        pattern = r'<div class="c-company career-element">' \
                  r'<i class="fa fa-th-large"></i> <strong>Company:</strong>(?P<issuer>.+?)</div>'
        item['issuer'] = functions.extract_by_re(pattern, 'issuer', body)
        # get the email
        pattern = r'<div class="c-email career-element"><i class="fa fa-envelope">' \
                  r'</i> <strong>Email:</strong> <a href="mailto:(?P<email>.+?)">'
        item['email'] = functions.extract_by_re(pattern, 'email', body)
        # get the phone
        pattern = r'<strong>Phone:</strong>(?P<phone>.+?)</div>'
        phone = functions.extract_by_re(pattern, 'phone', body)
        item['phone'] = phone.replace("-", "").replace(" ", "")
        # get the job description, all included, such as Qualifications, Salary, Ministry Expectations, Characteristics
        pattern = r'<div class="career-description"><h2>' \
                  r'<i class="fa fa-file-text-o"></i> Position Description</h2>(?P<description>.+?)</div>'
        item['description'] = functions.extract_by_re(pattern, 'description', body)
        # get the postedDate and timestamp
        pattern = r'<strong>Posted:</strong>(?P<postedDate>.+?)\|'
        posted_date = functions.extract_by_re(pattern, 'postedDate', body)
        item['postedDate'] = functions.clean_address(posted_date).strip()
        try:
            timestamp = datetime.timestamp(datetime.strptime(item['postedDate'], "%B %d,%Y"))
        except Exception as error:
            timestamp = 0
        item['timestamp'] = timestamp
        # get the expiryDate
        pattern = r'<strong>Expires:</strong> <span class="date-display-single">(?P<expiryDate>.+?)</span>'
        item['expiryDate'] = functions.extract_by_re(pattern, 'expiryDate', body)
        yield item


if __name__ == '__main__':
    from scrapy.crawler import CrawlerProcess
    from scrapy.utils.project import get_project_settings
    process = CrawlerProcess(get_project_settings())
    process.crawl('christiancareerscanada')
    process.start()
