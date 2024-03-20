import argparse
import csv
import os
from datetime import datetime, timedelta

import requests
from dateutil import parser as dateparser
from dotenv import load_dotenv
from oandapyV20 import API
from oandapyV20.contrib.factories import InstrumentsCandlesFactory

import logger_config

load_dotenv()

log = logger_config.logger

access_token = os.getenv("ACCESS_TOKEN")
client = API(access_token=access_token)

parser = argparse.ArgumentParser(
    description="Fetch candlestick data from Oanda",
)
parser.add_argument(
    "--startDate",
    type=str,
    required=True,
    help="Start date for the data",
)
parser.add_argument(
    "--endDate",
    type=str,
    required=True,
    help="End date for the data",
)

args = parser.parse_args()

date_format = "%Y-%m-%dT%H:%M:%SZ"

data = {
    "instrument": "EUR_USD",
    "granularity": "M15",
    "start_date": dateparser.isoparse(args.startDate).strftime(date_format),
    "end_date": dateparser.isoparse(args.endDate).strftime(date_format),
}

params = {
    "granularity": data["granularity"],
    "from": data["start_date"],
    "count": 5000,
}


filename = f"{data['instrument']}_{data['granularity']}_from_{data['start_date']}_to_{data['end_date']}.csv"


def get_dataframe(
    instrument=data["instrument"],
    params=params,
    filename=filename,
    end_date=data["end_date"],
):
    with open(filename, "w", newline="") as file:
        writer = csv.writer(file)

        writer.writerow(["time", "open", "high", "low", "close", "volume", "complete"])

        while True:

            for r in InstrumentsCandlesFactory(instrument=instrument, params=params):
                client.request(r)
                for candle in r.response.get("candles"):
                    if candle["complete"]:
                        time = candle["time"][:26] + "Z"
                        price = candle["mid"]
                        writer.writerow(
                            [
                                time,
                                price["o"],
                                price["h"],
                                price["l"],
                                price["c"],
                                candle["volume"],
                                candle["complete"],
                            ]
                        )

                    log.info(f"Fetching data {candle['time']}")

            time_format = "%Y-%m-%dT%H:%M:%S.%fZ"

            last_candle_time = datetime.strptime(
                r.response.get("candles")[-1]["time"][:26] + "Z",
                time_format,
            )
            if last_candle_time >= dateparser.isoparse(end_date).replace(tzinfo=None):
                break

            params["from"] = (last_candle_time + timedelta(minutes=15)).strftime(
                time_format,
            )
    log.info(f"Data has been saved to {filename}")


get_dataframe()
