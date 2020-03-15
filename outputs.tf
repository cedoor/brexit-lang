output "ec2_ids" {
  value = aws_instance.ec2_cluster.*.id
}

output "ec2_public_dns" {
  value = aws_instance.ec2_cluster.*.public_dns
}