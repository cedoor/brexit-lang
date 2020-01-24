resource "aws_elasticsearch_domain" "es-domain" {
  domain_name = var.name
  elasticsearch_version = var.elasticsearch_version

  cluster_config {
    instance_type = var.instance_type
    instance_count = var.instance_count
  }

  ebs_options {
    ebs_enabled = true
    volume_size = var.volume_size
  }

  tags = {
    Name = "${var.name} - Elastic search cluster"
  }
}

resource "aws_elasticsearch_domain_policy" "es-policy-document" {
  domain_name = aws_elasticsearch_domain.es-domain.domain_name
  access_policies = <<POLICY
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Principal": {
        "AWS": "*"
      },
      "Action": [
        "es:*"
      ],
      "Resource": "arn:aws:es:${var.region}:${var.caller_identity}:domain/${var.name}/*"
    }
  ]
}
POLICY
}