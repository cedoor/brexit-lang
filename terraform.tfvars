# General configuration.
name = "brexit-lang"
region = "eu-west-2"
caller_identity = "295036807698"
key_name = "amazon"

# Elastic search configuration.
elasticsearch_version = "7.1"
elasticsearch_instance_type = "t2.small.elasticsearch"
elasticsearch_instance_count = 3
elasticsearch_volume_size = 10

# EMR configuration.
emr_release_label = "emr-5.28.1"
emr_applications = [
  "Hadoop",
  "Spark"
]

# EMR master node configuration.
emr_master_instance_type = "m4.large"
emr_master_ebs_size = 50

# EMR slave nodes configuration.
emr_core_instance_type = "m4.large"
emr_core_instance_count = 2
emr_core_ebs_size = 50

