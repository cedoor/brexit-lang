output "id" {
  value = aws_emr_cluster.emr_cluster.id
}

output "name" {
  value = aws_emr_cluster.emr_cluster.name
}

output "master_public_dns" {
  value = aws_emr_cluster.emr_cluster.master_public_dns
}
