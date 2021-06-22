from data_providers import (MarketQuotes, MarketReturns)
import logging
import sys


logger = logging.getLogger("capital-markets-data")
logging.basicConfig(
    level=logging.INFO,
    stream=sys.stdout,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    encoding="utf-8"
)

def capital_markets_returns(data, context):
    """ Cloud Function for fetching quotes, calculating returns, updating data in the GCS. """
    quotes = MarketQuotes().fit()
    try: 
        returns = MarketReturns(quotes).fit(quotes)
    except TypeError: 
        logger.info(f"No additional data to load. Fetching completed.")
