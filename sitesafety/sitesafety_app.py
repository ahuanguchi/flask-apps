import os
import requests
from flask import Flask, render_template, request
from lxml import html
from socket import gethostname
from urllib.parse import quote, urlparse
from werkzeug.contrib.cache import FileSystemCache

app = Flask(__name__)
cache = FileSystemCache(os.path.join(app.root_path, '_cache'))


def fix_link(href):
    if '?' not in href:
        return href
    return '/check?' + href.split('?')[1]


def parse_google_sb(site):
    url = 'https://www.google.com/safebrowsing/diagnostic?site='
    query = quote(site, safe='')
    page = url + query
    data = requests.get(page).text
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


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/check')
def check():
    site = request.args.get('site')
    if site:
        site = site.strip()
    if not site or '.' not in site[1:-1] or ' ' in site or '\\' in site or len(site) < 4:
        return render_template('index.html', warning=True)
    domain = urlparse(site).netloc
    if not domain:
        site_with_protocol = '//' + site if not site[0] == '/' else '/' + site
        domain = urlparse(site_with_protocol).netloc
        if not domain:
            return render_template('index.html', warning=True)
    response_data = cache.get(domain)
    if not response_data:
        sb = parse_google_sb(domain);
        response_data = render_template('check.html', domain=domain, sb=sb)
        # cache response for 12 hours
        cache.set(domain, response_data, timeout=43200)
    return response_data


@app.errorhandler(404)
def not_found(e):
    return render_template('404.html'), 404


if __name__ == '__main__':
    cache.clear()
    if 'liveconsole' not in gethostname():
        app.debug = 'True'
        app.run()
