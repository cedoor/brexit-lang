# Elastic search output variables.
//output "es_id" {
//  value = module.es.id
//}
//
//output "es_domain" {
//  value = module.es.domain
//}

# EMR output variables.
output "emr_id" {
  value = module.emr.id
}

output "emr_name" {
  value = module.emr.name
}

output "emr_master_public_dns" {
  value = module.emr.master_public_dns
}