#_____ ELASTIC SEARCH _____#

//output "es_id" {
//  value = module.es.id
//}

#_____ EMR _____#

//output "emr_id" {
//  value = module.emr.id
//}
//
//output "emr_master_public_dns" {
//  value = module.emr.master_public_dns
//}

#_____ EC2 _____#

output "ec2_id" {
  value = module.ec2.id
}

output "ec2_public_dns" {
  value = module.ec2.public_dns
}