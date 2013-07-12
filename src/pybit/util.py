# Copyright (c) 2010 Witchspace <witchspace81@gmail.com>
#
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
from copy import copy
from datetime import datetime
from data import Block, Transaction

UNIX_EPOCH = datetime(1970, 1, 1, 0, 0)


class DStruct(object):
    """
    Simple dynamic structure, like :const:`collections.namedtuple` but more flexible
    (and less memory-efficient)
    """
    # Default arguments. Defaults are *shallow copied*, to allow defaults such as [].
    _fields = []
    _defaults = {}

    def __init__(self, *args_t, **args_d):
        # order
        if len(args_t) > len(self._fields):
            raise TypeError("Number of arguments is larger than of predefined fields")
            # Copy default values
        for (k, v) in self._defaults.items():
            self.__dict__[k] = copy(v)
            # Set pass by value arguments
        self.__dict__.update(zip(self._fields, args_t))
        # dict
        self.__dict__.update(args_d)

    def __repr__(self):
        return '{module}.{classname}({slots})'.format(
            module=self.__class__.__module__, classname=self.__class__.__name__,
            slots=", ".join('{k}={v!r}'.format(k=k, v=v) for k, v in
                            self.__dict__.items()))


def fetch_data(url):
    """
    :type url: str
    :rtype: str
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
    our timestamp is 1000 times smaller than standard
    :type timestamp: int
    :rtype : datetime
    """
    return datetime.utcfromtimestamp(timestamp)


def populate_block(json_block, **extra_attributes):
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