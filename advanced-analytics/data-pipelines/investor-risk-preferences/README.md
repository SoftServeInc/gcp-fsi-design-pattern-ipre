# Investor Risk Preferences
This section provides Cloud Function script for generating a dataset with investor risk preferences. And Cloud Composer/Apache Airflow DAG with the following steps:
* Import raw data from Google Cloud Storage bucket to BigQuery
* BigQuery AutoML model training
* predicting risk-aversion factor
