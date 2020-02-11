resource "aws_security_group" "emr_master" {
  name = "${var.name} - EMR Master"
  description = "Security group for EMR master."
  vpc_id = var.vpc_id
  revoke_rules_on_delete = true

  ingress {
    from_port = 22
    to_port = 22
    protocol = "tcp"
    cidr_blocks = [
      var.ingress_cidr_blocks
    ]
  }

  egress {
    from_port = 0
    to_port = 0
    protocol = "-1"
    cidr_blocks = [
      "0.0.0.0/0"
    ]
  }

  tags = {
    Name = "${var.name} - EMR master"
  }
}

resource "aws_security_group" "emr_slave" {
  name = "${var.name} - EMR Slave"
  description = "Security group for EMR slave."
  vpc_id = var.vpc_id
  revoke_rules_on_delete = true

  ingress {
    from_port = 22
    to_port = 22
    protocol = "tcp"
    cidr_blocks = [
      var.ingress_cidr_blocks
    ]
  }

  egress {
    from_port = 0
    to_port = 0
    protocol = "-1"
    cidr_blocks = [
      "0.0.0.0/0"
    ]
  }

  tags = {
    Name = "${var.name} - EMR slave"
  }
}