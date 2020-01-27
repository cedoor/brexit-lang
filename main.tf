module "iam" {
  source = "./modules/iam"
}

module "emr" {
  source = "./modules/emr"

  name = var.name
  key_name = var.key_name
  release_label = var.emr_release_label
  applications = var.emr_applications
  master_instance_type = var.emr_master_instance_type
  master_ebs_size = var.emr_master_ebs_size
  core_instance_type = var.emr_core_instance_type
  core_instance_count = var.emr_core_instance_count
  core_ebs_size = var.emr_core_ebs_size
  ec2_instance_profile = module.iam.emr_ec2_instance_profile
  service_role = module.iam.emr_service_role
}

module "es" {
  source = "./modules/es"

  name = var.name
  caller_identity = var.caller_identity
  region = var.region
  elasticsearch_version = var.elasticsearch_version
  instance_count = var.elasticsearch_instance_count
  instance_type = var.elasticsearch_instance_type
  volume_size = var.elasticsearch_volume_size
}
