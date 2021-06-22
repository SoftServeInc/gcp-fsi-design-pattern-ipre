""" The recommendation service module provides functions for loading remote data,
portfolio optimization, investment analytics.

`recommendation_engine.py` requires env variables:
    - QUOTES_BUCKET -- GCS bucket name with capital markets quotes data
    - QUOTES_BLOB -- name of capital markets quotes file, e.g. capital-markets-quotes.csv
    - PREDICTED_IRP_BUCKET -- GCS bucket name with _predicted_ investor risk preferences
    - PREDICTED_IRP_BLOB -- name of predicted IRP file, e.g. predicted-irp.csv
    - PREDICTED_RETURNS_BUCKET -- GCS bucket name with _predicted_ expected returns data
    - PREDICTED_RETURNS_BLOB -- name of predicted expected returns file, e.g. predicted-expected-returns.csv
"""

import json
import logging
import sys
import os
import sys

import numpy as np
import pandas as pd
import pypfopt
from google.cloud import storage

# Set logging
logger = logging.getLogger("recommendation-engine")
logging.basicConfig(
    level=logging.DEBUG,
    stream=sys.stdout,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    encoding="utf-8"
)

__valid_methods__ = [
    "make_recommendation"
]


class PortfolioOptimizer:
    """ Class for computing optimal asset weights in the portfolio.
    
    Public methods:
        fit() -- compute optimal asset weights for given risk aversion.
        get_portfolio_metrics() -- compute investment performance metrics.

    Attributes:
        uuid -- unique user ID for making personalized recommendation
    """
    def __init__(self, uuid):
        self.quotesBucket: str = os.environ["QUOTES_BUCKET"]
        self.quotesBlob: str = os.environ["QUOTES_BLOB"]
        self.quotes: pd.DataFrame = None

        self.riskAversionBucket: str = os.environ["PREDICTED_IRP_BUCKET"]
        self.riskAversionBlob: str = os.environ["PREDICTED_IRP_BLOB"]
        self.riskAversion: float = None

        self.expectedReturnsBucket: str = os.environ["PREDICTED_RETURNS_BUCKET"]
        self.expectedReturnsBlob: str = os.environ["PREDICTED_RETURNS_BLOB"]
        self.expectedReturns: pd.Series = None

        self.tickers = json.load(open("settings.json", "r"))["tickers"]
        self.uuid: str = uuid
        self.periodsPerYear: int = 12
        self.periodicReturns: pd.DataFrame = None
        self.expectedVolatility: pd.Series = None
        self.riskModel: pd.DataFrame = None
        self.optimizer = None
        self.assetWeights: dict = None
        self.portfolioMetrics: dict = None

    def get_quotes(self) -> pd.DataFrame:
        """ Load historical quotes data from Cloud storage csv.

            Returns:
                pd.DataFrame: quotes dataframe.
            """
        logger.debug(
            f"Getting quotes from {self.quotesBucket}/{self.quotesBlob}.")
        dataPath = "".join(["gs://", os.path.join(self.quotesBucket, self.quotesBlob)])
        quotesAll = pd.read_csv(dataPath, index_col=0)
        self.quotes = quotesAll.loc[:, self.tickers]
        return self.quotes

    def get_periodic_returns(self, periods: int = 20) -> pd.DataFrame:
        """ Calculate periodic returns from quotes.

        Args:
            periods (int): Rolling window of periodic returns. Defaults to 20.

        Args:
            periods (int): rolling window of MA. Defaults to 20.

        Returns:
            pd.DataFrame: periodic returns data frame.
        """
        if not isinstance(self.quotes, pd.DataFrame):
            self.get_quotes()
        logger.debug(f"Estimating periodic returns, periods = {periods}.")
        self.periodicReturns = self.quotes.pct_change(periods=periods).dropna(how='all')
        return self.periodicReturns

    def get_expected_returns(self) -> pd.Series:
        """ Get annualized expected returns vector.

        Returns:
            pd.Series: vector of annualized expected returns.
        """
        logger.debug(f"Estimating expected annualized returns, periodsPerYear={self.periodsPerYear}.")
        try:
            logger.debug(f"Getting expected returns vector from {self.expectedReturnsBucket}/{self.expectedReturnsBlob}.")
            dataPath = "".join(["gs://", os.path.join(self.expectedReturnsBucket, self.expectedReturnsBlob)])
            remoteReturns = pd.read_csv(dataPath, index_col=0)
            self.expectedReturns = remoteReturns.loc[self.tickers, 'forecast_value'] * self.periodsPerYear
        except FileNotFoundError:
            logger.warning("Failed to load expected returns from GCS. Estimating returns from quotes.")
            if not isinstance(self.periodicReturns, pd.DataFrame):
                self.get_periodic_returns()
            # annualize expected returns
            nYears = self.periodicReturns.shape[0] / self.periodsPerYear
            self.expectedReturns = np.power(np.prod(1 + self.periodicReturns), (1 / nYears)) - 1
        return self.expectedReturns

    def get_expected_volatility(self) -> pd.Series:
        """ Calculate annualized expected volatility vector.

        Returns:
            pd.Series: vector of annualized expected volatilities.
        """
        if not isinstance(self.periodicReturns, pd.DataFrame):
            self.get_periodic_returns()
        logger.debug("Estimating expected annualized volatilities for tickers.")
        self.expectedVolatility = self.periodicReturns.std() * np.sqrt(self.periodsPerYear)
        return self.expectedVolatility

    def get_risk_model(self) -> pd.DataFrame:
        """ Compute risk model with Ledoit-Wolf shrinkage method.

        Returns:
            pd.DataFrame: Annualized risk model VCM.
        """
        if not isinstance(self.periodicReturns, pd.DataFrame):
            self.get_periodic_returns()
        logger.debug("Estimating risk model.")
        vcm = pypfopt.risk_models.CovarianceShrinkage(
            prices=self.periodicReturns,
            returns_data=True,
            frequency=self.periodsPerYear
        )
        self.riskModel = vcm.ledoit_wolf()
        return self.riskModel

    def get_risk_aversion(self, label: str = "predicted_risk", min_max: tuple[int] = (5, 15)) -> float:
        """ Get risk aversion value for investor UUID.

        Args:
            label (str, optional): Name of predicted risk aversion column. Defaults to "predicted_risk".
            min_max (tuple, optional): Target min, max risk aversion range. Defaults to (5, 15).

        Returns:
            float: Risk aversion value.
        """
        try:
            logger.debug(f"Getting risk aversion from {self.riskAversionBucket}/{self.riskAversionBlob}.")
            dataPath = "".join(["gs://", os.path.join(self.riskAversionBucket, self.riskAversionBlob)])
            riskAversion_df = pd.read_csv(dataPath, sep=';')
            riskAversion_series = riskAversion_df.loc[riskAversion_df.clientID == self.uuid, 'predicted_risk']
            # scale risk aversion
            self.riskAversion = self.scale_value(riskAversion_series.iloc[-1], min_max)
        except FileNotFoundError:
            logger.warning("Failed to load risk aversion from GCS. Setting to default riskAversion=10.0")
            self.riskAversion = 10.0
        return self.riskAversion

    @staticmethod
    def scale_value(value: float, min_max: tuple[int] = (5, 15)):
        _min, _max = min_max
        return float(value * (_max - _min) + _min)

    @staticmethod
    def unscale_value(value: float, min_max: tuple[int] = (5, 15)):
        _min, _max = min_max
        return float((value - _min) / (_max - _min))

    def set_optimizer(self):
        """ Initialize convex optimizer.

        Returns:
            obj: pyfopt.efficient_frontier object.
        """
        if not isinstance(self.expectedReturns, pd.Series):
            self.get_expected_returns()
        if self.riskModel is None:
            self.get_risk_model()
        logger.debug("Setting convex optimizer.")
        self.optimizer = pypfopt.efficient_frontier.EfficientFrontier(
            expected_returns=self.expectedReturns,
            cov_matrix=self.riskModel,
            weight_bounds=(0, 1)
        )
        return self.optimizer

    @staticmethod
    def structure_results(weights: dict, returns: pd.Series, volatility: pd.Series) -> dict:
        """ Helper function for structuring results in dictionary.

        Args:
            weights (dict): dictionary with optimal asset weights in portfolio.
            returns (pd.Series): annualized expected returns vector.
            volatility (pd.Series): annualized expected volatility vector.

        Returns:
            dict: dictionary with ticker attributes.
        """
        for key, value in weights.items():
            weights[key] = {
                "weight": value,
                "expectedReturn": returns.loc[key],
                "expectedVolatility": volatility.loc[key]
            }
        return weights

    def fit(self, riskAversion: float) -> dict:
        """ Compute optimal asset weights in the portfolio.

        Args:
            riskAversion (float, optional): Risk aversion factor. Defaults to None.

        Returns:
            dict: dictionary of asset weights in the portfolio.
        """
        if self.optimizer is None:
            self.set_optimizer()
        logger.debug(f"Computing optimal weights for riskAversion = {riskAversion}.")
        self.assetWeights = self.optimizer.max_quadratic_utility(
            risk_aversion=riskAversion ** 2,
            market_neutral=False
        )
        self.assetWeights = self.structure_results(
            weights=dict(self.assetWeights),
            returns=self.expectedReturns,
            volatility=self.get_expected_volatility()
        )
        return self.assetWeights

    def get_portfolio_metrics(self, rf: float = 0.025) -> dict:
        """ Compute portfolio metrics given risk-free rate.

        Args:
            rf (float, optional): Risk-free rate. Defaults to 0.025.

        Returns:
            dict: E[r], E[std], Sharpe-Ratio.
        """
        logger.debug(f"Computing portfolio performance metrics for rf={rf}.")
        portfolio_metrics = self.optimizer.portfolio_performance(rf)
        self.portfolioMetrics = {
            "expectedReturn": portfolio_metrics[0] * 100,
            "annualVolatility": portfolio_metrics[1] * 100,
            "sharpeRatio": portfolio_metrics[2]
        }
        return self.portfolioMetrics


def make_recommendation(uuid: str, riskAversion: float = None):
    """ Workflow for making personalized recommendation, computing investment analytics.

    Args:
        uuid (str): unique user ID.
        riskAversion (float, optional): Select risk aversion factor in range [0, 1]. Defaults to None.

    Returns:
        dict: personalized recommendation on investment products, investment performance metrics.
    """
    mypy = PortfolioOptimizer(uuid)
    if not isinstance(riskAversion, float):
        riskAversion = mypy.get_risk_aversion(uuid)
    else:
        riskAversion = mypy.scale_value(riskAversion)
    weights = mypy.fit(riskAversion)
    metrics = mypy.get_portfolio_metrics(rf=0.025)
    recommendation = {
        "portfolioComposition": weights,
        "portfolioMetrics": metrics,
        "riskAversion": mypy.unscale_value(riskAversion),
    }
    return recommendation
