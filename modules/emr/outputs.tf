output "id" {
  value = aws_emr_cluster.emr-cluster.id
}

output "name" {
  value = aws_emr_cluster.emr-cluster.name
}

output "master_public_dns" {
  value = aws_emr_cluster.emr-cluster.master_public_dns
}
