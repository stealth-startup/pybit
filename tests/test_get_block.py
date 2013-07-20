__author__ = 'Rex'


import sys
sys.path.append('../src')

import pybit
from pybit import settings


if __name__ == "__main__":
    settings.USE_FAKE_DATA = False

    print pybit.get_block_by_height(247326, source=settings.SOURCE_BLOCKCHAIN_INFO, test_net=False)
    print pybit.get_block_by_height(247326, source=settings.SOURCE_BLOCKEXPLORER_COM, test_net=False)
    print pybit.get_block_by_height(80801, source=settings.SOURCE_BLOCKEXPLORER_COM, test_net=True)
