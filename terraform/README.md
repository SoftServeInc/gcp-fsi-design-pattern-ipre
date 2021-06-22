## Disclaimer
*This configuration is compatible to be run in [GCP Free Trial](https://cloud.google.com/free). Still, please pay attention that the estimated bill for running this pattern during a month will be close to $400 (actual consumption varies on resource usage). And Free Trial provides **$300 in free credits**. After spending **$300 in free credits** provided with each fresh new Trial Accounts, you can be charged for any resource consumption.*

## Overview
This folder contains the Terraform code for infrastructure and application provisioning of the Investment Products Recommendation Engine (IPRE). It leverages [Terraform modules for Google Cloud](https://github.com/terraform-google-modules) and assumes that Terraform v0.13 is used. On the date of publishing, not all Terraform modules has release versions that support Terraform 0.13, so they use feature branches of those modules that already provide support for v0.13. Details can be found at the [Modules](#modules) section of this page.

Infrastructure provisioning consist of the following major steps:
1. Creating git repo in Cloud Source Repositories and pushing code there.
2. Creating all necessary cloud resources (including Storage Buckets, Composer Environment, Cloud Functions, BigQuery Datasets, etc.)
3. Triggering data generation functions, which fetch/generate raw data. And the occurrence of raw data in storage buckets, in turn, triggers data processing pipelines.
4. Building and deploying a web application consisting of 3 microservices (ui, ui-fulfillment, and recommendation-engine). It's accomplished via Cloud Build jobs.

## Quick Start Guide
To bootstrap full-featured infrastructure, the following steps need to be compleated:
1. Create a new GCP project to host all assets. It is possible to utilize existent one, but we highly recommend creating a new to avoid any unexpected behaviors.
2. Check that the user has an __Owner__ role for the target project. In order to avoid any unexpected behaviors, we *recommend* bootstrapping this pattern from the **GCP Cloud Shell**.
3. Enable required GCP APIs:
```bash
user@cloudshell:~$ gcloud services enable sourcerepo.googleapis.com \
appengine.googleapis.com run.googleapis.com cloudfunctions.googleapis.com composer.googleapis.com \
cloudscheduler.googleapis.com servicenetworking.googleapis.com cloudbuild.googleapis.com \
compute.googleapis.com bigquery.googleapis.com sql-component.googleapis.com \
dataflow.googleapis.com automl.googleapis.com logging.googleapis.com --project <my-gcp-project-id>
```
4. Make sure that *gcloud-sdk*, *python3* with *pip*, and *terraform 0.13* installed. In case you are using Cloud Shell, you need to install terraform 0.13:
```bash
user@cloudshell:~$ curl \
https://releases.hashicorp.com/terraform/0.13.7/terraform_0.13.7_linux_amd64.zip \
-o terraform.zip && unzip terraform.zip && mkdir -p ~/bin && mv terraform ~/bin/ && \
export PATH=~/bin:$PATH && terraform version
```
The output should be similar to the following. Please make sure, that output confirms that you are using terraform version 0.13.7.
```bash
  % Total    % Received % Xferd  Average Speed   Time    Time     Time  Current
                                 Dload  Upload   Total   Spent    Left  Speed
100 33.2M  100 33.2M    0     0   111M      0 --:--:-- --:--:-- --:--:--  112M
Archive:  terraform.zip
  inflating: terraform
Terraform v0.13.7

Your version of Terraform is out of date! The latest version
is 0.15.4. You can update by downloading from https://www.terraform.io/downloads.html

```
5. Clone this repo and change work directory to the terraform code root directory (eg. *~/google-fsi-accelerator-pattern/terraform*).
6. Copy **terraform.tfvars.sample** to **terraform.tfvars** and adjust the following setting:
  - **project_id** - id of the GCP project, where the pattern will be deployed. 
  - **platform** - if you are using Cloud Shell - just left it as linux. If you are running from your own workstation - selection will depend on your platform (linux/darwin).  
  You can explore all available options in the [`Inputs`](#inputs) section at the bottom of this page.
7. Initialize terraform in the repo's terraform root directory:
```bash
user@cloudshell:~/google-fsi-accelerator-pattern/terraform$ terraform init
```
8. Deploy infrastructure with:
```bash
user@cloudshell:~/google-fsi-accelerator-pattern/terraform$ terraform apply
```
Applying Terraform changes may take up to 60 minutes, but it finishes within 30 minutes in most cases. After applying, Terraform output will provide the URL of the frontend application, so you can validate how it works. But, please notice that processing data pipelines will take more time than infrastructure provision. So, before validating, please make sure that Composer/Airflow DAGs successfully completed.

## GCP APIs
- compute.googleapis.com
- servicenetworking.googleapis.com
- run.googleapis.com
- appengine.googleapis.com
- cloudscheduler.googleapis.com
- cloudfunctions.googleapis.com
- composer.googleapis.com
- dataflow.googleapis.com
- bigquery.googleapis.com
- automl.googleapis.com
- cloudbuild.googleapis.com
- sql-component.googleapis.com
- sourcerepo.googleapis.com

<!-- BEGIN_TF_DOCS -->
## Requirements

| Name | Version |
|------|---------|
| <a name="requirement_terraform"></a> [terraform](#requirement\_terraform) | ~> 0.13.0 |
| <a name="requirement_external"></a> [external](#requirement\_external) | ~> 2.1.0 |
| <a name="requirement_google"></a> [google](#requirement\_google) | ~> 3.58.0 |
| <a name="requirement_google-beta"></a> [google-beta](#requirement\_google-beta) | ~> 3.58.0 |
| <a name="requirement_local"></a> [local](#requirement\_local) | ~> 2.1.0 |
| <a name="requirement_null"></a> [null](#requirement\_null) | ~> 2.1.0 |
| <a name="requirement_random"></a> [random](#requirement\_random) | ~> 2.2.0 |
| <a name="requirement_time"></a> [time](#requirement\_time) | ~> 0.7.1 |

## Providers

| Name | Version |
|------|---------|
| <a name="provider_external"></a> [external](#provider\_external) | ~> 2.1.0 |
| <a name="provider_google"></a> [google](#provider\_google) | ~> 3.58.0 |
| <a name="provider_google-beta"></a> [google-beta](#provider\_google-beta) | ~> 3.58.0 |
| <a name="provider_local"></a> [local](#provider\_local) | ~> 2.1.0 |
| <a name="provider_null"></a> [null](#provider\_null) | ~> 2.1.0 |
| <a name="provider_random"></a> [random](#provider\_random) | ~> 2.2.0 |
| <a name="provider_time"></a> [time](#provider\_time) | ~> 0.7.1 |

## Modules

| Name | Source | Version |
|------|--------|---------|
| <a name="module_bigquery"></a> [bigquery](#module\_bigquery) | terraform-google-modules/bigquery/google | ~> 5.0.0 |
| <a name="module_cb_sa_roles"></a> [cb\_sa\_roles](#module\_cb\_sa\_roles) | terraform-google-modules/iam/google//modules/member_iam | ~> 7.1.0 |
| <a name="module_cloud_storage"></a> [cloud\_storage](#module\_cloud\_storage) | terraform-google-modules/cloud-storage/google | ~> 2.0.0 |
| <a name="module_cloudsql_db"></a> [cloudsql\_db](#module\_cloudsql\_db) | GoogleCloudPlatform/sql-db/google//modules/safer_mysql | ~> 5.0.0 |
| <a name="module_composer"></a> [composer](#module\_composer) | terraform-google-modules/composer/google//modules/create_environment | ~> 1.0.0 |
| <a name="module_composer_sa"></a> [composer\_sa](#module\_composer\_sa) | terraform-google-modules/service-accounts/google | ~> 4.0.0 |
| <a name="module_default_sa_roles"></a> [default\_sa\_roles](#module\_default\_sa\_roles) | terraform-google-modules/iam/google//modules/member_iam | ~> 7.1.0 |
| <a name="module_deploy_backend_apps"></a> [deploy\_backend\_apps](#module\_deploy\_backend\_apps) | terraform-google-modules/gcloud/google | ~> 3.0.0 |
| <a name="module_deploy_frontend_apps"></a> [deploy\_frontend\_apps](#module\_deploy\_frontend\_apps) | terraform-google-modules/gcloud/google | ~> 3.0.0 |
| <a name="module_deploy_ml_apps"></a> [deploy\_ml\_apps](#module\_deploy\_ml\_apps) | terraform-google-modules/gcloud/google | ~> 3.0.0 |
| <a name="module_fuction_service_account"></a> [fuction\_service\_account](#module\_fuction\_service\_account) | terraform-google-modules/service-accounts/google | ~> 4.0.0 |
| <a name="module_gen_data_function"></a> [gen\_data\_function](#module\_gen\_data\_function) | github.com/terraform-google-modules/terraform-google-scheduled-function | v2.0.0 |
| <a name="module_network_private"></a> [network\_private](#module\_network\_private) | terraform-google-modules/network/google | ~> 3.2.2 |
| <a name="module_private_service_access"></a> [private\_service\_access](#module\_private\_service\_access) | GoogleCloudPlatform/sql-db/google//modules/private_service_access | ~> 5.0.0 |
| <a name="module_trigger_cf"></a> [trigger\_cf](#module\_trigger\_cf) | terraform-google-modules/gcloud/google | ~> 3.0.0 |
| <a name="module_trigger_dag_function"></a> [trigger\_dag\_function](#module\_trigger\_dag\_function) | github.com/terraform-google-modules/terraform-google-event-function | bot-add-module-attribution |

## Resources

| Name | Type |
|------|------|
| [google-beta_google_project_service_identity.cb_sa](https://registry.terraform.io/providers/hashicorp/google-beta/latest/docs/resources/google_project_service_identity) | resource |
| [google_app_engine_application.app](https://registry.terraform.io/providers/hashicorp/google/latest/docs/resources/app_engine_application) | resource |
| [google_cloudbuild_trigger.backend_main_branch](https://registry.terraform.io/providers/hashicorp/google/latest/docs/resources/cloudbuild_trigger) | resource |
| [google_cloudbuild_trigger.frontend_main_branch](https://registry.terraform.io/providers/hashicorp/google/latest/docs/resources/cloudbuild_trigger) | resource |
| [google_cloudbuild_trigger.ml_main_branch](https://registry.terraform.io/providers/hashicorp/google/latest/docs/resources/cloudbuild_trigger) | resource |
| [google_sourcerepo_repository.repo](https://registry.terraform.io/providers/hashicorp/google/latest/docs/resources/sourcerepo_repository) | resource |
| [google_storage_bucket_object.dag](https://registry.terraform.io/providers/hashicorp/google/latest/docs/resources/storage_bucket_object) | resource |
| [google_storage_bucket_object.schema](https://registry.terraform.io/providers/hashicorp/google/latest/docs/resources/storage_bucket_object) | resource |
| [google_storage_bucket_object.udf](https://registry.terraform.io/providers/hashicorp/google/latest/docs/resources/storage_bucket_object) | resource |
| [local_file.cf_trigger_dag](https://registry.terraform.io/providers/hashicorp/local/latest/docs/resources/file) | resource |
| [local_file.cf_trigger_req](https://registry.terraform.io/providers/hashicorp/local/latest/docs/resources/file) | resource |
| [null_resource.push_cs_repo](https://registry.terraform.io/providers/hashicorp/null/latest/docs/resources/resource) | resource |
| [null_resource.python_requirements](https://registry.terraform.io/providers/hashicorp/null/latest/docs/resources/resource) | resource |
| [random_shuffle.az](https://registry.terraform.io/providers/hashicorp/random/latest/docs/resources/shuffle) | resource |
| [random_string.django_admin](https://registry.terraform.io/providers/hashicorp/random/latest/docs/resources/string) | resource |
| [random_string.django_admin_password](https://registry.terraform.io/providers/hashicorp/random/latest/docs/resources/string) | resource |
| [random_string.django_sec](https://registry.terraform.io/providers/hashicorp/random/latest/docs/resources/string) | resource |
| [random_string.rand](https://registry.terraform.io/providers/hashicorp/random/latest/docs/resources/string) | resource |
| [time_sleep.gen_data_function](https://registry.terraform.io/providers/hashicorp/time/latest/docs/resources/sleep) | resource |
| [time_sleep.trigger_dag_function](https://registry.terraform.io/providers/hashicorp/time/latest/docs/resources/sleep) | resource |
| [external_external.composer_client_id](https://registry.terraform.io/providers/hashicorp/external/latest/docs/data-sources/external) | data source |
| [google_cloud_run_service.be](https://registry.terraform.io/providers/hashicorp/google/latest/docs/data-sources/cloud_run_service) | data source |
| [google_cloud_run_service.fe](https://registry.terraform.io/providers/hashicorp/google/latest/docs/data-sources/cloud_run_service) | data source |
| [google_cloud_run_service.ml](https://registry.terraform.io/providers/hashicorp/google/latest/docs/data-sources/cloud_run_service) | data source |
| [google_compute_default_service_account.default](https://registry.terraform.io/providers/hashicorp/google/latest/docs/data-sources/compute_default_service_account) | data source |
| [google_compute_zones.available](https://registry.terraform.io/providers/hashicorp/google/latest/docs/data-sources/compute_zones) | data source |

## Inputs

| Name | Description | Type | Default | Required |
|------|-------------|------|---------|:--------:|
| <a name="input_bq_location"></a> [bq\_location](#input\_bq\_location) | The regional location for the dataset only US and EU are suitable for AutoML. | `string` | `"EU"` | no |
| <a name="input_composer_machine_type"></a> [composer\_machine\_type](#input\_composer\_machine\_type) | Machine type of Cloud Composer nodes. | `string` | `"e2-medium"` | no |
| <a name="input_composer_subnet"></a> [composer\_subnet](#input\_composer\_subnet) | Subnetwork where Cloud Composer is created. | `string` | `"10.2.0.0/16"` | no |
| <a name="input_db_assign_public_ip"></a> [db\_assign\_public\_ip](#input\_db\_assign\_public\_ip) | Set to true if the master instance should also have a public IP (less secure). | `string` | `true` | no |
| <a name="input_db_availability_type"></a> [db\_availability\_type](#input\_db\_availability\_type) | The availability type for the master instance. Can be either `REGIONAL` or `null`. | `string` | `null` | no |
| <a name="input_db_tier"></a> [db\_tier](#input\_db\_tier) | The tier for the master instance. | `string` | `"db-f1-micro"` | no |
| <a name="input_env"></a> [env](#input\_env) | Application environment. | `string` | `"test"` | no |
| <a name="input_location"></a> [location](#input\_location) | Bucket location. | `string` | `"europe-west3"` | no |
| <a name="input_platform"></a> [platform](#input\_platform) | Platform CLI will run on. Defaults to linux. Valid values: linux, darwin. | `string` | `"linux"` | no |
| <a name="input_project_id"></a> [project\_id](#input\_project\_id) | The ID of the project in which to provision resources. | `string` | n/a | yes |
| <a name="input_repo_name"></a> [repo\_name](#input\_repo\_name) | Git repo name. | `string` | `"google-fsi-accelerator-pattern"` | no |
| <a name="input_storage_class"></a> [storage\_class](#input\_storage\_class) | Bucket storage class. | `string` | `"STANDARD"` | no |

## Outputs

| Name | Description |
|------|-------------|
| <a name="output_airflow_uri"></a> [airflow\_uri](#output\_airflow\_uri) | URI of the Apache Airflow Web UI hosted within the Cloud Composer Environment. |
| <a name="output_be_services"></a> [be\_services](#output\_be\_services) | URLs list of backend services running on Cloud Run |
| <a name="output_bucket_names"></a> [bucket\_names](#output\_bucket\_names) | List of bucket names. |
| <a name="output_db_instance_connection_name"></a> [db\_instance\_connection\_name](#output\_db\_instance\_connection\_name) | The connection name of the DB master instance to be used in connection strings |
| <a name="output_django_admin_password"></a> [django\_admin\_password](#output\_django\_admin\_password) | Django admin user password |
| <a name="output_django_admin_url"></a> [django\_admin\_url](#output\_django\_admin\_url) | Django admin panel URL |
| <a name="output_fe_services"></a> [fe\_services](#output\_fe\_services) | URLs list of frontend services running on Cloud Run |
| <a name="output_ml_services"></a> [ml\_services](#output\_ml\_services) | URLs list of ML services running on Cloud Run |
<!-- END_TF_DOCS -->