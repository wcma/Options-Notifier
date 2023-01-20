import boto3
import csv
import datetime
import json
import options_constants
import requests
import time
import yfinance

def _next_friday():
    today = datetime.date.today()
    next_friday = (today + datetime.timedelta((4 - today.weekday()) % 7))
    if (next_friday - today).days < 3:
        following_friday = next_friday + datetime.timedelta(weeks=1)
        return str(following_friday)
    else:
        return str(next_friday)


def _get_options(stock_symbol):
    ALPHA_VANTAGE_URL = f"https://www.alphavantage.co/query?function=TIME_SERIES_INTRADAY_EXTENDED&symbol={stock_symbol}&interval=15min&slice=year1month1&apikey={options_constants.ALPHA_VANTAGE_API_KEY}"
    current_price = ''

    with requests.Session() as s:
        download = s.get(ALPHA_VANTAGE_URL)
        decoded_content = download.content.decode('utf-8')
        cr = csv.reader(decoded_content.splitlines(), delimiter=',')
        my_list = list(cr)
        current_price = my_list[1][1]
    ideal_strike = float(current_price) * 0.9
    ticker_ob = yfinance.Ticker(stock_symbol)
    today = datetime.date.today()
    next_friday_expiration_date = _next_friday()
    options_results = f"Expiration date: {next_friday_expiration_date} "
    result = ticker_ob.option_chain(next_friday_expiration_date)
    rr = result.puts.sort_values('strike')
    rrr = rr.loc[rr['strike'] < ideal_strike ]
    for index, row in rrr.tail(2).iterrows():
        bid_value = rrr.at[index, 'bid']
        strike_value = rrr.at[index, 'strike']
        options_results = f"{options_results}Strike: {strike_value} Bid: {bid_value} "
    time.sleep(0.5)
    return options_results


def _publish(msg):
    message = {'options': msg}
    client = boto3.client('sns')
    response = client.publish(
        TargetArn=options_constants.SNS_ARN,
        Message=json.dumps({'default': json.dumps(message)}),
        MessageStructure='json'
    )


def compiler(event, context):
    stocks_list = options_constants.STOCKS_LIST
    message = ""
    for s in stocks_list:
        result = _get_options(s)
        message = f"{message}{s} - {result}"
    _publish(message)
    return {
        'message': 'Success!'
    }
if __name__ == '__main__':
    print(compiler(None, None))
    
