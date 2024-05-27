import oandapyV20
from oandapyV20.endpoints.accounts import AccountDetails
from dotenv import load_dotenv
import os

load_dotenv()

client = oandapyV20.API(access_token=os.getenv("ACCESS_TOKEN"))

account_id = os.getenv("ACCOUNT_ID")
r = AccountDetails(account_id)
try:
    response = client.request(r)
    print("API connection successful:", response)
except oandapyV20.exceptions.V20Error as e:
    print(f"An error occurred: {e}")
