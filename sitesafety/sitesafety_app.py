import os
import requests
from eventlet import GreenPool
from eventlet.green.urllib import request as eventlet_request
from flask import copy_current_request_context, Flask, render_template, request
from lxml import etree, html
from socket import gethostname
from urllib.parse import quote, urlparse
from werkzeug.contrib.cache import FileSystemCache

app = Flask(__name__)
cache = FileSystemCache(os.path.join(app.root_path, 'cache'))
pool = GreenPool()


def fix_link(href):
    if '?' not in href:
        return href
    return '/check?' + href.split('?')[1]


def parse_google_sb(site):
    url = 'https://www.google.com/safebrowsing/diagnostic?site='
    query = quote(site, safe='')
    page = url + query
    data = eventlet_request.urlopen(page).read()
    tree = html.fromstring(data)
    tree.rewrite_links(fix_link, False)
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
        data = eventlet_request.urlopen(page).read()
        # parse XML instead of HTML
        tree = etree.fromstring(data)
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
        result['summary'] = 'None'
    return result


def look_up(func_id, domain):
    with app.app_context():
        if func_id == 0:
            result = parse_google_sb(domain)
        else:
            result = parse_norton_sw(domain)
        return result


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/check')
def check():
    site = request.args.get('site')
    if not site or '.' not in site or ' ' in site:
        return render_template('index.html', warning=True)
    domain = urlparse(site).netloc
    if not domain:
        domain = urlparse('//' + site).netloc
    response_data = cache.get(domain)
    if not response_data:
        sb, sw = pool.starmap(look_up, ((0, domain), (1, domain)))
        response_data = render_template('check.html', domain=domain, sb=sb, sw=sw)
        if 'rate limiting' not in response_data:
            cache.set(domain, response_data, timeout=43200)     # 12 hours
    return response_data


@app.errorhandler(404)
def not_found(e):
    return render_template('404.html'), 404


if __name__ == '__main__':
    cache.clear()
    if 'liveconsole' not in gethostname():
        app.debug = 'True'
        app.run()
