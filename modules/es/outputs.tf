output "id" {
  value = aws_elasticsearch_domain.es-domain.id
}

output "domain" {
  value = aws_elasticsearch_domain.es-domain.domain_name
}

output "version" {
  value = aws_elasticsearch_domain.es-domain.elasticsearch_version
}