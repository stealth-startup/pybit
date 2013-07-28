# Copyright (c) 2013 Rex

from datetime import datetime
from types import Block, Transaction
from connection import BitcoinConnection
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
    if extra_attributes.get('ensure_order', True):
        import pybit
        rpc = pybit.local_rpc_channel(extra_attributes.get('config_file_name'))
        block_info = rpc.getblock(hash)
        tx_hashes = block_info["tx"]
        """:type: list of str"""
        txs.sort(key=lambda tx: tx_hashes.index(tx.hash))

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
    from decimal import Decimal
    page = html.parse(html_page_url)
    raw_data = fetch_json(raw_block_url)

    height = int(page.xpath("//body/h1[1]")[0].text.split(' ')[1])
    hash = raw_data['hash']
    previous_hash = raw_data['prev_block']
    timestamp = timestamp_to_datetime(raw_data['time'])

    txs = [
        Transaction(
            input_addresses=[e.get('href').split('/')[-1] for e in row.xpath('./td[4]/ul[1]/li/a')],
            outputs=[(i, e.get('href').split('/')[-1], int(Decimal(e.tail[1:].strip()) * 100000000) )
                     for i, e in enumerate(row.xpath('./td[5]/ul[1]/li/a'))],
            hash=row.xpath('./td[1]/a[1]')[0].get('href').split('/')[-1]
        )
        for row in page.xpath('//table[contains(concat(" ", normalize-space(@class), " "), " txtable ")]//tr')[1:]
    ]

    return Block(height=height, hash=hash, previous_hash=previous_hash, transactions=txs, timestamp=timestamp)


def block_hash_to_height__local(rpc, block_hash):
    """
    :type rpc: BitcoinConnection
    :type block_hash: str
    :rtype: int
    """
    return int(rpc.getblock(block_hash)['height'])


def get_transaction_output__local(rpc, tx_hash, n=None):
    """
    :type rpc: BitcoinConnection
    :type tx_hash: str
    :rtype: tuple of (int, str, int) or list of tuple of (int, str, int)
    """
    from decimal import Decimal
    from pybit.exceptions import CanNotParseNonstandardTransaction

    outputs = []
    for out in rpc.getrawtransaction(tx_hash, True)['vout']:
        try:
            addresses = out['scriptPubKey']['addresses']
        except KeyError:
            assert out['scriptPubKey']['type'] == 'nonstandard'
            # if we are getting all outputs, we can ignore this non-standard transaction
            # or this output is not what we want, can also can ignore it
            if n is None or n != int(out['n']):
                continue
            else:  # n == int(out['n'])
                raise CanNotParseNonstandardTransaction(out=out)

        address = addresses[0]  # for those multi-address transactions, we will only record the first one

        assert isinstance(out['value'], (Decimal, int))  # make sure we won't have precision problem
        amount = int(out['value'] * 100000000)

        if n is None:
            outputs.append((int(out['n']), address, amount))
        elif n == int(out['n']):
            return int(out['n']), address, amount

    return outputs


def get_transaction__local(rpc, tx_hash):
    """

    :param rpc:
    :param tx_hash:
    :type rpc: BitcoinConnection
    :type tx_hash: str
    :rtype: Transaction
    """
    tx_info = rpc.getrawtransaction(tx_hash, True)
    outputs = get_transaction_output__local(rpc, tx_hash)
    inputs = [get_transaction_output__local(rpc, vin['txid'],vin['vout'])[1]
              for vin in tx_info['vin'] if 'coinbase' not in vin]
    return Transaction(inputs, outputs, tx_hash)


def retrieve_block__local(rpc, block_hash, only_wallet_transactions=True):
    """
    if only_wallet_transactions is False, we will try to decode the whole block,
    otherwise, we only return transactions that are related to our wallet (make sure it's secure before you do this).
    :type rpc: BitcoinConnection
    :type block_hash: str
    :type only_wallet_transactions: bool
    :rtype: Block
    """
    block_info = rpc.getblock(block_hash)

    height = int(block_info['height'])
    previous_hash = block_info['previousblockhash']
    timestamp = timestamp_to_datetime(block_info['time'])

    tx_hashes = block_info["tx"]

    if only_wallet_transactions:
        wallet_hashes = set([tx_info.txid for tx_info in rpc.listsinceblock(
            rpc.getblockhash(block_hash_to_height__local(rpc, block_hash) - 1))['transactions']
            if tx_info.blockhash == block_hash and tx_info['category'] == 'receive'
        ])
        tx_hashes = [tx_hash for tx_hash in tx_hashes if tx_hash in wallet_hashes]

    return Block(height=height, hash=block_hash, previous_hash=previous_hash, timestamp=timestamp,
                 transactions=[get_transaction__local(rpc, tx_hash) for tx_hash in tx_hashes])





