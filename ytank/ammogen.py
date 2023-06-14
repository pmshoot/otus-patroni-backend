#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import json
import sys
from lorem.text import TextLorem

SERVER_ADDRESS = '10.128.0.16'
SERVER_PORT = '1443'
LINES_COUNT = 100
URL = '/notes/'
TAG = 'Normal_Requests'
TEMPL_POST = '{}||{}||{}||{}\n'
TEMPL_GET = '{}||{}||{}\n'


def make_ammo(method, url, headers, case, body):
    """ makes phantom ammo """
    # http request w/o entity body template
    req_template = (
        "%s %s HTTP/1.1\r\n"
        "%s\r\n"
        "\r\n"
    )

    # http request with entity body template
    req_template_w_entity_body = (
        "%s %s HTTP/1.1\r\n"
        "%s\r\n"
        "Content-Length: %d\r\n"
        "\r\n"
        "%s\r\n"
    )

    if not body:
        req = req_template % (method, url, headers)
    else:
        req = req_template_w_entity_body % (method, url, headers, len(body), body)

    # phantom ammo template
    ammo_template = (
        "%d %s\n"
        "%s"
    )

    return ammo_template % (len(req), case, req)


def gen_get(lines=LINES_COUNT):
    """"""
    for i in range(lines):
        yield TEMPL_GET.format('GET', URL, TAG)


def gen_post(lines=LINES_COUNT):
    """"""
    lorem = TextLorem(srange=(3, 50))
    for i in range(lines):
        body = json.dumps({'text': lorem.sentence()})
        yield TEMPL_POST.format('POST', URL, TAG, body)


def main(method):
    if method == 'GET':
        func = gen_get
    else:
        func = gen_post
    for line in func():
        try:
            method, url, case, body = line.split("||")
            body = body.strip()
        except ValueError:
            method, url, case = line.split("||")
            body = None

        method, url, case = method.strip(), url.strip(), case.strip()

        headers = f"Host: {SERVER_ADDRESS}:{SERVER_PORT}\r\n" + \
                  "User-Agent: tank\r\n" + \
                  "Accept: */*\r\n" + \
                  "Content-Type: application/json\r\n" + \
                  "Connection: keep-alive"

        sys.stdout.write(make_ammo(method, url, headers, case, body))


if __name__ == "__main__":
    error_message = "Usage: python ammogen.py post | python ammogen.py get"
    try:
        method = sys.argv[1].upper()
        if method not in ('GET', 'POST'):
            sys.exit(error_message)
    except IndexError:
        sys.exit(error_message)

    main(method)
