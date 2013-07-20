# Copyright (c) 2010 Witchspace <witchspace81@gmail.com>
# Copyright (c) 2013 Rex
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.
"""Generic utilities used by bitcoin client library."""
from datetime import datetime
from types import Block, Transaction
from lxml import html


UNIX_EPOCH = datetime(1970, 1, 1, 0, 0)


def fetch_data(url):
    """
    :type url: str
    """
    import urllib2

    return urllib2.urlopen(url).read()


def fetch_json(url):
    """
    :type url: str
    """
    import urllib2
    import json

    return json.load(urllib2.urlopen(url))


def timestamp_to_datetime(timestamp):
    """
    :type timestamp: int
    :rtype : datetime
    """
    return datetime.utcfromtimestamp(timestamp)


def populate_block__block_chain_dot_info(json_block, **extra_attributes):
    """
    :type json_block: dict
    :rtype: Block
    """
    height = extra_attributes.get('height', json_block['height'])
    hash = extra_attributes.get('hash', json_block['hash'])
    previous_hash = extra_attributes.get('previous_hash', json_block['prev_block'])
    timestamp = extra_attributes.get('timestamp', timestamp_to_datetime(json_block['time']))

    txs = [
        Transaction(
            input_addresses=
            [input['prev_out']['addr'] for input in tx['inputs'] if
             input.get('prev_out', {}).get('addr', None) is not None],
            outputs=sorted([(output['n'], output['addr'], output['value'])
                            for output in tx['out'] if 'addr' in output and 'value' in output and 'n' in output
                           ], key=lambda t: t[0]),
            hash=tx['hash']
        )
        for tx in json_block['tx'] if 'hash' in tx
    ]

    return Block(height=height, hash=hash, previous_hash=previous_hash, transactions=txs, timestamp=timestamp)


def get_block_hash__block_explorer_dot_com(html_page_url):
    """
    :type html_page_url: str
    :rtype: str
    """
    hash_li = html.parse(html_page_url).xpath('//body/ul[1]/li[1]')[0]
    assert hash_li.text.lower() == 'hash'

    hash_text = hash_li.xpath('./sup')[0].tail
    if hash_text.startswith(':'):
        hash_text = hash_text[1:].strip()
    return hash_text


def retrieve_block__block_explorer_dot_com(html_page_url, raw_block_url):
    """
    :type html_page_url: str
    :type raw_block_url: str
    :rtype: Block
    """
    page = html.parse(html_page_url)
    raw_data = fetch_json(raw_block_url)

    height = int(page.xpath("//body/h1[1]")[0].text.split(' ')[1])
    hash = raw_data['hash']
    previous_hash = raw_data['prev_block']
    timestamp = timestamp_to_datetime(raw_data['time'])

    txs = [
        Transaction(
            input_addresses=[e.get('href').split('/')[-1] for e in row.xpath('./td[4]/ul[1]/li/a')],
            outputs=[(i, e.get('href').split('/')[-1], float(e.tail[1:].strip())) for i, e in enumerate(row.xpath('./td[5]/ul[1]/li/a'))],
            hash=row.xpath('./td[1]/a[1]')[0].get('href').split('/')[-1]
        )
        for row in page.xpath('//table[contains(concat(" ", normalize-space(@class), " "), " txtable ")]//tr')[1:]
    ]

    return Block(height=height, hash=hash, previous_hash=previous_hash, transactions=txs, timestamp=timestamp)