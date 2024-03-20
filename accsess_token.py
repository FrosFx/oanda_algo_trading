from operator import __not__
from oandapyV20 import API
import oandapyV20.endpoints.trades as trades
import json


api = API(access_token='')
accountID = ''

r = trades.TradesList(accountID)

#Show the endpoint as it is constructed for this call

print("REQUEST:{}".format(r))
rv = api.request(r)
print("RESPONSE:\n{}".format(json.dumps(rv, indent=2)))

