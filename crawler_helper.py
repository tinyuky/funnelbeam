import json
import re

import requests
from bs4 import BeautifulSoup
from lxml.etree import HTML
from selenium import webdriver
from selenium.webdriver.chrome.options import Options


class AppleAppsCrawler:
    def __init__(self):
        self.main_url = 'https://apps.apple.com/'
        self.company_verify_url = 'https://itunes.apple.com/search?term={0}&entity=software&limit=1'
        self.app_url = self.main_url + '{0}/developer/{1}'

    def verify_company(self, company_name: str) -> (bool, str, str):
        url = self.company_verify_url.format(company_name)
        data = make_request(url, response_type='json')
        if data and 'resultCount' in data and data['resultCount'] > 0 \
                    and 'results' in data and data['results'][0] and 'artistId' in data['results'][0]:
                return True, data['results'][0]['artistId'], data['results'][0]['artistName']
        else:
            return False, None, None

    def crawl_data_by_company_id(self, company_id: str, country_code: str, company_name: str) -> json:
        result = {}

        # Get all valid url
        url = self.app_url.format(country_code, company_id)
        valid_links = self.extract_valid_links(url)

        # Get data from every url
        for link in valid_links:
            dom = make_request(link)
            if dom is None:
                continue
            items = dom.xpath("//a[contains(@class, 'targeted-link')]")
            for item in items:
                app_id = self.extract_app_id(item.attrib['href'])
                if app_id in result:
                    result[app_id]['app_targets'] += self.extract_app_targets(item.attrib['data-metrics-location'])
                else:
                    result[app_id] = {
                        'app_name': self.extract_app_name(item.attrib['aria-label']),
                        'app_id': app_id,
                        'app_url': item.attrib['href'],
                        'app_targets': self.extract_app_targets(item.attrib['data-metrics-location'])
                    }
        return self.export_result(result, company_name)

    def extract_valid_links(self, url):
        dom = make_selenium_request(url)
        see_all_links = dom.xpath("//a[contains(@class, 'section__nav__see-all-link')]")
        valid_links = [url] + [self.main_url + link.attrib['href'] for link in see_all_links]
        return valid_links

    def extract_app_name(self, item_text: str) -> str:
        app_name = ''
        match = re.match(r'^([^\.]+)', item_text)
        if match:
            app_name = match.group(0)
        return app_name

    def extract_app_id(self, item_text: str) -> str:
        app_id = ''
        match = re.search(r'/id(\d+)', item_text)
        if match:
            app_id = match.group(1)
        return app_id

    def extract_app_targets(self, item_text: str) -> list:
        result = []
        if 'iphone' in item_text.lower():
            result.append('Iphone')
        if 'ipad' in item_text.lower():
            result.append('Ipad')
        if 'appletv' in item_text.lower():
            result.append('AppleTv')
        return result

    def export_result(self, result, company_name):
        output = {'company_name': company_name, 'apps': []}
        for item in result:
            result[item]['app_targets'] = list(set(result[item]['app_targets']))
            output['apps'].append(result[item])
        return output


def make_request(url, response_type='html'):
    HEADERS = ({'User-Agent':
                    'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 \
                    (KHTML, like Gecko) Chrome/44.0.2403.157 Safari/537.36',
                'Accept-Language': 'en-US, en;q=0.5'})
    response = requests.get(url, headers=HEADERS)
    data = None
    if response.status_code == 200:
        if response_type == 'json':
            data = response.json()
        else:
            soup = BeautifulSoup(response.content, 'html.parser')
            data = HTML(str(soup))
    return data


def make_selenium_request(url) -> HTML:
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument('--disable-blink-features=AutomationControlled')
    chrome_options.add_argument('--disable-extensions')
    chrome_options.add_argument('--no-sandbox')

    driver = webdriver.Chrome(options=chrome_options)
    driver.get(url)
    content = driver.page_source
    driver.quit()
    return HTML(str(BeautifulSoup(content, 'html.parser')))
