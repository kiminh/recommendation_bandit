# utf-8
import json
import os
import random
import re

from datetime import datetime
from pprint import pprint

import requests
import redis

from bs4 import BeautifulSoup as Soup
from flask import Flask, jsonify, request, render_template, Response
from requests_toolbelt.adapters import appengine
from flask_wtf import Form
from function.storecontent import *
from requests_toolbelt.adapters import appengine
from wtforms import DateField, TextField, IntegerField


appengine.monkeypatch()

app = Flask(__name__)
app.secret_key = 'SHH!'

DOMAIN = 'https://adelaidefringe.com.au/'

# global EPSILON
# global BANNER
EPSILON = {'v': 0}
BANNER = {'v': 1}

# client = datastore.Client()

# content_key = client.key('content', 'testcontent1')

def _proxy(sessionid):
    resp = requests.request(
        method=request.method,
        url=request.url.replace(request.host_url, DOMAIN),
        headers={key: value for (key, value) in request.headers if key != 'Host'},
        data=request.get_data(),
        cookies=request.cookies,
        allow_redirects=False
    )

    content = resp.content

    if 'text/html' in resp.headers.get('Content-Type', '') and BANNER['v'] == 1:
        try:
            soup = Soup(resp.content, features='html.parser')
            header = soup.find('header')
            header_idx = header.parent.contents.index(header)
            banner_images = getBannerImages(numimages=4, sessionid=sessionid, EPSILON=EPSILON)
            html_banners = ''
            for banner_image_url in banner_images:
                html_banners += '<div class="banner-image-container"><div class="bandit-title">[BANDITS FAVORITES]</div><img class="banner-image" src="{}"></div>'.format(banner_image_url)
            header.parent.insert(
                header_idx + 1,
                Soup(
"""
<div class="banner-container">
    <div class="viewport">
""" + html_banners + \
"""
    </div>
</div>
<style>
div.banner-container {
    width: 100%;
    postion: relative;
    display: flex;
    justify-content: center;
    margin-bottom: -5px;
}
div.bandit-title {
    position: absolute;
    left: 20px;
    top: 20px;
    color: white;
    text-shadow: -3px 3px 2px black;
    font-weight: bold;
    font-size: 20px;
}
div.viewport {
    position: relative;
    display: flex;
    width: 100%;
    overflow: hidden;
    -ms-overflow-style: none;
    overflow: -moz-scrollbars-none;
}
div.banner-image-container {
    transition: all 0.2s ease-in-out;
    position: relative;
    width: 25%;
    min-width: 25%;
}
div.banner-image-container:hover {
    width: 100%;
    transform: scale(1.1);
}
div.banner-image-container img {
    width: 100%;
    cursor: pointer;
}
</style>
""",
                    features="html.parser"
                )
            )
            content = str(soup)
        except AttributeError:
            pass

    if 'application/json' in resp.headers.get('Content-Type', ''):
        print('path contains json')
        json_doc = resp.json()
        if type(json_doc) != list:
            storejsoncontent(json_doc,  request.url.split('?')[-1])
            remixed = remixjsoncontent(json_doc, request.url.split('?')[-1], EPSILON)
            content = json.dumps(remixed)


    excluded_headers = ['content-encoding', 'content-length', 'transfer-encoding', 'connection']
    headers = [
        (name, value) for (name, value)
        in resp.raw.headers.items()
        if name.lower() not in excluded_headers
    ]

    response = Response(content, resp.status_code, headers)
    return response


@app.route('/', defaults={'path': ''})
@app.route('/<path:path>')
def forward(*args, **kwargs):
    if 'epsilon' in request.url.split('?')[-1]:
        EPSILON['v'] = float(request.url.split('=')[-1])
        print ('epsilon set to {}'.format(EPSILON['v']))

        response = Response('OK')
        response.set_cookie('epsilon', str(EPSILON['v']))
        return response

    if 'magicbanner' in request.url.split('?')[-1]:
        BANNER['v'] = float(request.url.split('=')[-1])
        print ('banner set to {}'.format(BANNER['v']))

        response = Response('OK')
        response.set_cookie('banner', str(BANNER['v']))
        return response

    user_id = request.cookies.get('ads_user_id')
    if user_id is None:
        user_id = "%032x" % random.getrandbits(128)

    epsilon = request.cookies.get('epsilon')
    if epsilon is not None:
        EPSILON['v'] = float(epsilon)

    banner = request.cookies.get('banner')
    if banner is not None:
        BANNER['v'] = float(banner)

    addClickTo(request.url, user_id)
    print('user_id is {}'.format(user_id))

    # kwargs = {**kwargs, **{sessionid: user_id}}

    response = _proxy(user_id)
    response.set_cookie('ads_user_id', user_id)
    response.set_cookie('epsilon', str(EPSILON['v']))
    response.set_cookie('banner', str(BANNER['v']))

    return response

if __name__ == "__main__":
    app.run()