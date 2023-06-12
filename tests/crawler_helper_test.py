from unittest.mock import patch

from lxml import html

from crawler_helper import make_request, AppleAppsCrawler


@patch('crawler_helper.requests.get')
def test_make_request_html(mock_get):
    url = 'https://example.com'
    response_content = '<html><body>Test HTML</body></html>'
    mock_get.return_value.status_code = 200
    mock_get.return_value.content = response_content.encode()

    result = make_request(url)
    assert (result, response_content)


@patch('crawler_helper.requests.get')
def test_make_request_json(mock_get):
    url = 'https://example.com'
    response_json = {'key': 'value'}
    mock_get.return_value.status_code = 200
    mock_get.return_value.json.return_value = response_json
    result = make_request(url, response_type='json')

    assert (result, response_json)


def test_verify_company(mocker):
    crawler = AppleAppsCrawler()
    mocker.patch("crawler_helper.make_request", return_value={
        'resultCount': 1,
        'results': [
            {
                'artistId': 1,
                'artistName': 'test'
            }
        ]
    })
    result = crawler.verify_company('test')
    assert result == (True, 1, 'test')


@patch('crawler_helper.make_selenium_request')
def test_extract_valid_links(mock_make_selenium_request):
    crawler = AppleAppsCrawler()
    with open('./extract_valid_links.html', 'r') as f:
        html_content = f.read()

    mock_dom = html.fromstring(html_content)
    mock_make_selenium_request.return_value = mock_dom

    url = "https://example.com/page"
    expected_links = ["https://example.com/page",
                      "https://example.com/page/us/developer/netflix-inc/id363590054?see-all=i-phonei-pad-apps"]
    result = crawler.extract_valid_links(url)

    assert (result, expected_links)
    mock_make_selenium_request.assert_called_once_with(url)
