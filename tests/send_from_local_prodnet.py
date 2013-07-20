__author__ = 'Rex'


import sys
sys.path.append('../src')

import pybit
from pybit import settings
from decimal import Decimal


if __name__ == "__main__":
    settings.IGNORE_SEND_FROM_LOCAL = False
    settings.TEST_NET = False
    settings.USE_FAKE_DATA = False

    conn = pybit.local_rpc_channel()  # will use read_default_config
    assert not conn.getinfo().testnet # test on prodnet

    sender = "13bRqs7QiUNjw27L1Z6wPzn8DakPipnpdA"
    receiver1 = "1F8xHghqtgKWmR6xe2MfTqcZMDNaTytkec"
    receiver2 = "189tPVgiLiGdSjH6qSWWxvEBCVJnKmR2Uz"

    payments = {receiver1: Decimal("0.02"), receiver2: Decimal("0.02")}
    from_addresses = [sender]
    fee = Decimal("0")  # no fee
    #fee = Decimal("0.001")  # add fee
    tx = pybit.send_from_local(payments, from_addresses=from_addresses, fee=fee, change_address=sender)
    print tx
