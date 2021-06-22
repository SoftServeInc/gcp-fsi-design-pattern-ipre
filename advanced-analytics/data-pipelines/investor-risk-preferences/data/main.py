from investor_data import InvestorData
from google.cloud import storage
import os


def investor_risk_preferences(request, context) -> str:
    """ Generates investor risk preference data and stores to GCS.
    """
    try:
        BUCKET_NAME = os.environ["BUCKET_NAME"]
        BLOB_NAME = os.environ["BLOB_NAME"]
        investors = InvestorData()
        investors.gen_all_features()
        storage_client = storage.Client()
        bucket = storage_client.bucket(BUCKET_NAME)
        bucket.blob(BLOB_NAME).upload_from_string(
            investors._investor_data[["risk",
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
                                    "largestSingleTransaction"]].to_csv(index=False, header=None),
            'text/csv')
        print(f'Data has been written to {BUCKET_NAME}/{BLOB_NAME}.')
        return 'OK'
    except Exception as e:
        print(e)
        return 'Error'
