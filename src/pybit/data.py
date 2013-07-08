# Copyright (c) 2013 Rex <fdrex1987@gmail.com>
# Copyright (c) 2010 Witchspace <witchspace81@gmail.com>

"""
Bitcoin RPC service, data objects.
"""
from pybit.util import DStruct


class ServerInfo(DStruct):
    """
    Information object returned by :func:`~bitcoinrpc.connection.BitcoinConnection.getinfo`.

    - *errors* -- Number of errors.

    - *blocks* -- Number of blocks.

    - *paytxfee* -- Amount of transaction fee to pay.

    - *keypoololdest* -- Oldest key in keypool.

    - *genproclimit* -- Processor limit for generation.

    - *connections* -- Number of connections to other clients.

    - *difficulty* -- Current generating difficulty.

    - *testnet* -- True if connected to testnet, False if on real network.

    - *version* -- Bitcoin client version.

    - *proxy* -- Proxy configured in client.

    - *hashespersec* -- Number of hashes per second (if generation enabled).

    - *balance* -- Total current server balance.

    - *generate* -- True if generation enabled, False if not.

    - *unlocked_until* -- Timestamp (seconds since epoch) after which the wallet
                          will be/was locked (if wallet encryption is enabled).

    """


class AccountInfo(DStruct):
    """
    Information object returned by :func:`~pybit.connection.BitcoinConnection.listreceivedbyaccount`.

    - *account* -- The account of the receiving address.

    - *amount* -- Total amount received by the address.

    - *confirmations* -- Number of confirmations of the most recent transaction included.

    """


class AddressInfo(DStruct):
    """
    Information object returned by :func:`~pybit.connection.BitcoinConnection.listreceivedbyaddress`.

    - *address* -- Receiving address.

    - *account* -- The account of the receiving address.

    - *amount* -- Total amount received by the address.

    - *confirmations* -- Number of confirmations of the most recent transaction included.

    """


class TransactionInfo(DStruct):
    """
    Information object returned by :func:`~pybit.connection.BitcoinConnection.listtransactions`.

    - *account* -- account name.

    - *address* -- the address bitcoins were sent to, or received from.
    
    - *category* -- will be generate, send, receive, or move.

    - *amount* -- amount of transaction.

    - *fee* -- Fee (if any) paid (only for send transactions).

    - *confirmations* -- number of confirmations (only for generate/send/receive).

    - *txid* -- transaction ID (only for generate/send/receive).

    - *otheraccount* -- account funds were moved to or from (only for move).

    - *message* -- message associated with transaction (only for send).

    - *to* -- message-to associated with transaction (only for send).
    """


class AddressValidation(DStruct):
    """
    Information object returned by :func:`~pybit.connection.BitcoinConnection.validateaddress`.

    - *isvalid* -- Validatity of address (:const:`True` or :const:`False`).

    - *ismine* -- :const:`True` if the address is in the server's wallet.

    - *address* -- Bitcoin address.

    """


class WorkItem(DStruct):
    """
    Information object returned by :func:`~pybit.connection.BitcoinConnection.getwork`.

    - *midstate* -- Precomputed hash state after hashing the first half of the data.

    - *data* -- Block data.

    - *hash1* -- Formatted hash buffer for second hash.

    - *target* -- Little endian hash target.

    """


class MiningInfo(DStruct):
    """
    Information object returned by :func:`~pybit.connection.BitcoinConnection.getmininginfo`.

    - *blocks* -- Number of blocks.

    - *currentblocksize* -- Size of current block.

    - *currentblocktx* -- Number of transactions in current block.

    - *difficulty* -- Current generating difficulty.

    - *errors* -- Number of errors.

    - *generate* -- True if generation enabled, False if not.

    - *genproclimit* -- Processor limit for generation.

    - *hashespersec* -- Number of hashes per second (if generation enabled).

    - *pooledtx* -- Number of pooled transactions.

    - *testnet* -- True if connected to testnet, False if on real network.

    """


class Transaction(object):
    def __init__(self, input_addresses, outputs, hash):
        """
        :type input_addresses: list of str
        :type outputs: list of (n, address, amount)
        :type hash: str
        """
        assert isinstance(input_addresses, list)
        assert isinstance(outputs, list)
        assert isinstance(hash, str)

        self.input_addresses = input_addresses
        self.outputs = outputs
        self.hash = hash

    def __str__(self):
        return 'input_addresses: %s, outputs: %s, hash: %s' % (str(self.input_addresses), str(self.outputs), self.hash)

    def __unicode__(self):
        return unicode(str(self))

    __repr__ = __str__


class Block(object):
    def __init__(self, height, hash, previous_hash, transactions, timestamp):
        """
        :type height: int
        :type hash: str
        :type previous_hash: str
        :type transactions: list of Transaction
        :type timestamp: Datetime
        """
        self.height = height
        self.hash = hash
        self.previous_hash = previous_hash
        self.transactions = transactions
        self.timestamp = timestamp

    def __str__(self):
        return 'height: %d, hash: %s, previous_hash: %s, timestamp: %s, transactions: %s' % (
            self.height, self.hash, self.previous_hash, str(self.timestamp), str(self.transactions))

    def __unicode__(self):
        return unicode(str(self))

    __repr__ = __str__