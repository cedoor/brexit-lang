variable "name" {}
variable "region" {}
variable "caller_identity" {}
variable "key_name" {}

variable "elasticsearch_version" {}
variable "elasticsearch_instance_type" {}
variable "elasticsearch_instance_count" {}
variable "elasticsearch_volume_size" {}

variable "emr_release_label" {}
variable "emr_applications" {
  type = list(string)
}

variable "emr_master_instance_type" {}
variable "emr_master_ebs_size" {}

variable "emr_core_instance_type" {}
variable "emr_core_instance_count" {}
variable "emr_core_ebs_size" {}