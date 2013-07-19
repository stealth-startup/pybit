__author__ = 'Rex'


import pybit
from pybit import settings

settings.USE_FAKE_DATA = False

print pybit.get_block_by_height(247326, source=settings.SOURCE_BLOCKEXPLORER_COM, test_net=False)
print pybit.get_block_by_height(80801, source=settings.SOURCE_BLOCKEXPLORER_COM, test_net=True)