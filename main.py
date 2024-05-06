import argparse
import csv
import os
from datetime import datetime, timedelta
import pandas as pd

import requests
from dateutil import parser as dateparser
from dotenv import load_dotenv
from oandapyV20 import API
from oandapyV20.contrib.factories import InstrumentsCandlesFactory

import src

load_dotenv()

log = src.logger_config.logger

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

# Place where fetched files will be stored
DATA_DIR = ".\\data"

args = parser.parse_args()

date_format = "%Y-%m-%dT%H:%M:%SZ"

params = {
    "instrument": "EUR_USD",
    "granularity": "M15",
    "start_date": dateparser.isoparse(args.startDate).strftime(date_format),
    "end_date": dateparser.isoparse(args.endDate).strftime(date_format),
    "count": 5000,
}

if not os.path.exists(DATA_DIR):
    os.makedirs(DATA_DIR)

filename = f"{DATA_DIR}\\{params['instrument']}_{params['granularity']}_from_{params['start_date'].replace(':', '-')}_to_{params['end_date'].replace(':', '-')}.csv"


def get_dataframe(
    instrument=params["instrument"],
    params=params,
    filename=filename,
    end_date=params["end_date"],
):
    with open(filename, "w", newline="") as file:
        writer = csv.writer(file)

        writer.writerow(["time", "open", "high", "low", "close", "volume", "complete"])

        while True:

            for r in InstrumentsCandlesFactory(
                instrument=params["instrument"],
                params={
                    "from": params["start_date"],
                    "granularity": params["granularity"],
                    "count": params["count"],
                },
            ):
                client.request(r)
                for candle in r.response.get("candles"):
                    if candle["complete"]:
                        time = candle["time"][:26]
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
                r.response.get("candles")[-1]["time"][:26],
                time_format,
            )
            if last_candle_time >= dateparser.isoparse(end_date).replace(tzinfo=None):
                break

            params["from"] = (last_candle_time + timedelta(minutes=15)).strftime(
                time_format,
            )
    log.info(f"Data has been saved to {filename}")


if __name__ == "__main__":
    get_dataframe()

    #Path to the CSV file 
    file_path = filename

    #Function to load data with datetime parsing
    def load_data(df):
        df["time"] = pd.to_datetime(df["time"], unit="s")
        return df
    
    #Load the data
    df = load_data(file_path)
    print(df.info())
