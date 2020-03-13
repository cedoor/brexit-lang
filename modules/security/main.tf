resource "aws_security_group" "ec2_security_group" {
  name = "${var.name} - EC2 security group"
  description = "Security group for EC2 instances."
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
}