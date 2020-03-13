resource "aws_instance" "ec2_cluster" {
  count = var.instance_count

  ami = var.ami
  instance_type = var.instance_type
  key_name = var.key_name
  vpc_security_group_ids = var.vpc_security_group_ids
}