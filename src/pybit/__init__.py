from pybit import util
from pybit import settings
from pybit import exceptions
from types import Block, Transaction


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
    rcp_user = cfg.get('rpcuser', '')

    return BitcoinConnection(rcp_user, cfg['rpcpassword'], 'localhost', port)


def get_block_count(**kwargs):
    """
    optional paramters:
    source: setting.SOURCE_BLOCKCHAIN_INFO or settings.SOURCE_LOCAL or settings.SOURCE_BLOCKEXPLORER_COM
    test_net: True or False
    config_file_name: local config file name
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
        if test_net != rpc.getinfo().testnet:
            raise exceptions.BitcoindStateError(test_net=test_net, rpc_test_net=rpc.getinfo().testnet)
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
    optional paramters:
    source: setting.SOURCE_BLOCKCHAIN_INFO or settings.SOURCE_LOCAL or settings.SOURCE_BLOCKEXPLORER_COM
    test_net: True or False

    :type block_hash: str
    :rtype Block:
    """
    if settings.USE_FAKE_DATA:
        return settings.FAKE_DATA_GET_BLOCK_BY_HASH[block_hash]

    source = kwargs.get('source', settings.SOURCE_LOCAL)
    test_net = kwargs.get('test_net', settings.TEST_NET)

    if source == settings.SOURCE_BLOCKCHAIN_INFO:
        if test_net:
            raise exceptions.OperationNotSupportedError('test_net is not supported in blockchain.info')
        else:
            return util.populate_block__block_chain_dot_info(
                util.fetch_json('http://blockchain.info/rawblock/%s' % block_hash), **kwargs)
    elif source == settings.SOURCE_LOCAL:
        rpc = local_rpc_channel(kwargs.get('config_file_name'))
        if test_net != rpc.getinfo().testnet:
            raise exceptions.BitcoindStateError(test_net=test_net, rpc_test_net=rpc.getinfo().testnet)
        return util.retrieve_block__local(rpc, block_hash)
    elif source == settings.SOURCE_BLOCKEXPLORER_COM:
        if test_net:
            html_url = "http://blockexplorer.com/testnet/block/" + block_hash
            raw_block_url = "http://blockexplorer.com/testnet/rawblock/" + block_hash
        else:
            html_url = "http://blockexplorer.com/block/" + block_hash
            raw_block_url = "http://blockexplorer.com/rawblock/" + block_hash

        return util.retrieve_block__block_explorer_dot_com(html_url, raw_block_url)
    else:
        raise exceptions.OperationNotSupportedError(source=source)


def get_block_by_height(height, **kwargs):
    """
    optional paramters:
    source: setting.SOURCE_BLOCKCHAIN_INFO or settings.SOURCE_LOCAL or settings.SOURCE_BLOCKEXPLORER_COM
    test_net: True or False

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
            all_blocks = util.fetch_json('http://blockchain.info/block-height/%d?format=json' % height)['blocks']
            return util.populate_block__block_chain_dot_info(
                [b for b in all_blocks if b.get('main_chain') is True][0], **kwargs)
    elif source == settings.SOURCE_LOCAL:
        rpc = local_rpc_channel(kwargs.get('config_file_name'))
        if test_net != rpc.getinfo().testnet:
            raise exceptions.BitcoindStateError(test_net=test_net, rpc_test_net=rpc.getinfo().testnet)
        block_hash = rpc.getblockhash(height)
        return util.retrieve_block__local(rpc, block_hash,
                                          only_wallet_transactions=kwargs.get('only_wallet_transactions', False))
    elif source == settings.SOURCE_BLOCKEXPLORER_COM:
        if test_net:
            html_url = "http://blockexplorer.com/testnet/b/" + str(height)
        else:
            html_url = "http://blockexplorer.com/b/" + str(height)

        block_hash = util.get_block_hash__block_explorer_dot_com(html_url)
        if test_net:
            raw_block_url = "http://blockexplorer.com/testnet/rawblock/" + block_hash
        else:
            raw_block_url = "http://blockexplorer.com/rawblock/" + block_hash

        return util.retrieve_block__block_explorer_dot_com(html_url, raw_block_url)
    else:
        raise exceptions.OperationNotSupportedError(source=source)


def send_from_local(payments, **kwargs):
    """
    optional paramaters:
    change_address: str. will use a new address if not provided
    from_addresses: can be a list of str or str
    min_conf: min confirmation, default is 1
    max_conf: max confirmation, default is 9999
    fee: default is getinfo().fee. unit is BTC
    wallet_pwd: str
    return_signed_transaction: True or False, if True, the return value is transaction_hash, transaction; if False, the
     return value is transaction_hash

    note: the wallet will be locked after this op if it is encrypted

    :type payments: dict
    :param payments: payments are in BTC
    :rtype: str or tuple
    """
    if settings.IGNORE_SEND_FROM_LOCAL:
        if kwargs.get('return_signed_transaction'):
            return '0'*30, '0'*100
        return '0'*30  # a fake transaction id

    from decimal import Decimal
    from pybit.exceptions import NotEnoughFundError, ChangeAddressIllegitError, WalletWrongEncState, \
        SignRawTransactionFailedError, BitcoindStateError

    #check types, turn all amounts to Decimal
    _payments = {}
    for address, amount in payments.iteritems():
        if not isinstance(amount, (Decimal, int, long)):
            raise TypeError('only Decimal, int and long is allowed for the type of amount')
        _payments[address] = Decimal(amount)
    payments = _payments

    rpc = local_rpc_channel(kwargs.get('config_file_name'))

    fee = kwargs.get('fee', rpc.getinfo().paytxfee)
    if not isinstance(fee, (Decimal, int, long)):
        raise TypeError('fee must be Decimal, int, or long')

    if settings.USE_FAKE_DATA or kwargs.get('test_net', settings.TEST_NET):  # in this case, testnet is enforced
        if not rpc.getinfo().testnet:
            raise BitcoindStateError(settings_USE_FAKE_DATA=settings.USE_FAKE_DATA,
                                     kwargs_test_net=kwargs.get('test_net'),
                                     settings_TEST_NET=settings.TEST_NET,
                                     rpc_testnet=rpc.getinfo().testnet)

    from_addresses = kwargs.get('from_addresses')
    if isinstance(from_addresses, str):
        from_addresses = [from_addresses]
    min_conf = kwargs.get('min_conf', 1)
    max_conf = kwargs.get('max_conf', 9999)

    if from_addresses is None:
        unspent = rpc.listunspent(min_conf, max_conf)
    else:
        unspent = [t for t in rpc.listunspent(min_conf, max_conf) if t.address in from_addresses]

    send_sum = sum(payments.values())
    unspent_sum = sum([t.amount for t in unspent])

    if unspent_sum < send_sum + fee:
        raise NotEnoughFundError(unspent=unspent, unspent_sum=unspent_sum, send_sum=send_sum, fee=fee)

    #select unspent
    unspent.sort(key=lambda t: t.confirmations, reverse=True)

    chosen = []
    for t in unspent:
        if sum([c.amount for c in chosen]) < send_sum + fee:
            chosen.append(t)
        else:
            break

    change = sum([c.amount for c in chosen]) - fee - send_sum
    change_address = kwargs.get('change_address')
    if change > 0:
        if change_address is None:
            change_address = rpc.getnewaddress()
        if change_address in payments:
            raise ChangeAddressIllegitError(change_address=change_address, payments=payments)
        payments[change_address] = change

    #compose raw transaction
    raw_tx = rpc.createrawtransaction([{'txid':c.txid, 'vout':c.vout} for c in chosen], payments)

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
        sign_rst = rpc.signrawtransaction(raw_tx)
        if sign_rst['complete'] == 0:
            raise SignRawTransactionFailedError(sign_result=sign_rst)

        #send the signed raw transaction to the network
        tx_hash = rpc.sendrawtransaction(sign_rst['hex'])

        if kwargs.get('return_signed_transaction', False):
            return tx_hash, sign_rst['hex']
        else:
            return tx_hash
    finally:
        #lock the wallet
        if wallet_pwd:
            try:
                rpc.walletlock()
            except WalletWrongEncState:
                pass

