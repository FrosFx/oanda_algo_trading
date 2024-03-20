import json
import os
from operator import __not__

import oandapyV20.endpoints.trades as trades
from dotenv import load_dotenv
from oandapyV20 import API

load_dotenv()

api = API(access_token=os.getenv(ACCESS_TOKEN))
accountID = os.getenv(ACCOUNT_ID)

r = trades.TradesList(accountID)

# Show the endpoint as it is constructed for this call

print("REQUEST:{}".format(r))
rv = api.request(r)
print("RESPONSE:\n{}".format(json.dumps(rv, indent=2)))
