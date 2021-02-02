import json
import kraken_manager
import kraken_bot
import requests
import uuid
import orm

# print(kraken_manager.get_current_price(['XBTUSDT', 'ETHUSDT']))


# result = kraken_manager.get_open_orders()

# with open('tests.json', 'w') as outfile:
#     json.dump(result, outfile)

# request = kraken_manager.ApiRequest(url='https://api.kraken.com/0/private/OpenOrders')
# request._sign()

# result = kraken_manager.post_order(pair='XBTUSDT', type='sell', price=63000, volume=0.001)
# print(result)
#
# result = kraken_manager.cancel_order(id=result['id'])
# print(result)

def test_start_robot():
    strategies = orm.Strategy.get_all()
    print(strategies)
    price = kraken_manager.get_current_price(['XBTUSDT'])['XBTUSDT']
    print(price)
    bot = kraken_bot.Bot(strategies[0], price)
    bot.start_robot()

test_start_robot()
