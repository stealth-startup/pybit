__author__ = 'rex'

SOURCE_LOCAL = 'local rpc'
SOURCE_BLOCKCHAIN_INFO = 'blockchain.info'
SOURCE_BLOCKEXPLORER_COM = "blockexplorer.com"

TEST_NET = False
DEFAULT_SOURCE = SOURCE_BLOCKCHAIN_INFO

DEBUG = True

if DEBUG:
    DEBUG_GET_BLOCK_COUNT = None
    DEBUG_GET_BLOCK_BY_HASH = {}  # from str to Block
    DEBUG_GET_BLOCK_BY_HEIGHT = {}  #  from int to Block
    DEBUG_SEND_PAYMENT = True