# Advanced Analytics
This section contains modules for machine learning, advanced analytics, recommendation engine, deep customer insights.


## Modules
### Data collection/generation
1. Collect quotes data, write to `capital-market-quotes` bucket
2. Calculate returns from `capital-market-quotes`, write unique entries to `capital-market-returns` bucket
3. Generate the Investor Risk Preferences (IRP) dataset, write to `investor-risk-preferences` bucket

### BQ data
1. Write from GCS `capital-market-returns` bucket to BQ `capital-market-returns` table.
2. Write from GCS `investor-risk-preferences` bucket to BQ `investor-risk-preferences` table.

### BQ ML training
1. Train AutoML on `investor-risk-preferences` table
2. Train ML.FORECAST on `capital-market-returns` table

### BQ ML inference
1. Predict risk-aversion with AutoML model on `investor-risk-preferences`
2. Write prediction csv to `predicted-investor-risk-preferences` bucket
3. Predict E[r] with ML.FORECAST on `capital-market-returns` table
4. Write predicted E[r] to `predicted-capital-market-returns` bucket

### IPRE service
1. Load predicted risk-aversion from `predicted-investor-risk-preferences` bucket
2. Load predicted E[r] from `predicted-capital-market-returns` bucket
3. Make, return recommendation. 


## Environment variables
List of env variables required for Cloud Functions and advanced analytics services.

1. `data-pipelines/capital-markets-returns/data`
    - QUOTES_BUCKET_NAME -- GCS bucket name with capital markets quotes data
    - QUOTES_BLOB_NAME -- name of capital markets quotes file, e.g. `capital-markets-quotes.csv` 
    - RETURNS_BUCKET_NAME -- GCS bucket name with _historical_ returns data
    - RETURNS_BLOB_NAME -- name of returns file, e.g. `capital-markets-returns.csv`
    - PROJECT_NAME -- GCP project ID

2. `data-pipelines/investor-risk-preferences/data`
    - BUCKET_NAME -- GCS bucket name with _generated_ investor risk preferences
    - BLOB_NAME -- name of the generated IRP dataset file
    - PROJECT_NAME -- GCP project ID

3. `recommendation-engine`
    - PROJECT_ID -- GCP project ID
    - QUOTES_BUCKET -- GCS bucket name with capital markets quotes data
    - QUOTES_BLOB -- name of capital markets quotes file, e.g. `capital-markets-quotes.csv`
    - PREDICTED_IRP_BUCKET -- GCS bucket name with _predicted_ investor risk preferences
    - PREDICTED_IRP_BLOB -- name of predicted IRP file, e.g. `predicted-irp.csv`
    - PREDICTED_RETURNS_BUCKET -- GCS bucket name with _predicted_ expected returns data
    - PREDICTED_RETURNS_BLOB -- name of predicted expected returns file, e.g. `predicted-expected-returns.csv`
