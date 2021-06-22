from yfinance import Ticker
import time
import json

settings = json.load(open("settings.json", "r"))
tickers_description = settings["tickersDescription"]
tickers_exchange = settings["tickersExchange"]
tickers_exchange_timezone = settings["tickersExchangeTimezone"]
tickers_currency = settings["tickersCurrency"]


def basic(asset_name):
    """
    Returns basic statistics about an asset:
    - current price;
    - change for day %;
    - long name.
    """
    ticker = Ticker(asset_name)
    # Sometimes yfinance returns one-day statistics if the period is 2d,
    # so request 3 days period and consume only the last 2 days
    asset_history = ticker.history(period='3d').dropna(subset=['Close'])
    yesterday_info = asset_history.iloc[-2]
    today_info = asset_history.iloc[-1]
    previous_close = float(yesterday_info.get('Close'))
    current_price = float(today_info.get('Close'))
    return {
        'current_price': current_price,
        'change_for_day': current_price * 100.0 / previous_close - 100.0,
        'long_name': tickers_description.get(asset_name),
    }


def detailed(asset_name):
    """
    Returns detailed statistics about an asset:
    - long name;
    - exchange;
    - timezone;
    - currency;
    - datetime;
    - current price;
    - change for day;
    - change for day %;
    - volume;
    - previous close;
    - day range;
    - year range;
    - forward dividend;
    - dividend yield.
    """
    ticker = Ticker(asset_name)
    year_info = ticker.history(period='1y').dropna(subset=['Close'])
    yesterday_info = year_info.iloc[-2]
    today_info = year_info.iloc[-1]
    previous_close = float(yesterday_info.get('Close'))
    current_price = float(today_info.get('Close'))
    return {
        'previous_close': previous_close,
        'current_price': current_price,
        'change_for_day': current_price * 100.0 / previous_close - 100.0,
        'change_for_day_sum': current_price - previous_close,

        'volume': today_info.get('Volume'),
        'day_range_low': today_info.get('Low'),
        'day_range_high': today_info.get('High'),
        'year_range_low': year_info['Low'].min(),
        'year_range_high': year_info['High'].max(),

        'long_name': tickers_description.get(asset_name),
        'exchange': tickers_exchange.get(asset_name),
        'timezone': tickers_exchange_timezone,
        'currency': tickers_currency,

        'timestamp': round(time.time()),
    }


def history(asset_name, period='5mo'):
    """
    Returns history for the specified period of time in format `timestamp: price at day start`.
    """
    asset = Ticker(asset_name)
    return asset.history(period).dropna(subset=['Open']).loc[:, 'Open'].to_json()
