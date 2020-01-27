# EMR configuration.
resource "aws_emr_cluster" "emr-cluster" {
  name = var.name
  release_label = var.release_label
  applications = var.applications

  ec2_attributes {
    key_name = var.key_name
    instance_profile = var.ec2_instance_profile
  }

  master_instance_group {
    name = "EMR master"
    instance_type = var.master_instance_type
    instance_count = 1
  }

  core_instance_group {
    name = "EMR slave"
    instance_type = var.core_instance_type
    instance_count = var.core_instance_count
  }

  service_role = var.service_role

  tags = {
    Name = "${var.name} - cluster"
  }

  configurations_json = <<EOF
    [
    {
    "Classification": "spark-defaults",
      "Properties": {
      "maximizeResourceAllocation": "true",
      "spark.dynamicAllocation.enabled": "true"
      }
    }
  ]
  EOF
}
