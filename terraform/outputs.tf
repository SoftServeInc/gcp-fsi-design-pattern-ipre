output "bucket_names" {
  description = "List of bucket names."
  value       = module.cloud_storage.names_list
}

output "airflow_uri" {
  value       = module.composer.airflow_uri
  description = "URI of the Apache Airflow Web UI hosted within the Cloud Composer Environment."
}

output "db_instance_connection_name" {
  value       = module.cloudsql_db.instance_connection_name
  description = "The connection name of the DB master instance to be used in connection strings"
}

output "ml_services" {
  value = { for service in data.google_cloud_run_service.ml :
    service.name => service.status[0].url
  }
  description = "URLs list of ML services running on Cloud Run"
}

output "be_services" {
  value = { for service in data.google_cloud_run_service.be :
    service.name => service.status[0].url
  }
  description = "URLs list of backend services running on Cloud Run"
}

output "fe_services" {
  value = { for service in data.google_cloud_run_service.fe :
    service.name => service.status[0].url
  }
  description = "URLs list of frontend services running on Cloud Run"
}

output "django_admin_password" {
  value       = random_string.django_admin_password.result
  description = "Django admin user password"
}

output "django_admin_url" {
  value       = "${data.google_cloud_run_service.be["ui-fulfillment"].status[0].url}/${random_string.django_admin.result}"
  description = "Django admin panel URL"
}
