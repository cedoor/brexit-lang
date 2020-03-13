output "id" {
  value = aws_instance.ec2_cluster.*.id
}

output "public_dns" {
  value = aws_instance.ec2_cluster.*.public_dns
}

output "instance_count" {
  value = var.instance_count
}
