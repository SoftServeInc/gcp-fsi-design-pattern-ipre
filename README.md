# Google FSI Accelerator Pattern

This pattern consists of few major components:
1) [Terraform code](terraform)
2) [Data processing pipelines, which include ML model training jobs](advanced-analytics/data-pipelines)
3) Web application, which consists of 3 components: [frontend](frontend/ui), [backed](backend/ui-fulfillment), [ml](advanced-analytics/recommendation-engine) 

The Terraform code is used for providing required GCP resources for running the app and initial deploying it. It also creates appropriate foundations, such as Cloud Build triggers and configures Cloud Source Repositories repo, so it's possible to continue developing or modifying the app without significant effort.

Data processing pipelines include Cloud Functions that generate synthetic investor risk preferences data or fetch capital markets data from Yahoo Finance. And Composer/Airflow DAGs are responsible for importing raw data from GCS buckets to BigQuery, training BQ AutoML models, and making inference (exporting batch predict to GCS bucket, which is leveraged by recommendation engine). An appropriate Cloud Function triggers DAG after a new raw file appears in the GCS bucket.

Web application have two major parts. The first one is UI itself. It's a ReactJS app deployed into Cloud Run and interacts with a backend service called ui-fulfillment. ui-fulfillment is a Python (_Django/DRF_) service responsible for working with wallets, manages transactions, shows the user's portfolio with detailed statistics, and acts as a bridge to Recommendation Engine Service. And the last service is a recommendation engine, which is also Python (Flask) app, which is responsible for providing recommendations based on batch predicts, received as an outcome of data pipelines. If you want to modify any microservice - you need to make changes in a code and push/merge them to the main branch. Appropriate Cloud Build job will be triggered, resulting in building a docker image and deploying it into Cloud Run.

To deploy this app, the following prerequisites should be satisfied:
1) Create a new GCP project to host all assets. It is possible to utilize an existent, but we highly recommend creating a new one to avoid any unexpected behaviors.
2) Check that the user has an **Owner** role for the target project.
4) Follow Quick Start Guide from [README.md](terraform/README.md) file in terraform directory.
