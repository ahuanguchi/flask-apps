import requests
from flask import Flask, render_template, request
from lxml import etree, html
from urllib.parse import quote

app = Flask(__name__)


def parse_google_sb(site):
    url = 'https://www.google.com/safebrowsing/diagnostic?site='
    query = quote(site, safe='')
    page = url + query
    r = requests.get(page)
    tree = html.fromstring(r.content)
    tree.make_links_absolute('https://www.google.com')
    url = tree.xpath('//h3/text()', smart_strings=False)[0].rsplit(' ', 1)[1]
    blockquotes = [html.tostring(x, encoding='unicode')
                   for x in tree.xpath('//blockquote')]
    result = {
        'page': page,
        'url': url,
        'status': blockquotes[0],
        'summary': blockquotes[1],
        'intermediary': blockquotes[2],
        'hosted': blockquotes[3]
    }
    return result


def parse_norton_sw(site):
    result = {}
    try:
        # YQL for requests outside of PythonAnywhere's free user whitelist
        url = 'https://query.yahooapis.com/v1/public/yql?q='
        query_url = 'http://safeweb.norton.com/report/show?url='
        result['page'] = query_url + quote(site, safe='')
        query = quote('select * from html where url="%s"' % (query_url + site), safe='')
        page = url + query
        r = requests.get(page)
        # parse XML instead of HTML
        tree = etree.fromstring(r.content)
        norton_url = tree.xpath('//a[@class="nolink"]/@title', smart_strings=False)[0]
        result['url'] = norton_url
        norton_ico = tree.xpath('//div[@class="big_rating_wrapper"]/img/@alt',
                                smart_strings=False)[0]
        result['ico'] = norton_ico.replace('ico', '').replace('NSec', 'Norton sec')
        norton_summary = tree.xpath('//div[@class="span10"]')[0]
        result['summary'] = etree.tostring(norton_summary, method='html',
                                           encoding='unicode')
        norton_community = tree.xpath('//div[@class="community-text"]')[0]
        result['community'] = etree.tostring(norton_community, method='html',
                                             encoding='unicode')
    except IndexError:
        result['summary'] = "None"
    return result


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/check')
def check():
    site = request.args['site']
    if '.' not in site:
        return render_template('index.html', warning=True)
    sb = parse_google_sb(site)
    sw = parse_norton_sw(site)
    template = render_template(
        'check.html',
        site=site,
        sb=sb,
        sw=sw
    )
    return template


if __name__ == '__main__':
    app.debug = 'True'
    app.run()
