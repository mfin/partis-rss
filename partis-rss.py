#!/usr/bin/env python

import requests
import os
from flask import Flask
from werkzeug.contrib.atom import AtomFeed
from bs4 import BeautifulSoup
from datetime import datetime

app = Flask(__name__)

username = os.getenv('PARTIS_USERNAME')
password = os.getenv('PARTIS_PASSWORD')
rss_url = 'http://127.0.0.1:5000'

payload = {
    'action': 'login',
    'user[username]': username,
    'user[password]': password
}

headers = {
    'X-Requested-With': 'XMLHttpRequest',
    'Content-Type': 'text/html; charset=utf-8'
}

session = requests.Session()
session.post('https://www.partis.si/user/login', data=payload)

response = session.get('https://www.partis.si/brskaj?offset=0&ns=true', headers=headers)
data = BeautifulSoup(response.text, 'html.parser')


def get_id(href):
    return href.split('/')[-1]


def get_url(torrent_id):
    return 'https://www.partis.si/torrent/prenesi/{}'.format(torrent_id)


def set_rss_url(torrent_id):
    return '/static/{}.torrent'.format(torrent_id)


def get_page(torrent_id):
    return 'https://www.partis.si/torrent/podrobno/{}'.format(torrent_id)


def get_title(torrent_id):
    torrent_page = get_page(torrent_id)
    response = session.get(torrent_page)
    data = BeautifulSoup(response.text, 'html.parser')
    return data.find('div', class_='h11').string


def get_file(torrent_id):
    torrent_file = 'static/{}.torrent'.format(torrent_id)
    with open(torrent_file, 'wb') as handle:
        response = session.get(get_url(torrent_id))

        for block in response.iter_content(1024):
            handle.write(block)

@app.route("/")
def rss_feed():
    feed = AtomFeed('Recent Torrents', feed_url=rss_url, url=rss_url)
    for torrent in data.find_all('div', class_='listeklink'):
        torrent_id = get_id(torrent.a.get('href'))
        torrent_title = get_title(torrent_id)
        get_file(torrent_id)
        torrent_url = set_rss_url(torrent_id)
        feed.add(torrent_title,
                 content_type='html',
                 url=torrent_url,
                 updated=datetime.now())
        print('ADDED: {} at {}\n'.format(torrent_title, torrent_url))
    return feed.get_response()

if __name__ == '__main__':
    app.run(host='0.0.0.0')
