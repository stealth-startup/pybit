__author__ = 'Rex'


import sys
sys.path.append('../src')

import pybit
from pybit import settings
from decimal import Decimal


if __name__ == "__main__":
    settings.IGNORE_SEND_FROM_LOCAL = False

    conn = pybit.local_rpc_channel()  # will use read_default_config
    assert conn.getinfo().testnet  # test on test net

    test1 = "mpdptxB1Xy6p9rUpgQDnGenewK1AVFTjti"
    test2 = "mp7tFikT9eCLDYCW3PUzyLK6WHx4zGRchn"
    test3 = "mqo6ZdP2AM6SRxYd5arTW29K2u4rr9Yz1F"
    test4 = "n3KGzq4SCB2boWDYXkgBL4TaNMXLdRuXvQ"

    print pybit.send_from_local(
        {test1: 15, test2: 15},
        from_addresses=['moxT1cTs2Jn6Sodhv53QpxQkqKaVKkgSnv'],
        fee=0,
        change_address='moxT1cTs2Jn6Sodhv53QpxQkqKaVKkgSnv',
        min_conf=0
    )

    print pybit.send_from_local(
        {test3: 15, test4: 15},
        from_addresses=[test1, test2],
        fee=0,
        change_address=test1,
        min_conf=0
    )

    print pybit.send_from_local(
        {test1: 15, test2: 15},
        from_addresses=[test3, test4],
        fee=0,
        change_address=test3,
        min_conf=0
    )

    print pybit.send_from_local(
        {test3: 15, test4: 15},
        from_addresses=[test1, test2],
        fee=0,
        change_address=test1,
        min_conf=0
    )

    print pybit.send_from_local(
        {test1: 15, test2: 15},
        from_addresses=[test3, test4],
        fee=0,
        change_address=test3,
        min_conf=0
    )

