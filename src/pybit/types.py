# Copyright (c) 2013 Rex <fdrex1987@gmail.com>
# Copyright (c) 2010 Witchspace <witchspace81@gmail.com>

from copy import copy


class DynamicStruct(object):
    """
    Simple dynamic structure, like :const:`collections.namedtuple` but more flexible
    (and less memory-efficient)
    """
    # Default arguments. Defaults are *shallow copied*, to allow defaults such as [].
    _fields = []
    _defaults = {}

    def __init__(self, *args_t, **args_d):
        # order
        if len(args_t) > len(self._fields):
            raise TypeError("Number of arguments is larger than of predefined fields")
            # Copy default values
        for (k, v) in self._defaults.items():
            self.__dict__[k] = copy(v)
            # Set pass by value arguments
        self.__dict__.update(zip(self._fields, args_t))
        # dict
        self.__dict__.update(args_d)

    def __repr__(self):
        return '{module}.{classname}({slots})'.format(
            module=self.__class__.__module__,
            classname=self.__class__.__name__,
            slots=", ".join('{k}={v!r}'.format(k=k, v=v) for k, v in self.__dict__.items()))


class ServerInfo(DynamicStruct):
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


class AccountInfo(DynamicStruct):
    """
    Information object returned by :func:`~pybit.connection.BitcoinConnection.listreceivedbyaccount`.

    - *account* -- The account of the receiving address.

    - *amount* -- Total amount received by the address.

    - *confirmations* -- Number of confirmations of the most recent transaction included.

    """


class AddressInfo(DynamicStruct):
    """
    Information object returned by :func:`~pybit.connection.BitcoinConnection.listreceivedbyaddress`.

    - *address* -- Receiving address.

    - *account* -- The account of the receiving address.

    - *amount* -- Total amount received by the address.

    - *confirmations* -- Number of confirmations of the most recent transaction included.

    """


class TransactionInfo(DynamicStruct):
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


class AddressValidation(DynamicStruct):
    """
    Information object returned by :func:`~pybit.connection.BitcoinConnection.validateaddress`.

    - *isvalid* -- Validatity of address (:const:`True` or :const:`False`).

    - *ismine* -- :const:`True` if the address is in the server's wallet.

    - *address* -- Bitcoin address.

    """


class WorkItem(DynamicStruct):
    """
    Information object returned by :func:`~pybit.connection.BitcoinConnection.getwork`.

    - *midstate* -- Precomputed hash state after hashing the first half of the data.

    - *data* -- Block data.

    - *hash1* -- Formatted hash buffer for second hash.

    - *target* -- Little endian hash target.

    """


class MiningInfo(DynamicStruct):
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


class Printable(object):
    def __str__(self):
        contents = '\n'.join([k+' : ' + str(v) for k, v in self.__dict__.iteritems() if not k.startswith('_')])
        return self.__class__.__name__ + " : [\n" + contents + "\n]\n"

    def __unicode__(self):
        return unicode(str(self))

    __repr__ = __str__


class Transaction(Printable):
    def __init__(self, input_addresses, outputs, hash):
        """
        :type input_addresses: list of str
        :type outputs: list of (n, address, amount)
        :param outputs: amount is int, in Satoshi, not in BTC
        :type hash: str
        """
        assert isinstance(input_addresses, list)
        assert isinstance(outputs, list)
        assert isinstance(hash, (str, unicode))

        self.input_addresses = input_addresses
        self.outputs = outputs
        self.hash = hash


class Block(Printable):
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