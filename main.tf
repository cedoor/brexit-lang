resource "aws_instance" "ec2_cluster" {
  count = var.ec2_instance_count

  ami = var.ec2_ami
  instance_type = var.ec2_instance_type
  key_name = var.key_name
  vpc_security_group_ids = [
    var.vpc_security_group_id
  ]
}