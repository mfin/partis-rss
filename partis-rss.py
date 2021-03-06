#!/usr/bin/env python

import os
import re
import requests
import gevent
import arrow
from gevent import monkey
from flask import Flask, make_response
from werkzeug.contrib.atom import AtomFeed
from bs4 import BeautifulSoup

monkey.patch_all()

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
session.post('http://www.partis.si/user/login', data=payload)


def get_id(href):
    return href.split('/')[-1]


def get_url(torrent_id):
    return 'http://www.partis.si/torrent/prenesi/{}'.format(torrent_id)


def set_rss_url(torrent_id):
    return '/torrents/{}.torrent'.format(torrent_id)


def get_page(torrent_id):
    return 'http://www.partis.si/torrent/podrobno/{}'.format(torrent_id)


def get_torrent_info(torrent_id):
    torrent_page = get_page(torrent_id)
    response = session.get(torrent_page)
    data = BeautifulSoup(response.text, 'html.parser')
    title = data.find('div', class_='h11').string
    date = data.find('table', class_='q4').find(string=re.compile("Dodano")).find_next('td', class_='q3').string
    return [title, arrow.get(date, 'DD.MM.YYYY ob HH:mm:ss').replace(tzinfo='Europe/Ljubljana')]


def torrent_to_rss(torrent, feed):
    torrent_id = get_id(torrent.a.get('href'))
    torrent_info = get_torrent_info(torrent_id)
    torrent_url = set_rss_url(torrent_id)
    feed.add(torrent_info[0],
             content_type='html',
             url=torrent_url,
             updated=torrent_info[1])


@app.route('/torrents/<path:torrent_id>.torrent')
def get_torrent(torrent_id):
    torrent = session.get(get_url(torrent_id))
    response = make_response(torrent.content)
    response.headers['Content-Disposition'] = 'attachment; filename={}.torrent'.format(torrent_id)
    return response


@app.route("/")
def rss_feed():
    response = session.get('http://www.partis.si/brskaj?offset=0&ns=true', headers=headers)
    data = BeautifulSoup(response.text, 'html.parser')

    feed = AtomFeed('Recent Torrents', feed_url=rss_url, url=rss_url)
    torrent = data.find_all('div', class_='listeklink')

    inject = [gevent.spawn(torrent_to_rss, _torrent, feed) for _torrent in torrent]
    gevent.joinall(inject)

    return feed.get_response()


if __name__ == '__main__':
    app.run(host='0.0.0.0')
