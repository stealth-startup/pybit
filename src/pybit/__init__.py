from pybit import util
from pybit import settings
from pybit import exceptions
from data import Block, Transaction


def local_rpc_channel(config_file_name=None):
    """
    Connect to default bitcoin instance owned by this user, on this machine.

    Returns a :class:`~bitcoinrpc.connection.BitcoinConnection` object.

    Arguments:

        - `filename`: Path to a configuration file in a non-standard location (optional)
    """
    from pybit.connection import BitcoinConnection
    from pybit.config import read_default_config

    cfg = read_default_config(config_file_name)
    port = int(cfg.get('rpcport', '18332' if cfg.get('testnet') else '8332'))
    rcpuser = cfg.get('rpcuser', '')

    return BitcoinConnection(rcpuser, cfg['rpcpassword'], 'localhost', port)


def get_block_count(**kwargs):
    """
    :rtype: int
    """
    if settings.USE_FAKE_DATA:
        return settings.FAKE_DATA_GET_BLOCK_COUNT

    source = kwargs.get('source', settings.SOURCE_LOCAL)
    test_net = kwargs.get('test_net', settings.TEST_NET)

    if source == settings.SOURCE_BLOCKCHAIN_INFO:
        if test_net:
            raise exceptions.OperationNotSupportedError('test_net is not supported in blockchain.info')
        else:
            return int(util.fetch_data('https://blockchain.info/q/getblockcount'))
    elif source == settings.SOURCE_LOCAL:
        rpc = local_rpc_channel(kwargs.get('config_file_name'))
        if test_net:
            assert rpc.getinfo().testnet
        return rpc.getblockcount()
    elif source == settings.SOURCE_BLOCKEXPLORER_COM:
        if test_net:
            return int(util.fetch_data('https://blockexplorer.com/q/testnet/getblockcount'))
        else:
            return int(util.fetch_data('https://blockexplorer.com/q/getblockcount'))
    else:
        raise exceptions.OperationNotSupportedError(source=source)


def get_block_by_hash(block_hash, **kwargs):
    """
    :type hash: str
    :rtype Block:
    """
    if settings.USE_FAKE_DATA:
        return settings.FAKE_DATA_GET_BLOCK_BY_HASH['block_hash']

    source = kwargs.get('source', settings.SOURCE_LOCAL)
    test_net = kwargs.get('test_net', settings.TEST_NET)

    if source == settings.SOURCE_BLOCKCHAIN_INFO:
        if test_net:
            raise exceptions.OperationNotSupportedError('test_net is not supported in blockchain.info')
        else:
            return util.populate_block(util.fetch_json('http://blockchain.info/rawblock/%s' % block_hash))
    elif source == settings.SOURCE_LOCAL:
        raise exceptions.OperationNotSupportedError('local rpc does not support this operation')
    elif source == settings.SOURCE_BLOCKEXPLORER_COM:
        raise exceptions.OperationNotSupportedError('not implement yet')
    else:
        raise exceptions.OperationNotSupportedError(source=source)


def get_block_by_height(height, **kwargs):
    """
    :type height: int
    :rtype: Block
    """
    if settings.USE_FAKE_DATA:
        return settings.FAKE_DATA_GET_BLOCK_BY_HEIGHT[height]

    source = kwargs.get('source', settings.SOURCE_LOCAL)
    test_net = kwargs.get('test_net', settings.TEST_NET)

    if source == settings.SOURCE_BLOCKCHAIN_INFO:
        if test_net:
            raise exceptions.OperationNotSupportedError('test_net is not supported in blockchain.info')
        else:
            all_blocks = util.fetch_json('http://blockchain.info/block-height/%d?format=json' % height)
            return util.populate_block([b for b in all_blocks if b.get('main_chain') is True][0])
    elif source == settings.SOURCE_LOCAL:
        raise exceptions.OperationNotSupportedError('local rpc does not support this operation')
    elif source == settings.SOURCE_BLOCKEXPLORER_COM:
        #code picked up from old openexchangelib source code
        # import re
        # blockhash = re.search('00000000[0-9a-fA-F]+', util.fetch_data('http://blockexplorer.com/testnet/b/%d' % height)).group()
        # data = fetch_json_data("http://blockexplorer.com/testnet/rawblock/%s" % blockhash)
        raise exceptions.OperationNotSupportedError('not implement yet')
    else:
        raise exceptions.OperationNotSupportedError(source=source)


def send_from_local(payments, **kwargs):
    """
    optional paramaters:
    change_address: will use a new address by default, however, you can specify a address as the change address
    from_addresses: can be a list of str or str
    min_conf: min confirmation
    max_conf: max confirmation

    note: the wallet will be locked after this op if it is encrypted
    :type from_addresses: str or list of str
    :type payments: dict from str to int
    :param payments: payments are in Satoshi
    """
    if settings.IGNORE_SEND_FROM_LOCAL:
        return '0'*30  # a fake transaction id

    from pybit.exceptions import NotEnoughFundError, ChangeAddressIllegitError, WalletWrongEncState, \
        SignRawTransactionFailedError
    import decimal

    rpc = local_rpc_channel()

    if settings.USE_FAKE_DATA or kwargs.get('test_net', settings.TEST_NET):  # in this case, testnet is enforced
        assert rpc.getinfo().testnet

    from_addresses = kwargs.get('from_addresses')
    if isinstance(from_addresses, str):
        from_addresses = [from_addresses]
    min_conf = kwargs.get('min_conf', 1)
    max_conf = kwargs.get('max_conf', 9999)

    if from_addresses is None:
        unspent = rpc.listunspent(min_conf, max_conf)
    else:
        unspent = [t for t in rpc.listunspent(min_conf, max_conf) if t.address in [from_addresses]]

    for v in payments.values():
        assert isinstance(v, (int, long))
    send_sum = decimal.Decimal(sum(payments.values())) / 100000000
    unspent_sum = sum([t.amount for t in unspent])
    fee = kwargs.get('fee', rpc.getinfo().paytxfee)

    if unspent_sum < send_sum + fee:
        raise NotEnoughFundError(unspent=unspent, unspent_sum=unspent_sum, send_sum=send_sum, fee=fee)

    #select unspent
    unspent.sort(key=lambda t: t.confirmations, reverse=True)

    chosen = []
    while sum(chosen) < send_sum + fee:
        chosen.append(t)

    change = sum(chosen) - fee - send_sum
    change_address = kwargs.get('change_address')
    if change > 0:
        payments = dict(payments)  # make a copy of payments so that the original object won't be changed
        if change_address is None:
            change_address = rpc.getnewaddress()
        if change_address in payments:
            raise ChangeAddressIllegitError(change_address=change_address, payments=payments)
        payments[change_address] = int(round(float(change) * 100000000))

    #compose raw transaction
    raw_tx = rpc.createrawtransaction(
        [{'txid':c.txid, 'vout':c.vout} for c in chosen],
        {address: v/100000000.0 for address, v in payments.iteritems()}
    )

    wallet_pwd = kwargs.get('wallet_pwd')
    try:
        #make sure the wallet is not locked
        if wallet_pwd:
            try:
                rpc.walletlock()  # lock the wallet so we make sure it has sufficient time in the later process
            except WalletWrongEncState:
                pass
            rpc.walletpassphrase(wallet_pwd, 10)  # unlock the wallet

        #sign raw transaction
        rst = rpc.signrawtransaction(raw_tx)
        if rst['complete'] == 0:
            raise SignRawTransactionFailedError(sign_result=rst)

        #send the signed raw transaction to the network
        return rpc.sendrawtransaction(rst['hex'])
    finally:
        #lock the wallet
        if wallet_pwd:
            try:
                rpc.walletlock()
            except WalletWrongEncState:
                pass

