resource "aws_route53domains_registered_domain" "athletic_summary" {
  domain_name   = local.domain_name
  transfer_lock = false
}

import {
  to = aws_route53domains_registered_domain.athletic_summary
  id = "athleticsummary.net" # TODO - validate
}

