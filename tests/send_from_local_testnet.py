import sys
sys.path.append('../src')

import pybit
from pybit import settings

settings.IGNORE_SEND_FROM_LOCAL = False

if __name__ == "__main__":
    conn = pybit.local_rpc_channel()  # will use read_default_config
    assert conn.getinfo().testnet # don't test on prodnet

    test_sender1 = "mqo6ZdP2AM6SRxYd5arTW29K2u4rr9Yz1F"
    test_sender2 = "n3KGzq4SCB2boWDYXkgBL4TaNMXLdRuXvQ"
    test_receiver1 = "mpdptxB1Xy6p9rUpgQDnGenewK1AVFTjti"
    test_receiver2 = "mp7tFikT9eCLDYCW3PUzyLK6WHx4zGRchn"

    payments = {test_receiver1: 15, test_receiver2: 15}
    from_addresses = [test_sender1, test_sender2]
    fee = 0
    tx = pybit.send_from_local(payments, from_addresses=from_addresses, fee=fee, change_address=test_sender1)
    print tx
