#_____ ELASTIC SEARCH _____#

output "es_id" {
  value = module.es.id
}

#_____ EMR _____#

output "emr_id" {
  value = module.emr.id
}

output "emr_master_public_dns" {
  value = module.emr.master_public_dns
}