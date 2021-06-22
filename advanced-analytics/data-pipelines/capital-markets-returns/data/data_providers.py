""" Script for collecting, preprocessing capital markets data.

Required environment variables:
    - PROJECT_ID
    - QUOTES_BUCKET -- GCS bucket name with capital markets quotes data
    - QUOTES_BLOB -- name of capital markets quotes file, e.g. `capital-markets-quotes.csv` 
    - RETURNS_BUCKET -- GCS bucket name with _historical_ returns data
    - RETURNS_BLOB -- name of returns file, e.g. `capital-markets-returns.csv`
"""

import datetime
import json
import logging
import os
import sys

import pandas as pd
import yfinance
from google.cloud import storage

# Set logging
logger = logging.getLogger("capital-markets-data")
logging.basicConfig(
    level=logging.INFO,
    stream=sys.stdout,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    encoding="utf-8"
)

class MarketData:
    """ Parent class for initializing environment variables, GCS methods. """

    def __init__(self):
        self.settings: dict = json.load(open("settings.json", "r"))

    @staticmethod
    def upload_to_gcs(bucket: str, file_name: str, data: pd.DataFrame) -> None:
        """ Upload data to GCS.

        Args:
            bucket (str): bucket name to upload an object to
            file_name (str): file name to be stored on the bucket
            data (pd.DataFrame): dataframe to be uploaded.
        """
        if data.shape[0] > 0:
            logger.info(f"Uploading {file_name} to GCS bucket {bucket}.")
            storage_client = storage.Client()
            bucket = storage_client.bucket(bucket)
            bucket.blob(file_name).upload_from_string(data.to_csv(), 'text/csv')
        else:
            logger.info("Skip uploading an empty dataframe.")

    @staticmethod
    def load_from_gcs(bucket: str, file_name: str) -> pd.DataFrame:
        """ Download data from GCS.

        Args:
            bucket (str): bucket name in GCS to load an object from
            fileName (str): file name to load from GCS

        Returns:
            pd.DataFrame: data loaded from GCS to dataframe.
        """
        logger.info(f"Dowloading {file_name} from GCS bucket {bucket}.")
        data_path = "".join(["gs://", os.path.join(bucket, file_name)])
        try:
            data = pd.read_csv(data_path, index_col=0)
        except FileNotFoundError:
            data = None
        return data


class MarketQuotes(MarketData):
    """ Class for getting capital markets quotes from external source to GCS. """

    def __init__(self):
        super().__init__()
        self.quotes: pd.DataFrame = None
        self.quotesBucket: str = os.environ["QUOTES_BUCKET_NAME"]
        self.quotesFileName: str = os.environ["QUOTES_BLOB_NAME"]

    def fetch(self) -> pd.DataFrame:
        """ Fetch and process quotes from YahooFinance.

        Returns:
            pd.DataFrame: historical quotes for select tickers.
        """
        logger.info(f"Fetching YahooFinance quotes from {self.settings['startDate']}.")
        self.quotes = yfinance.download(
            tickers=self.settings["tickers"],
            start=self.settings["startDate"],
            progress=False
        )
        return self.quotes

    def preprocess(self) -> pd.DataFrame:
        """ Preprocess raw data, sort columns, handle missing values.

        Args:
            data (pd.DataFrame): Raw data from YahooFinance.

        Returns:
            pd.DataFrame: Clean, structured data.
        """
        logger.info("Preprocessing quotes.")
        self.quotes = self.quotes.loc[:, "Adj Close"]
        self.quotes = self.quotes.reindex(sorted(self.quotes.columns), axis=1)
        self.quotes.dropna(how="any", axis=0, inplace=True)
        return self.quotes

    def fit(self) -> pd.DataFrame:
        """ Fetch quotes from YF, preprocess and upload to GCS.

        Returns:
            pd.DataFrame: Clean, structured quotes for select tickers.
        """
        logger.info("Start MarketQuotes pipeline.")
        self.fetch()
        self.preprocess()
        super().upload_to_gcs(
            bucket=self.quotesBucket,
            file_name=self.quotesFileName,
            data=self.quotes
        )
        return self.quotes


class MarketReturns(MarketData):
    """ Class for calculating periodic returns from historical market quotes. """
    def __init__(self, quotes):
        super().__init__()
        self.returns: pd.DataFrame = None
        self.remoteReturns: pd.DataFrame = None
        self.returnsBucket: str = os.environ["RETURNS_BUCKET_NAME"]
        self.returnsFileName: str = os.environ["RETURNS_BLOB_NAME"]

    def get_returns(self, quotes: pd.DataFrame, periods: int = 20) -> pd.DataFrame:
        """ Calculate returns from quotes.

        Args:
            quotes (pd.DataFrame): most recent capital markets quotes 
            periods (int): rolling window of returns. Defaults to 20.
        Returns:
            pd.DataFrame: MA(period) returns from fetched quotes.
        """
        logger.info(f"Calculating MA({periods}) returns from the most recent quotes.")
        self.returns = quotes.pct_change(periods=periods).dropna(how='all')
        return self.returns

    def compare(self) -> pd.DataFrame:
        """ Compare calculated market returns with one from GCS bucket

        Returns:
            Difference of several rows to be uploaded (pd.DataFrame)
        """
        logger.info("Comparing remote returns from GCS to most recent returns.")
        if isinstance(self.remoteReturns, pd.DataFrame):
            remote_date = self.remoteReturns.index[-1]
            logger.info(f"Comparing calculated returns data with one from GCS bucket")
            self.returns = self.returns.loc[remote_date:, :]
            self.returns.drop(self.returns.index[0], axis=0, inplace=True)
        return self.returns

    def fit(self, quotes: pd.DataFrame):
        """ Calculate returns, compare with the remote returns from GCS, update file in GCS.

        Args:
            quotes (pd.DataFrame): most recent capital market quotes.

        Returns:
            Updated batch of returns.
        """
        logger.info("Start MarketReturns pipeline.")
        self.remoteReturns = super().load_from_gcs(self.returnsBucket, self.returnsFileName)
        self.get_returns(quotes)
        self.compare()
        super().upload_to_gcs(
            bucket=self.returnsBucket,
            file_name=self.returnsFileName,
            data=self.returns
        )
        return self.returns


def workflow():
    quotes = MarketQuotes().fit()
    returns = MarketReturns().fit(quotes)


if __name__ == '__main__':
    workflow()
