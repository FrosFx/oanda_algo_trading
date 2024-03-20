import csv
from datetime import datetime, timedelta
from oandapyV20 import API
from oandapyV20.contrib.factories import InstrumentsCandlesFactory


access_token = ''
client = API(access_token=access_token)

instrument = 'EUR_USD'
granularity = 'M15'
start_date = datetime(2014, 1, 1)
end_date = datetime.now() 


params = {
    'granularity': granularity,
    'from': start_date.strftime('%Y-%m-%dT%H:%M:%SZ'),  
    'count': 5000, 
}


filename = f"{instrument}_{granularity}_from_{start_date.strftime('%Y%m%d')}_to_{end_date.strftime('%Y%m%d')}.csv"


with open(filename, 'w', newline='') as file:
    writer = csv.writer(file)
    
    writer.writerow(['time', 'open', 'high', 'low', 'close', 'volume', 'complete'])

    while True:
        
        for r in InstrumentsCandlesFactory(instrument=instrument, params=params):
            client.request(r)
            for candle in r.response.get('candles'):
                if candle['complete']:
                    time = candle['time'][:26] + 'Z'  
                    price = candle['mid']  
                    writer.writerow([
                        time,
                        price['o'],
                        price['h'],
                        price['l'],
                        price['c'],
                        candle['volume'],
                        candle['complete']
                    ])

        
        last_candle_time = datetime.strptime(r.response.get('candles')[-1]['time'][:26] + 'Z', '%Y-%m-%dT%H:%M:%S.%fZ')
        if last_candle_time >= end_date:
            break

        
        params['from'] = (last_candle_time + timedelta(minutes=15)).strftime('%Y-%m-%dT%H:%M:%SZ')

print(f"Data has been saved to {filename}")
