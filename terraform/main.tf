locals {
  bucket_names = concat(
    ["dataflow-assets", "be-static"],
    values(local.datasets),
    [for value in values(local.datasets) : "predicted-${value}"],
    ["capital-markets-quotes"]
  )
  datasets = {
    "capital_markets_returns"   = "capital-markets-returns",
    "investor_risk_preferences" = "investor-risk-preferences"
  }
  tickers_list              = jsondecode(file("${path.module}/../advanced-analytics/data-pipelines/capital-markets-returns/data/settings.json"))
  ml_apps                   = toset(["recommendation-engine"])
  backend_apps              = toset(["ui-fulfillment"])
  frontend_apps             = toset(["ui"])
  be_host                   = data.google_cloud_run_service.be["ui-fulfillment"].status[0].url
  ml_host                   = data.google_cloud_run_service.ml["recommendation-engine"].status[0].url
  db_secret                 = "mysql://default:${module.cloudsql_db.generated_user_password}@/default?unix_socket=/cloudsql/${module.cloudsql_db.instance_connection_name}"
  django_secret_key         = random_string.django_sec.result
  django_admin_url          = random_string.django_admin.result
  django_superuser_password = random_string.django_admin_password.result
  django_settings_module    = "config.settings.production"
  django_allowed_hosts      = ".run.app"
}

resource "random_string" "rand" {
  length  = 4
  upper   = false
  special = false
}

resource "random_string" "django_sec" {
  length  = 20
  upper   = true
  number  = true
  special = false
}

resource "random_string" "django_admin" {
  length  = 10
  upper   = true
  number  = true
  special = false
}

resource "random_string" "django_admin_password" {
  length  = 30
  upper   = true
  number  = true
  special = false
}

resource "google_sourcerepo_repository" "repo" {
  project = var.project_id
  name    = var.repo_name
}

resource "null_resource" "push_cs_repo" {
  provisioner "local-exec" {
    command = <<-EOL
                cd ${path.module}/../
                git config credential.https://source.developers.google.com.helper gcloud.sh
                git remote set-url origin ${google_sourcerepo_repository.repo.url}
                git push --all origin
              EOL
  }
}

module "cloud_storage" {
  source  = "terraform-google-modules/cloud-storage/google"
  version = "~> 2.0.0"

  project_id         = var.project_id
  prefix             = "${var.env}-${random_string.rand.result}"
  names              = local.bucket_names
  location           = var.location
  storage_class      = var.storage_class
  labels             = { env = var.env }
  force_destroy      = { for bucket in local.bucket_names : bucket => true }
  bucket_policy_only = { "be-static" = false }
}

module "bigquery" {
  for_each = local.datasets

  source  = "terraform-google-modules/bigquery/google"
  version = "~> 5.0.0"

  project_id                 = var.project_id
  location                   = var.bq_location
  dataset_id                 = "${var.env}_${each.key}"
  delete_contents_on_destroy = true
  tables = [
    {
      table_id           = each.key,
      schema             = file("${path.module}/../advanced-analytics/data-pipelines/${each.value}/bq/${each.value}.json"),
      time_partitioning  = null,
      range_partitioning = null,
      expiration_time    = null,
      clustering         = [],
      labels = {
        env = var.env
      },
    }
  ]
  dataset_labels = {
    env = var.env
  }
}

data "google_compute_zones" "available" {
  project = var.project_id
  region  = var.location
  status  = "UP"
}

resource "random_shuffle" "az" {
  input        = data.google_compute_zones.available.names
  result_count = 1
}

module "composer_sa" {
  source      = "terraform-google-modules/service-accounts/google"
  version     = "~> 4.0.0"
  project_id  = var.project_id
  prefix      = var.env
  names       = ["composer-sa"]
  description = "Service account for ${var.env} Composer environment"
  project_roles = [
    "${var.project_id}=>roles/composer.worker",
    "${var.project_id}=>roles/dataflow.admin",
    "${var.project_id}=>roles/iam.serviceAccountUser",
    "${var.project_id}=>roles/bigquery.admin"
  ]
}

data "google_compute_default_service_account" "default" {
  project = var.project_id
}

module "default_sa_roles" {
  source  = "terraform-google-modules/iam/google//modules/member_iam"
  version = "~> 7.1.0"

  service_account_address = data.google_compute_default_service_account.default.email
  project_id              = var.project_id
  project_roles           = ["roles/bigquery.dataEditor", "roles/cloudsql.client"]
  prefix                  = "serviceAccount"
}

module "network_private" {
  source  = "terraform-google-modules/network/google"
  version = "~> 3.2.2"

  project_id   = var.project_id
  network_name = "${var.env}-private"

  subnets = [
    {
      subnet_name           = "${var.env}-composer-subnetwork"
      subnet_ip             = var.composer_subnet
      subnet_region         = var.location
      subnet_private_access = "true"
      description           = "Cloud Composer subnet"
    }
  ]

  firewall_rules = [
    {
      name        = "dataflow"
      description = "Dataflow workers interconnect"
      direction   = "INGRESS"
      source_tags = ["dataflow"]
      target_tags = ["dataflow"]
      allow = [{
        protocol = "tcp"
        ports    = ["12345", "12346"]
      }]
    }
  ]
}

module "private_service_access" {
  source  = "GoogleCloudPlatform/sql-db/google//modules/private_service_access"
  version = "~> 5.0.0"

  project_id  = var.project_id
  vpc_network = module.network_private.network_name

  depends_on = [module.network_private]
}

module "composer" {
  source  = "terraform-google-modules/composer/google//modules/create_environment"
  version = "~> 1.0.0"

  project_id               = var.project_id
  region                   = var.location
  zone                     = join(",", random_shuffle.az.result)
  network                  = module.network_private.network_name
  subnetwork               = join(",", module.network_private.subnets_names)
  composer_env_name        = "${var.env}-composer-env"
  composer_service_account = module.composer_sa.email
  machine_type             = var.composer_machine_type

  env_variables = {
    AIRFLOW_VAR_PROJECT_ID     = var.project_id
    AIRFLOW_VAR_GCE_REGION     = var.location
    AIRFLOW_VAR_GCE_ZONE       = join(",", random_shuffle.az.result)
    AIRFLOW_VAR_BUCKET_PATH    = "gs://${lookup(module.cloud_storage.buckets_map["dataflow-assets"], "name")}"
    AIRFLOW_VAR_GCE_NETWORK    = module.network_private.network_name
    AIRFLOW_VAR_GCE_SUBNETWORK = join(",", module.network_private.subnets_names)
  }

  airflow_config_overrides = {
    api-auth_backend            = "airflow.api.auth.backend.default"
    scheduler-job_heartbeat_sec = "30"
  }
}

resource "google_storage_bucket_object" "schema" {
  for_each = local.datasets

  name = "${each.value}/composer/${each.value}.json"
  content = templatefile("${path.module}/../advanced-analytics/data-pipelines/common/composer/dataflow-schema.tmpl", {
    table_schema = file("${path.module}/../advanced-analytics/data-pipelines/${each.value}/bq/${each.value}.json")
  })
  bucket = lookup(module.cloud_storage.buckets_map["dataflow-assets"], "name")
}

resource "google_storage_bucket_object" "udf" {
  for_each = local.datasets

  name = "${each.value}/composer/transformCSVtoJSON.js"
  content = templatefile("${path.module}/../advanced-analytics/data-pipelines/common/composer/transformCSVtoJSON.tmpl", {
    properties = jsondecode(file("${path.module}/../advanced-analytics/data-pipelines/${each.value}/bq/${each.value}.json")).*.name
  })
  bucket = lookup(module.cloud_storage.buckets_map["dataflow-assets"], "name")
}

resource "google_storage_bucket_object" "dag" {
  for_each = local.datasets

  name = "dags/composer-dataflow-dag-${each.value}.py"
  content = templatefile("${path.module}/../advanced-analytics/data-pipelines/${each.value}/composer/dag.tmpl", {
    input_bucket     = lookup(module.cloud_storage.buckets_map[each.value], "name"),
    predicted_bucket = lookup(module.cloud_storage.buckets_map["predicted-${each.value}"], "name")
    env              = var.env,
    dataset_name     = each.key,
    file_name        = each.value,
    bq_location      = var.bq_location,
    tickers_list     = local.tickers_list.tickers
  })
  bucket = element(split("/", module.composer.gcs_bucket), 2)
}

module "gen_data_function" {
  for_each = local.datasets

  # source  = "terraform-google-modules/event-function/google"
  # version = "~> 2.0.0"
  source = "github.com/terraform-google-modules/terraform-google-scheduled-function?ref=v2.0.0"

  project_id = var.project_id
  region     = var.location

  function_name                  = "${var.env}-${each.value}-gen-data"
  function_description           = "Generating ${each.value} files and save them into the GCS buckets"
  function_entry_point           = each.key
  function_source_directory      = "${path.module}/../advanced-analytics/data-pipelines/${each.value}/data"
  function_runtime               = "python39"
  function_service_account_email = module.fuction_service_account.email
  function_available_memory_mb   = 1024
  function_timeout_s             = 540
  bucket_name                    = "${var.env}-${random_string.rand.result}-${each.value}-gen-data"
  function_environment_variables = each.key == "capital_markets_returns" ? {
    QUOTES_BUCKET_NAME  = lookup(module.cloud_storage.buckets_map["capital-markets-quotes"], "name")
    RETURNS_BUCKET_NAME = lookup(module.cloud_storage.buckets_map[each.value], "name")
    QUOTES_BLOB_NAME    = "capital-markets-quotes.csv"
    RETURNS_BLOB_NAME   = "${each.value}.csv"
    PROJECT_NAME        = var.project_id
    } : {
    BUCKET_NAME  = lookup(module.cloud_storage.buckets_map[each.value], "name")
    BLOB_NAME    = "${each.value}.csv"
    PROJECT_NAME = var.project_id
  }

  job_description = "Trigger ${var.env}-${each.value}-gen-data function"
  job_name        = "${var.env}-${each.value}-gen-data"
  job_schedule    = each.key == "capital_markets_returns" ? "0 1 * * *" : "0 0 29 2 1"
  topic_name      = "${var.env}-${each.value}-gen-data"

  function_source_archive_bucket_labels = {
    env = var.env
  }
  function_labels = {
    env = var.env
  }
}

resource "time_sleep" "gen_data_function" {
  depends_on = [module.gen_data_function]

  create_duration = "30s"
}

module "trigger_cf" {
  for_each = local.datasets

  source  = "terraform-google-modules/gcloud/google"
  version = "~> 3.0.0"

  platform = var.platform

  create_cmd_body = "scheduler jobs run ${lookup(module.gen_data_function[each.key].scheduler_job, "id")}"
  create_cmd_triggers = {
    bq_table = join(",", module.bigquery[each.key].table_names)
  }

  module_depends_on = [time_sleep.trigger_dag_function, time_sleep.gen_data_function]
}

resource "null_resource" "python_requirements" {
  provisioner "local-exec" {
    command     = "pip3 install -r ./scripts/requirements.txt"
    interpreter = ["bash", "-c"]
  }
}

data "external" "composer_client_id" {
  program = ["python3", "${path.module}/scripts/client-id.py"]

  query = {
    project_id           = var.project_id
    location             = var.location
    composer_environment = module.composer.composer_env_name
  }
  depends_on = [null_resource.python_requirements, module.composer.composer_env_name]
}

resource "local_file" "cf_trigger_dag" {
  for_each = local.datasets

  content = templatefile("${path.module}/../advanced-analytics/data-pipelines/common/dag-trigger/main.tmpl", {
    webserver_url = module.composer.airflow_uri,
    client_id     = lookup(data.external.composer_client_id.result, "client_id"),
    dag_name      = "${each.value}-dag"
  })
  filename = "${path.module}/../advanced-analytics/data-pipelines/common/dag-trigger/tmp/${each.value}/main.py"
}

resource "local_file" "cf_trigger_req" {
  for_each = local.datasets

  source   = "${path.module}/../advanced-analytics/data-pipelines/common/dag-trigger/requirements.txt"
  filename = "${path.module}/../advanced-analytics/data-pipelines/common/dag-trigger/tmp/${each.value}/requirements.txt"
}

module "fuction_service_account" {
  source  = "terraform-google-modules/service-accounts/google"
  version = "~> 4.0.0"

  project_id = var.project_id
  prefix     = ""
  names      = ["cloudfunction-sa"]
  project_roles = [
    "${var.project_id}=>roles/composer.user",
    "${var.project_id}=>roles/storage.objectAdmin",
  ]
  description = "Cloud Function Service Account"
}

module "trigger_dag_function" {
  for_each = local.datasets

  # source  = "terraform-google-modules/event-function/google"
  # version = "~> 2.0.0"
  source = "github.com/terraform-google-modules/terraform-google-event-function?ref=bot-add-module-attribution"

  description = "Triger Composer DAG for new files in GCS bucket"
  entry_point = "trigger_dag"

  event_trigger = {
    event_type = "google.storage.object.finalize"
    resource   = lookup(module.cloud_storage.buckets_map[each.value], "name")
  }

  name                  = "${var.env}-${each.value}-dag-trigger"
  project_id            = var.project_id
  region                = var.location
  source_directory      = "${path.module}/../advanced-analytics/data-pipelines/common/dag-trigger/tmp/${each.value}"
  runtime               = "python39"
  service_account_email = module.fuction_service_account.email
  bucket_name           = "${var.env}-${random_string.rand.result}-${each.value}-dag-trigger"
  bucket_labels = {
    env = var.env
  }
  labels = {
    env = var.env
  }

  source_dependent_files = [local_file.cf_trigger_dag[each.key], local_file.cf_trigger_req[each.key]]
  depends_on             = [google_storage_bucket_object.dag]
}

resource "time_sleep" "trigger_dag_function" {
  depends_on = [module.trigger_dag_function]

  create_duration = "30s"
}

module "cloudsql_db" {
  source  = "GoogleCloudPlatform/sql-db/google//modules/safer_mysql"
  version = "~> 5.0.0"

  project_id           = var.project_id
  name                 = "${var.env}-metadata-db"
  random_instance_name = true
  database_version     = "MYSQL_8_0"
  zone                 = join(",", random_shuffle.az.result)
  region               = var.location
  tier                 = var.db_tier
  availability_type    = var.db_availability_type
  assign_public_ip     = var.db_assign_public_ip
  vpc_network          = module.network_private.network_self_link
  deletion_protection  = false

  module_depends_on = [module.private_service_access.peering_completed]
}

resource "google_app_engine_application" "app" {
  project     = var.project_id
  location_id = var.location
}

resource "google_project_service_identity" "cb_sa" {
  provider = google-beta

  project = var.project_id
  service = "cloudbuild.googleapis.com"
}

module "cb_sa_roles" {
  source  = "terraform-google-modules/iam/google//modules/member_iam"
  version = "~> 7.1.0"

  service_account_address = google_project_service_identity.cb_sa.email
  project_id              = var.project_id
  project_roles           = ["roles/run.admin", "roles/iam.serviceAccountUser", "roles/cloudsql.client", "roles/storage.objectAdmin"]
  prefix                  = "serviceAccount"
}

resource "google_cloudbuild_trigger" "ml_main_branch" {
  for_each = local.ml_apps

  project        = var.project_id
  name           = "${var.env}-${each.key}-main"
  filename       = "advanced-analytics/${each.key}/cloudbuild.yaml"
  included_files = ["advanced-analytics/${each.key}/**"]

  trigger_template {
    branch_name = "^main$"
    repo_name   = var.repo_name
  }

  substitutions = {
    _ENV                      = var.env
    _REGION                   = var.location
    _NAME                     = each.key
    _PROJECT_ID               = var.project_id
    _QUOTES_BUCKET            = lookup(module.cloud_storage.buckets_map["capital-markets-quotes"], "name")
    _QUOTES_BLOB              = "capital-markets-quotes.csv"
    _PREDICTED_RETURNS_BUCKET = lookup(module.cloud_storage.buckets_map["predicted-capital-markets-returns"], "name")
    _PREDICTED_RETURNS_BLOB   = "capital-markets-returns-forecasted.csv"
    _PREDICTED_IRP_BUCKET     = lookup(module.cloud_storage.buckets_map["predicted-investor-risk-preferences"], "name")
    _PREDICTED_IRP_BLOB       = "predicted_risk_000000000000.csv"
  }

  depends_on = [null_resource.push_cs_repo]
}

module "deploy_ml_apps" {
  for_each = local.ml_apps

  source  = "terraform-google-modules/gcloud/google"
  version = "~> 3.0.0"

  platform = var.platform

  create_cmd_entrypoint  = "gcloud"
  create_cmd_body        = <<-EOL
                          builds submit ${path.module}/../ --project ${var.project_id} --config=${path.module}/../advanced-analytics/${each.key}/cloudbuild.yaml \
                          --substitutions SHORT_SHA=${random_string.rand.result},\
                          _REGION=${var.location},\
                          _NAME=${each.key},\
                          _PROJECT_ID=var.project_id,\
                          _QUOTES_BUCKET=${lookup(module.cloud_storage.buckets_map["capital-markets-quotes"], "name")},\
                          _QUOTES_BLOB='capital-markets-quotes.csv',\
                          _PREDICTED_RETURNS_BUCKET=${lookup(module.cloud_storage.buckets_map["predicted-capital-markets-returns"], "name")},\
                          _PREDICTED_RETURNS_BLOB='capital_market_returns_forecasted.csv',\
                          _PREDICTED_IRP_BUCKET=${lookup(module.cloud_storage.buckets_map["predicted-investor-risk-preferences"], "name")},\
                          _PREDICTED_IRP_BLOB='predicted_risk_000000000000.csv'
                          EOL
  destroy_cmd_entrypoint = "gcloud"
  destroy_cmd_body       = "run services delete ${each.key} --project ${var.project_id} --region ${var.location} --platform=managed --quiet"

  module_depends_on = [google_cloudbuild_trigger.ml_main_branch[each.key].id]
}

data "google_cloud_run_service" "ml" {
  for_each = local.ml_apps

  project  = var.project_id
  location = var.location
  name     = each.key

  depends_on = [module.deploy_ml_apps.wait]
}

resource "google_cloudbuild_trigger" "backend_main_branch" {
  for_each = local.backend_apps

  project        = var.project_id
  name           = "${var.env}-${each.key}-main"
  filename       = "backend/${each.key}/cloudbuild.yaml"
  included_files = ["backend/${each.key}/**"]

  trigger_template {
    branch_name = "^main$"
    repo_name   = var.repo_name
  }

  substitutions = {
    _ENV                       = var.env
    _REGION                    = var.location
    _NAME                      = each.key
    _CLOUDSQL_INSTANCE         = module.cloudsql_db.instance_connection_name
    _DB_SECRET                 = local.db_secret
    _DJANGO_SECRET_KEY         = local.django_secret_key
    _DJANGO_ADMIN_URL          = local.django_admin_url
    _DJANGO_SUPERUSER_PASSWORD = local.django_superuser_password
    _DJANGO_SETTINGS_MODULE    = local.django_settings_module
    _DJANGO_ALLOWED_HOSTS      = local.django_allowed_hosts
    _ML_SERVICE_URL            = local.ml_host
    _GS_BUCKET_NAME            = lookup(module.cloud_storage.buckets_map["be-static"], "name")
  }
}

module "deploy_backend_apps" {
  for_each = local.backend_apps

  source  = "terraform-google-modules/gcloud/google"
  version = "~> 3.0.0"

  platform = var.platform

  create_cmd_entrypoint  = "gcloud"
  create_cmd_body        = <<-EOL
                          builds submit ${path.module}/../ --project ${var.project_id} --config=${path.module}/../backend/${each.key}/cloudbuild.yaml \
                          --substitutions SHORT_SHA=${random_string.rand.result},\
                          _REGION=${var.location},\
                          _NAME=${each.key},\
                          _CLOUDSQL_INSTANCE=${module.cloudsql_db.instance_connection_name},\
                          _DB_SECRET=${local.db_secret},\
                          _DJANGO_SECRET_KEY=${local.django_secret_key},\
                          _DJANGO_ADMIN_URL=${local.django_admin_url},\
                          _DJANGO_SUPERUSER_PASSWORD=${local.django_superuser_password},\
                          _DJANGO_SETTINGS_MODULE=${local.django_settings_module},\
                          _DJANGO_ALLOWED_HOSTS=${local.django_allowed_hosts},\
                          _ML_SERVICE_URL=${local.ml_host},\
                          _GS_BUCKET_NAME=${lookup(module.cloud_storage.buckets_map["be-static"], "name")}
                          EOL
  destroy_cmd_entrypoint = "gcloud"
  destroy_cmd_body       = "run services delete ${each.key} --project ${var.project_id} --region ${var.location} --platform=managed --quiet"

  module_depends_on = [google_cloudbuild_trigger.backend_main_branch[each.key].id, module.cloudsql_db.instance_name]
}

data "google_cloud_run_service" "be" {
  for_each = local.backend_apps

  project  = var.project_id
  location = var.location
  name     = each.key

  depends_on = [module.deploy_backend_apps.wait]
}

resource "google_cloudbuild_trigger" "frontend_main_branch" {
  for_each = local.frontend_apps

  project        = var.project_id
  name           = "${var.env}-${each.key}-main"
  filename       = "frontend/${each.key}/cloudbuild.yaml"
  included_files = ["frontend/${each.key}/**"]

  trigger_template {
    branch_name = "^main$"
    repo_name   = var.repo_name
  }

  substitutions = {
    _ENV               = var.env
    _REGION            = var.location
    _NAME              = each.key
    _REACT_APP_API_URL = local.be_host
  }
}

module "deploy_frontend_apps" {
  for_each = local.frontend_apps

  source  = "terraform-google-modules/gcloud/google"
  version = "~> 3.0.0"

  platform = var.platform

  create_cmd_entrypoint  = "gcloud"
  create_cmd_body        = <<-EOL
                          builds submit ${path.module}/../ --project ${var.project_id} --config=${path.module}/../frontend/${each.key}/cloudbuild.yaml \
                          --substitutions SHORT_SHA=${random_string.rand.result},\
                          _REGION=${var.location},\
                          _NAME=${each.key},\
                          _REACT_APP_API_URL=${local.be_host}
                          EOL
  destroy_cmd_entrypoint = "gcloud"
  destroy_cmd_body       = "run services delete ${each.key} --project ${var.project_id} --region ${var.location} --platform=managed --quiet"

  module_depends_on = [google_cloudbuild_trigger.frontend_main_branch[each.key].id]
}

data "google_cloud_run_service" "fe" {
  for_each = local.frontend_apps

  project  = var.project_id
  location = var.location
  name     = each.key

  depends_on = [module.deploy_frontend_apps.wait]
}
