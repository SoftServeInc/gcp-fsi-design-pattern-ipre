variable "project_id" {
  description = "The ID of the project in which to provision resources."
  type        = string
}

variable "location" {
  description = "Bucket location."
  type        = string
  default     = "europe-west3"
}

variable "bq_location" {
  description = "The regional location for the dataset only US and EU are suitable for AutoML."
  type        = string
  default     = "EU"
}

variable "storage_class" {
  description = "Bucket storage class."
  type        = string
  default     = "STANDARD"
}

variable "env" {
  description = "Application environment."
  type        = string
  default     = "test"
}

variable "composer_machine_type" {
  description = "Machine type of Cloud Composer nodes."
  type        = string
  default     = "e2-medium"
}

variable "composer_subnet" {
  description = "Subnetwork where Cloud Composer is created."
  type        = string
  default     = "10.2.0.0/16"
}

variable "platform" {
  description = "Platform CLI will run on. Defaults to linux. Valid values: linux, darwin."
  default     = "linux"
}

variable "repo_name" {
  description = "Git repo name."
  default     = "google-fsi-accelerator-pattern"
}

variable "db_tier" {
  description = "The tier for the master instance."
  type        = string
  default     = "db-f1-micro"
}

variable "db_availability_type" {
  description = "The availability type for the master instance. Can be either `REGIONAL` or `null`."
  type        = string
  default     = null
}

variable "db_assign_public_ip" {
  description = "Set to true if the master instance should also have a public IP (less secure)."
  type        = string
  default     = true
}
