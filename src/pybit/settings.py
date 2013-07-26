__author__ = 'Rex'

SOURCE_LOCAL = 'local rpc'
SOURCE_BLOCKCHAIN_INFO = 'blockchain.info'
SOURCE_BLOCKEXPLORER_COM = "blockexplorer.com"

TEST = True
TEST_NET = True
DEFAULT_SOURCE = SOURCE_LOCAL

USE_FAKE_DATA = False
IGNORE_SEND_FROM_LOCAL = False

if USE_FAKE_DATA:
    from types import Block, Transaction
    from datetime import datetime, timedelta

    now = datetime.now()
    delta = timedelta(seconds=600)

    blocks = [
        Block(
            height=1,
            hash='1',
            previous_hash='0',
            transactions=[],  # test empty
            timestamp=now,
        ),
        Block(
            height=2,
            hash='2',
            previous_hash='1',
            transactions=[
                #openexchange change state to running
                Transaction(['xch_open_exchange'], [(1, 'xch_state_control', 1)], 'hash1'),
                #create asset ASICMINER
                Transaction(['xch_open_exchange'], [(1, 'xch_create_asset', 1)], 'hash2'),
                #change ASICMINER's running state to running
                Transaction(['xch_open_exchange'], [(1, 'asm_state_control', 1)], 'hash3'),
            ],
            timestamp=now+delta
        ),
        Block(
            height=3,
            hash='3',
            previous_hash='2',
            transactions=[
                #captain miao: limit sell 0.1*9999
                Transaction(['captain_miao'], [(1, 'asm_limit_sell', 10009999)], 'hash4'),
            ],
            timestamp=now+delta*2
        ),
        Block(
            height=4,
            hash='4',
            previous_hash='3',
            transactions=[
                #captain miao: limit sell 0.09*99
                Transaction(['captain_miao'], [(1, 'asm_limit_sell', 9000099)], 'hash4'),
                #rex: market buy 1BTC
                Transaction(['rex'], [(1, 'asm_market_buy', 1000000000)], 'hash5'),
            ],
            timestamp=now+delta*3
        )
    ]

    FAKE_DATA_GET_BLOCK_COUNT = len(blocks)  # exchange start height = 0 when debug
    FAKE_DATA_GET_BLOCK_BY_HASH = {str(i+1):blocks[i] for i in xrange(len(blocks))}
    FAKE_DATA_GET_BLOCK_BY_HEIGHT = {i+1:blocks[i] for i in xrange(len(blocks))}
