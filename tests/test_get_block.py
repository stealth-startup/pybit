__author__ = 'Rex'


import sys
sys.path.append('../src')

import pybit
from pybit import settings


if __name__ == "__main__":
    settings.USE_FAKE_DATA = False

    print 'getting block 247326 from blockchain.info ...'
    block = pybit.get_block_by_height(247326, source=settings.SOURCE_BLOCKCHAIN_INFO, test_net=False)
    print block
    print len(block.transactions)

    print 'getting block 247326 from blockexplorer.com ...'
    block = pybit.get_block_by_height(247326, source=settings.SOURCE_BLOCKEXPLORER_COM, test_net=False)
    print block
    print len(block.transactions)

    print 'getting block 80801 (testnet) from blockexplorer.com ...'
    block = pybit.get_block_by_height(80801, source=settings.SOURCE_BLOCKEXPLORER_COM, test_net=True)
    print block
    print len(block.transactions)

    print 'getting block 80801 (testnet) from local bitcoind ...'
    block = pybit.get_block_by_height(80801, source=settings.SOURCE_LOCAL, test_net=True)
    print block
    print len(block.transactions)

    print 'finished'
