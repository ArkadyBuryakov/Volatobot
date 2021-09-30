import krakenex
from settings import KRAKEN_KEY, KRAKEN_PRIVATE_KEY

# Instantiate an instance of kraken api
k = krakenex.API()
k.key = KRAKEN_KEY
k.secret = KRAKEN_PRIVATE_KEY


class KrakenApiException(Exception):
    pass


class KrakenApiTemporaryLockoutException(Exception):
    # via https://support.kraken.com/hc/en-us/articles/360001491786-API-error-messages
    DELAY = 15 * 60
    pass


def raise_appropriate_kraken_api_exception(error: str):  # todo: maybe it can be better
    """Find specified error, if no: raise KrakenApiException finally."""

    if error.startswith('EGeneral:Temporary lockout'):
        raise KrakenApiTemporaryLockoutException(error)

    raise KrakenApiException(errors)


def extract_result(json_response):
    try:
        if not json_response['error']:
            if json_response['result']:
                return json_response['result']
            else:
                raise KrakenApiException('empty result')
        else:
            raise_appropriate_kraken_api_exception(json_response['error'])

    except Exception as e:
        raise KrakenApiException('extract_result: ' + str(e))


def extract_orders(raw_order_list):
    result = {}

    for order_id, order_info in raw_order_list.items():
        order = {'id': order_id,
                 'type': order_info['descr']['type'],
                 'amount': float(order_info['vol']),
                 'price': float(order_info['descr']['price']),
                 'open_position': float(order_info['vol']) - float(order_info['vol_exec']),
                 'closed_position': float(order_info['vol_exec']),
                 'status': order_info['status']}
        result[order_id] = order

    return result


def get_current_price(pairs: list):
    # Prepare a parameter with currency pairs list
    pair_list = ''
    for pair in pairs:
        pair_list += f'{pair},'
    pair_list = pair_list[:-1]

    # Call Kraken API and get response
    try:
        response_result = k.query_public(method='Ticker', data={'pair': pair_list})
    except Exception as e:
        raise KrakenApiException('get_current_price: ' + str(e))

    # Generate easy to use result
    result = {}

    try:
        raw_result = extract_result(response_result)
        # fill result with pair prices
        for pair_name, price_info in raw_result.items():
            result[pair_name] = float(price_info['c'][0])

    except KrakenApiException as e:
        raise KrakenApiException('get_current_price: ' + str(e))

    # Finish
    return result


def get_open_orders():
    # Call Kraken API and get response
    try:
        response_result = k.query_private(method='OpenOrders')
    except Exception as e:
        raise KrakenApiException('get_open_orders: ' + str(e))

    # Generate easy to use result
    try:
        raw_result = extract_result(response_result)
        result = extract_orders(raw_result['open'])

    except KrakenApiException as e:
        raise KrakenApiException('get_open_orders: ' + str(e))

    # Finish
    return result


def query_orders(id_list):
    order_txid = ''

    for order_id in id_list[0: 50]:  # API allows maximum 50 id's
        order_txid += order_id + ','
    order_txid = order_txid[:-1]

    data = {'txid': order_txid}

    # Call Kraken API and get response
    try:
        response_result = k.query_private(method='QueryOrders', data=data)
    except KrakenApiException as e:
        raise KrakenApiException('query_orders: ' + str(e))

    # Generate easy to use result
    try:
        raw_result = extract_result(response_result)
        result = extract_orders(raw_result)

    except KrakenApiException as e:
        raise KrakenApiException('query_orders: ' + str(e))

    return result


def post_order(pair, type, price, volume, order_type="limit"):
    # Form data for request
    data = {'pair': pair,
            'type': type,
            'ordertype': order_type,
            'price': price,
            'volume': volume}

    # Post order via API
    try:
        response_result = k.query_private(method='AddOrder', data=data)
    except Exception as e:
        raise KrakenApiException('post_order: ' + str(e))

    # Generate easy to use result
    result = {}

    try:
        raw_result = extract_result(response_result)
        result['id'] = raw_result['txid'][0]
        result['descr'] = raw_result['descr']['order']
    except KrakenApiException as e:
        raise KrakenApiException('post_order: ' + str(e))

    # Finish
    return result


def cancel_order(id):
    # Form data for request
    data = {'txid': id}

    # Post order via API
    try:
        response_result = k.query_private(method='CancelOrder', data=data)
    except Exception as e:
        raise KrakenApiException('cancel_order: ' + str(e))

    # Generate easy to use result
    result = {}

    try:
        raw_result = extract_result(response_result)
        result['count'] = raw_result['count']
    except KrakenApiException as e:
        raise KrakenApiException('cancel_order: ' + str(e))

    # Finish
    return result
