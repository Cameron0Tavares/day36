import requests
import json
from datetime import date
from pandas.tseries.offsets import BDay
from twilio.rest import Client


def get_keys(path):
    with open(path) as f:
        return json.load(f)


def sig_change(stock_prev, stock_curr):
    num1 = float(stock_prev)
    num2 = float(stock_curr)
    perc = (num2 - num1)/num1
    return perc


STOCK = "TSLA"
COMP_NAME = "Tesla Inc"
ARTICLE_NUM = 3
STOCK_ENDPOINT = 'https://www.alphavantage.co/query?'
NEWS_ENDPOINT = 'https://newsapi.org/v2/everything?'

## STEP 1: Use https://www.alphavantage.co
# When STOCK price increase/decreases by 5% between yesterday and the day before yesterday then print("Get News").
# Get the dates to compare
today_dt = date.today() - BDay(1)
yeste_dt = today_dt - BDay(2)
today = today_dt.strftime("%Y-%m-%d")
yeste = yeste_dt.strftime("%Y-%m-%d")

av_token = get_keys('/Users/camerontavares/.secret/alphavantage_api.json')['api_key']

stock_params = {
    'function': 'TIME_SERIES_DAILY_ADJUSTED',
    'symbol': STOCK,
    'apikey': av_token
}

avr = requests.get(STOCK_ENDPOINT, params=stock_params)
av_data = avr.json()

# print(json.dumps(av_data, indent=4))

today_open = av_data['Time Series (Daily)'][today]['1. open']
yeste_open = av_data['Time Series (Daily)'][yeste]['1. open']
perc_change = 100*sig_change(yeste_open, today_open)

## STEP 2: Use https://newsapi.org
# Instead of printing ("Get News"), actually get the first 3 news pieces for the COMPANY_NAME.


def build_sms():
    nw_token = get_keys('/Users/camerontavares/.secret/newsapi_api.json')['api_key']
    news_params = {
        'q': COMP_NAME,
        'from': today,
        'sortBy': 'popularity',
        'pageSize': 1,
        'apiKey': nw_token
    }
    nwr = requests.get(NEWS_ENDPOINT, params=news_params)
    nw_data = nwr.json()

    # print(json.dumps(nw_data, indent=2))

    headline = nw_data['articles'][0]['title']
    brief = nw_data['articles'][0]['description']
    sms_text = (
        f'{STOCK}: {perc_change:.2f}%\n'
        f'Headline: {headline}\n'
        f'Brief: {brief}'
    )
    return sms_text


## STEP 3: Use https://www.twilio.com
# Send a separate message with the percentage change and each article's title and description to your phone number.


def send_sms(sms_text):
    tw_sid = get_keys('/Users/camerontavares/.secret/twilio_api.json')['sid']
    tw_token = get_keys('/Users/camerontavares/.secret/twilio_api.json')['api_key']
    client = Client(tw_sid, tw_token)

    message = client.messages.create(
      body=sms_text,
      from_='+18563862857',
      to='+14066961846'
    )
    print(message.sid)
    print('Message sent!')


if abs(perc_change) >= 5:
    send_sms(build_sms())
else:
    print('Threshold not met, no message sent.')
