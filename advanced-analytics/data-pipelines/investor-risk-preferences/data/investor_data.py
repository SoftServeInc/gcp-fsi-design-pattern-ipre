import random

import numpy as np
import pandas as pd
import scipy.stats as stat
from sklearn.ensemble import RandomForestRegressor
from sklearn.linear_model import LinearRegression
from sklearn.metrics import r2_score
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import MinMaxScaler

random.seed(2021)
np.random.seed(2021)
stat.rv_continuous.random_state = 2021

# consider moving params to a separate file

params = {
    "investor": {
        "count": 1000,  # number of unique investors
        "attributes": {
            "risk",  # label
            "clientID",
            "dateID",
            "avgMonthlyIncome",
            "education",
            "expSavings",
            "expTransport",
            "expGroceries",
            "expLeisure",
            "expShopping",
            "expUtilities",
            "expOther",
            "cardLevel",
            "amountDeposit",
            "amountLoan",
            "avgTransaction",
            "avgNumTransactions",
            "largestSingleTransaction"
        }
    },
    "observation": {
        "frequency": "M",  # monthly
        "startDate": "2017-01-01",
        "endDate": "2021-01-01"
    }
}


class InvestorData:
    def __init__(self):
        self._investor_data = self.get_empty_df()
        self._count = self._investor_data.shape[0]

    def make_date_range(self, startDate: str = "2017-01-01",
                        endDate: str = "2021-01-01",
                        freq: str = "M") -> set[str]:
        """ Create list of "year-month" pairs.

        Args:
            startDate (str, optional): [description]. Defaults to "2017-01-01".
            endDate (str, optional): [description]. Defaults to "2021-01-01".
            freq (str, optional): [description]. Defaults to "M".

        Returns:
            set[str]: [description]
        """
        dateStamps = pd.date_range(start=startDate, end=endDate,
                                   freq=freq, normalize=True).to_list()
        datePairs = {"-".join([str(dt.year), str(dt.month)])
                     for dt in dateStamps}
        return datePairs

    def get_empty_df(self) -> pd.DataFrame:
        """ Creates empty placeholder dataset of investor risk preference features.

        Returns:
            pd.DataFrame: [description]
        """

        dateRange = self.make_date_range(
            startDate=params["observation"]["startDate"],
            endDate=params["observation"]["endDate"],
            freq=params["observation"]["frequency"]
        )

        dimX = params["investor"]["count"] * len(dateRange)
        dimY = len(params["investor"]["attributes"])
        dim = (dimX, dimY)

        investorData = pd.DataFrame(
            data=np.full(dim, np.nan),
            index=None,
            columns=params["investor"]["attributes"])
        return investorData

    def gen_target(self) -> None:
        """ Generate random risk preferences (target) from Generalized
         Gamma distribution.
        """
        a, c = 0.5, 10  # generalized gamme parameters
        random_vars = stat.gengamma.rvs(a, c, size=self._count)
        random_vars = np.array(random_vars).reshape(-1, 1)

        scaler = MinMaxScaler(feature_range=(0, 1))
        random_vars = scaler.fit_transform(random_vars).ravel()
        self._investor_data['risk'] = random_vars

    def gen_avg_monthly_income(self, x: list[float],
                            feature_range: tuple = (1000, 1_000_000)) -> None:
        """ Generates avgMonthlyIncome feature meaning earning over
        past 6 months.  Random samples are drawn from non-central chi-squared
        distribution conditioned on risk label only.

        Args:
            x (list[float]): input to gengamme distribution sampler, in our
                                case it's risk preference target.
            feature_range (tuple, optional): Defaults to (1000, 1_000_000).
        """
        np.random.seed(2021)
        df, nc = 5, 1.06
        rv = stat.ncx2(df, nc)
        # add noise to random sampling
        noise = stat.skewnorm(0, 1).rvs(len(x))
        noise = np.where(noise > 1.5, noise, -1.5 * noise)
        random_vars = 10 * rv.pdf(x) - noise
        random_vars = np.max(random_vars) - random_vars
        scaler = MinMaxScaler(feature_range=feature_range)
        random_vars = np.array(random_vars).reshape(-1, 1)
        random_vars = scaler.fit_transform(random_vars).ravel()
        self._investor_data['avgMonthlyIncome'] = np.round(random_vars, 1)

    def gen_avg_transaction(self, x: list[float],
                            feature_range: tuple = (0, 100_000)) -> None:
        """ Generates avgTransaction feature meaning average transaction over
        past 6 months. Random samples are drawn from exponential distribution
        with gaussian noise and random  conditioned on risk label only.

        Args:
            x (list[float]): input to distribution sampler.
            feature_range (tuple, optional): Defaults to (1000, 1_000_000).
        """
        np.random.seed(2021)
        rv = stat.expon(-0.1)
        # add noise to random sampling
        noise = stat.norm(0, 1).rvs(len(x))
        noise = np.where(noise > 1.5, noise, -1.5 * noise)
        random_vars = 3 - rv.pdf(x) + noise
        idx_reduce = np.random.choice(range(len(random_vars)),
                                      size=int(0.75*len(x)))
        random_vars[idx_reduce] /= 10.
        # scale
        scaler = MinMaxScaler(feature_range=feature_range)
        random_vars = np.array(random_vars).reshape(-1, 1)
        random_vars = scaler.fit_transform(random_vars).ravel()
        self._investor_data['avgTransaction'] = np.round(random_vars, 1)

    def gen_largest_single_transaction(self, x: list[float],
                            feature_range: tuple = (0, 1_000_000)) -> None:
        """ Generates largestSingleTransaction feature, random samples are
        drawn from Exponential distribution conditioned on risk label only.

        Args:
            x (list[float]): input to distribution sampler, in our
                                case it's risk preference target.
            feature_range (tuple, optional): Defaults to (1000, 1_000_000).
        """
        np.random.seed(2021)
        # add noise to random sampling
        random_vars = stat.expon.pdf(x, -0.1)
        idx_reduce = np.random.choice(range(len(random_vars)),
                                      size=int(0.2*len(x)), replace=False)
        random_vars[idx_reduce] /= 10.
        random_vars -= np.mean(random_vars)
        idx_random = np.random.choice(range(len(random_vars)),
                                      size=int(0.2*len(x)), replace=False)
        random_vars[idx_random] = stat.norm(0, 1.5).rvs(len(idx_random))
        random_vars = np.where(random_vars < 0, -1 * random_vars, 0.5 * random_vars)
        # scale
        scaler = MinMaxScaler(feature_range=feature_range)
        random_vars = np.array(random_vars).reshape(-1, 1)
        random_vars = scaler.fit_transform(random_vars).ravel()
        self._investor_data['largestSingleTransaction'] = np.round(random_vars, 1)

    def gen_avg_num_transactions(self, x: list[float],
                                 feature_range: tuple = (0, 1_000)) -> None:
        """ Generates average number of transactions over
        past 6 months.  Random samples are drawn from Gumbel distribution
        distribution conditioned on risk label only.

        Args:
            x (list[float]): input todistribution sampler, in our
                                case it's risk preference target.
            feature_range (tuple, optional): Defaults to (0, 1_000).
        """
        np.random.seed(2021)
        random.seed(2021)
        rv = stat.gumbel_r()
        # add noise to random sampling
        noise = stat.norm(0, 0.5).rvs(len(x))
        random_vars = 3.5 * rv.pdf(x) - 0.4 * noise
        random_vars = np.where(random_vars < 1, 1.0 * random_vars, 0.5 * random_vars)
        random_vars = np.clip(random_vars, 0.5, 1)
        random.shuffle(random_vars[:len(x) // 3])
        # scale
        scaler = MinMaxScaler(feature_range=feature_range)
        random_vars = np.array(random_vars).reshape(-1, 1)
        random_vars = scaler.fit_transform(random_vars).ravel()
        self._investor_data['avgNumTransactions'] = np.round(random_vars, 1)

    def gen_amount_deposit(self, x: list[float],
                           feature_range: tuple = (0, 1_000_000)) -> None:
        """ Generates amount deposit currently holding by customer.
        Random samples are drawn from Gaussian distribution.

        Args:
            x (list[float]): input to distribution sampler, in our
                                case it's risk preference target.
            feature_range (tuple, optional): Defaults to (1000, 1_000).
        """
        np.random.seed(2021)
        random.seed(2021)
        rv = stat.norm(0, 1)
        random_vars = abs(rv.rvs(len(x)))
        random_vars = np.clip(random_vars, 0.8, 5)  # clip for larger imbalance
        # scale
        scaler = MinMaxScaler(feature_range=feature_range)
        random_vars = np.array(random_vars).reshape(-1, 1)
        random_vars = scaler.fit_transform(random_vars).ravel()
        # convert to bins as people usually put rounded thousands to deposit
        bins = np.linspace(feature_range[0], feature_range[1], 21)
        ind = np.digitize(random_vars, bins)
        random_vars = [bins[i-1] for i in ind]
        self._investor_data['amountDeposit'] = np.round(random_vars, 1)

    def gen_amount_loan(self, x: list[float],
                        feature_range: tuple = (0, 1_000_000)) -> None:
        """ Generates amount loan feature customer own.
        Random samples are drawn from an F continuous random variable
        distribution.

        Args:
            x (list[float]): input to distribution sampler, in our
                                case it's risk preference target.
            feature_range (tuple, optional): Defaults to (1000, 1_000).
        """
        np.random.seed(2021)
        random.seed(2021)
        dfn, dfd = 5, 18
        rv = stat.f(dfn, dfd)
        random_vars = 1 - rv.pdf(x)
        # scale
        scaler = MinMaxScaler(feature_range=feature_range)
        random_vars = np.array(random_vars).reshape(-1, 1)
        random_vars = scaler.fit_transform(random_vars).ravel()
        t = random_vars[:len(random_vars)//3]
        random.shuffle(t)
        random_vars[:len(random_vars)//3] = t
        # convert to bins
        bins = np.linspace(feature_range[0], feature_range[1], 21)
        ind = np.digitize(random_vars, bins)
        random_vars = [bins[i-1] for i in ind]
        self._investor_data['amountLoan'] = np.round(random_vars, 1)

    def gen_card_level(self, x: list[float]) -> None:
        """ Generates 4 card levels by drawing samples from
        R-distributed (symmetric beta) distribution and quantile
        binning.

        Args:
            x (list[float]): input to distribution sampler, in our
                                case it's risk preference target.
        """
        np.random.seed(2021)
        random.seed(2021)
        c = 1.4
        rv = stat.rdist(c)
        random_vars = [t - np.random.random() if
                       np.random.random() > 0.5 else t for t in x]
        random_vars = rv.pdf(random_vars)
        cardLevel = []
        card_quantiles = np.quantile(random_vars, [0.25, 0.5, 0.9])
        for c in random_vars:
            if c <= card_quantiles[0]:
                cardLevel.append(0)
            elif c > card_quantiles[0] and c < card_quantiles[1]:
                cardLevel.append(1)
            elif c >= card_quantiles[1] and c < card_quantiles[2]:
                cardLevel.append(2)
            elif c >= card_quantiles[2]:
                cardLevel.append(3)
        self._investor_data['cardLevel'] = cardLevel

    def gen_education(self, x: list[float]) -> None:
        """ Generates education using rayleigh distribution and quantile
        binning.

        Args:
            x (list[float]): input to distribution sampler, in our
                                case it's risk preference target.
        """
        np.random.seed(2021)
        random.seed(2021)
        rv = stat.rayleigh()
        random_vars = [t + np.random.random() if
                       np.random.random() > 0.9 else t for t in x]
        random_vars = rv.pdf(random_vars)
        edu = []
        edu_quantiles = np.quantile(random_vars, [0.2, 0.5, 0.7, 0.9])
        for c in random_vars:
            if c <= edu_quantiles[0]:
                edu.append('college')
            elif c > edu_quantiles[0] and c < edu_quantiles[1]:
                edu.append('NA')
            elif c >= edu_quantiles[1] and c < edu_quantiles[2]:
                edu.append('BSc')
            elif c >= edu_quantiles[2] and c < edu_quantiles[3]:
                edu.append('MSc')
            else:
                edu.append('PhD')
        self._investor_data['education'] = edu

    def gen_n_exp_spendings(self,
                            n_spendings: int = 7) -> None:
        """Generates copmletely random joint distribution of category
        spendings per client. Uses convention of @_investor_data columns that
        starts with 'exp*'.

        Args:
            n_spendings (int, optional): Number of spendings categories.
                                         Defaults to 7.
        """
        def _gen_random_joint(n_samples):
            df, nc = 21, 1.06
            rv = stat.ncx2(df, nc)
            allrandom = []
            for i in range(n_samples):
                random_vars = [rv.rvs() for _ in range(n_spendings)]
                random_vars = random_vars / sum(random_vars)
                allrandom.append(random_vars)
            allrandom = np.array(allrandom).reshape(n_samples, n_spendings)
            return np.round(allrandom, 2)

        n_samples = int(self._investor_data.shape[0] * 0.05)
        random_spendings = _gen_random_joint(n_samples)
        random_spendings = np.tile(random_spendings, [20, 1])
        j = 0
        for exp_col in self._investor_data.columns:
            if exp_col.startswith('exp'):
                self._investor_data[exp_col] = random_spendings[:, j]
                j += 1

    def gen_client_id(self, len_id: int = 16) -> None:
        """ Generates clients id with given length according to params.

        Args:
            len_id (int): number of characters in the ID.
        """
        clientIDset = [f"user-{tail:0{len_id}d}" for tail in range(params['investor']['count'])]
        assert len(set(clientIDset)) == params['investor']['count']
        clientID = clientIDset * (self._investor_data.shape[0] // params['investor']['count'])
        self._investor_data['clientID'] = clientID

    def gen_date_id(self) -> None:
        """ Generates date ID according to params.
        """
        dateID = list(self.make_date_range(
                        startDate=params["observation"]["startDate"],
                        endDate=params["observation"]["endDate"],
                        freq=params["observation"]["frequency"]
                    ))
        n_points = self._investor_data.shape[0] // len(dateID)
        dateID = [[one_ts] * n_points for one_ts in dateID]
        dateID = np.array(dateID).ravel()
        dateID = pd.to_datetime(dateID)
        self._investor_data['dateID'] = dateID

    def check_dataset(self) -> None:
        """ Tests for dataset consistency.
        """
        # check no NaNs in dataset
        assert not np.any(self._investor_data.isna())
        # check number of unique clients match to the param value at given date
        unq_clients = self._investor_data[self._investor_data['dateID'] ==
                         params["observation"]["startDate"]].clientID.nunique()
        assert unq_clients == params["investor"]["count"]
        # check dataset cannot be easily fit by Linear Regression
        assert not self.is_dataset_trivial()
        print("\nSynthetic dataset generation has completed successfully!")

    def is_dataset_trivial(self, threshold: float = 0.8) -> bool:
        """ Fits linear regression and random forest regressors,
        evaluates R^2 score to define whether the dataset is complex enough.

        Args:
            threshold: r^2 evaluation metric threshold
        Returns:
            bool: True if dataset is trivial and r^2 score is > @threshold,
                    else False
        """
        print('Checking dataset for triviality, start training of regressors')
        X_train, X_test, y_train, y_test = train_test_split(
                self._investor_data.drop(['education', 'dateID', 'clientID', 'risk'],
                axis=1),
                self._investor_data['risk'], test_size=0.2, random_state=2021)
        clf = RandomForestRegressor(verbose=True, random_state=2021)
        clf.fit(X_train, y_train)

        lr = LinearRegression()
        lr.fit(X_train, y_train)

        preds = lr.predict(X_test)
        r2_1 = r2_score(y_test, preds)

        preds = clf.predict(X_test)
        r2_2 = r2_score(y_test, preds)
        print(f'LinearRegression R^2 score: {r2_1}\n'
              f'RandomForestRegressor R^2 score: {r2_2}')
        if r2_1 > threshold or r2_2 > threshold:
            return True
        return False

    def gen_all_features(self) -> None:
        """ Generates all features from random distribution based on
        risk label. Checks dataset for consistency and triviality.
        """
        self.gen_target()
        self.gen_avg_monthly_income(self._investor_data['risk'].values)
        self.gen_avg_transaction(self._investor_data['risk'].values)
        self.gen_avg_num_transactions(self._investor_data['risk'].values)
        self.gen_largest_single_transaction(self._investor_data['risk'].values)
        self.gen_amount_deposit(self._investor_data['risk'].values)
        self.gen_amount_loan(self._investor_data['risk'].values)
        self.gen_date_id()
        self.gen_client_id()
        self.gen_card_level(self._investor_data['risk'].values)
        self.gen_education(self._investor_data['risk'].values)
        self.gen_n_exp_spendings()
        self.check_dataset()
        self._investor_data['risk'] = np.round(self._investor_data['risk'], 3)

    def save_dataset(self, filepath: str) -> None:
        self._investor_data = self._investor_data.loc[:,   ["risk",
                                                            "clientID",
                                                            "dateID",
                                                            "avgMonthlyIncome",
                                                            "education",
                                                            "expSavings",
                                                            "expTransport",
                                                            "expGroceries",
                                                            "expLeisure",
                                                            "expShopping",
                                                            "expUtilities",
                                                            "expOther",
                                                            "cardLevel",
                                                            "amountDeposit",
                                                            "amountLoan",
                                                            "avgTransaction",
                                                            "avgNumTransactions",
                                                            "largestSingleTransaction"]]
        self._investor_data.to_csv(filepath, index=False)


if __name__ == "__main__":
    investors = InvestorData()
    investors.gen_all_features()
    investors.save_dataset('investor_data.csv')
