import os

from crawler_helper import AppleAppsCrawler

if __name__ == '__main__':
    company_name = os.environ.get('COMPANY', None)
    country_code = os.environ.get('COUNTRY_CODE', 'us')
    if company_name is None or company_name == '':
        raise ValueError('Invalid company name')
    crawler = AppleAppsCrawler()
    valid_status, company_id, company_name = crawler.verify_company(company_name)
    if valid_status is False:
        raise ValueError('Can not process this company')
    print(crawler.crawl_data_by_company_id(company_id, country_code, company_name))
    print('Finish process')
