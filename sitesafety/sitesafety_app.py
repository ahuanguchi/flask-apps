import json
import os
import requests
from datetime import datetime
from flask import Flask, render_template, request
from socket import gethostname
from urllib.parse import quote, urlparse
from werkzeug.contrib.cache import FileSystemCache

app = Flask(__name__)
cache = FileSystemCache(os.path.join(app.root_path, '_cache'))


def parse_date(timestamp):
    return datetime.utcfromtimestamp(timestamp).strftime('%Y-%m-%d')


def parse_google_sb(site):
    base = 'https://www.google.com/transparencyreport/safebrowsing/diagnostic/index.html#url='  # previously 'https://www.google.com/safebrowsing/diagnostic?site='
    query = quote(site, safe='')
    page = base + query
    resp_url = 'https://www.google.com/safebrowsing/diagnostic?output=jsonp&site=' + query
    resp = requests.get(resp_url).text
    resp_str = resp.split('processResponse(')[1].split(');')[0]
    resp_obj = json.loads(resp_str)
    url = resp_obj['website'].get('name')
    num_tested = resp_obj.get('numTested')
    if num_tested:
        status_set = set()
        for k in resp_obj['website'].keys():
            if k[-6:] == 'Status':
                status_set.add(resp_obj['website'].get(k))
        if 'listed' in status_set:
            status = 'Dangerous'
        elif 'partial' in status_set:
            status = 'Partially dangerous'
        else:
            status = 'Not dangerous'
        last_mal_int = resp_obj.get('lastMaliciousDate')
        if last_mal_int:
            last_mal = parse_date(last_mal_int)
        else:
            last_mal = 'N/A'
        last_update = parse_date(resp_obj.get('dataUpdatedDate'))
        sent_from = resp_obj['website']['malwareSite'].get('receivesTrafficFrom')
        attack = resp_obj['website']['malwareSite'].get('sendsToAttackSites')
        intermediary = resp_obj['website']['malwareSite'].get('sendsToIntermediarySites')
        result = {
            'page': page,
            'resp_url': resp_url,
            'url': url,
            'num_tested': num_tested,
            'status': status,
            'last_mal': last_mal,
            'last_update': last_update,
            'sent_from': sent_from,
            'sent_to': attack + intermediary,
        }
    else:
        result = {
            'page': page,
            'resp_url': resp_url,
            'url': url,
            'num_tested': num_tested,
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
        # cache.set(domain, response_data, timeout=43200)
    return response_data


@app.errorhandler(404)
def not_found(e):
    return render_template('404.html'), 404


if __name__ == '__main__':
    cache.clear()
    if 'liveconsole' not in gethostname():
        app.debug = 'True'
        app.run()
