import scrapy
import re
import time
import platform
from selenium import webdriver
from selenium.webdriver.common.by import By
from jobpostings.items import JobpostingsItem
from utils import functions
from jobpostings import settings


class ChristiancharityjobsSpider(scrapy.Spider):
    name = 'christiancharityjobs'
    allowed_domains = ['christiancharityjobs.ca']
    start_urls = ['http://christiancharityjobs.ca/']

    def parse(self, response):
        url_list = []
        options = webdriver.ChromeOptions()
        options.add_argument('--headless')
        options.add_argument('--disable-gpu')
        options.add_argument("--disable-blink-features=AutomationControlled")
        operation = platform.uname()
        if operation[0] == "Windows":
            # This two rows coding only be used when we need to run Selenium in Win10 OS.
            path = settings.CHROMEDRIVER_PATH + 'chromedriver.exe'
            driver = webdriver.Chrome(executable_path=path, options=options)
        if operation[0] == "Linux":
            # Use this command If it runs in the Docker Environment because need to use Selenium Docker service.
            driver = webdriver.Remote(command_executor=settings.SELENIUM_API, options=options)
        driver.get("https://www.christiancharityjobs.ca/search")
        msg_title_list1 = driver.find_elements(By.ID, 'lnkJobId')
        for msg in msg_title_list1:
            url_list.append(msg.get_attribute("href"))
        msg_element = driver.find_element(By.CLASS_NAME, 'pagerPageLink')  # It is importance to locate next page
        msg_element.click()
        msg_title_list2 = driver.find_elements(By.ID, 'lnkJobId')
        for msg in msg_title_list2:
            url_list.append(msg.get_attribute("href"))
        for url in url_list:
            item = JobpostingsItem()
            yield scrapy.Request(url=url, callback=self.parse_detail, meta={'item': item})
        driver.quit()

    @staticmethod
    def parse_detail(response):
        item = response.meta['item']
        body = str(response.body)
        item['website'] = "christiancharityjobs"
        item['url'] = str(response.url)
        # get the title
        pattern = r'<span id="lblOutTitle">(?P<title>.+?)</span>'
        item['jobTitle'] = functions.extract_by_re(pattern, 'title', body)
        # get the issuer
        pattern = r'<span id="lblOutEmployer">(?P<issuer>.+?)</span>'
        item['issuer'] = functions.extract_by_re(pattern, 'issuer', body)
        # get the postedDate
        pattern = r'<span id="lblOutPostedDate" class="formDataLabel">(?P<posted_date>.+?)</span>'
        item['postedDate'] = functions.extract_by_re(pattern, 'posted_date', body)
        try:
            timestamp = time.mktime(time.strptime(item['postedDate'], "%m/%d/%Y"))
        except Exception as error:
            timestamp = 0
        item['timestamp'] = timestamp
        # get the description
        pattern = r'<div id="description" class="formItemContainer widthFull clearLeft">(?P<description>.+?)</div>'
        item['description'] = functions.clean_stringjunk(functions.extract_by_re(pattern, 'description', body))
        # get the location and street
        pattern = r'<span id=\"lblOutAddress\" class=\"formDataLabel\">(?P<location>.+?)</span>'
        match = re.search(pattern, str(response.body), re.S)
        if match:
            location = match.group("location")
            item['location'] = location.replace("<br />", ",").strip()
            location_list = item['location'].split(",")
            region_locality_postcode = ""
            if len(location_list) >= 3:
                street = ",".join(location_list[0:-2])
                item['street'] = functions.clean_address(street)
                region_locality_postcode = functions.clean_stringjunk(location_list[-2] + "," + location_list[-1])
            if len(location_list) >= 2:
                item['street'] = functions.clean_address(location_list[0])
                region_locality_postcode = functions.clean_stringjunk(location_list[1])
            item["postalCode"] = functions.extract_postcode(region_locality_postcode)
            item['regionLocality'] = functions.extract_city_province(region_locality_postcode, item["postalCode"])
        yield item


if __name__ == '__main__':
    from scrapy.crawler import CrawlerProcess
    from scrapy.utils.project import get_project_settings
    process = CrawlerProcess(get_project_settings())
    process.crawl('christiancharityjobs')
    process.start()
