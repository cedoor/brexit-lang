variable "name" {}
variable "key_name" {}
variable "release_label" {}
variable "applications" {
  type = list(string)
}
variable "master_instance_type" {}
variable "master_ebs_size" {}
variable "core_instance_type" {}
variable "core_instance_count" {}
variable "core_ebs_size" {}
variable "ec2_instance_profile" {}
variable "service_role" {}