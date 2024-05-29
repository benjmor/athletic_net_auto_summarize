locals {
  website_bucket_name          = "athleticsummary.net" # Yes, this needs to match the website name for S3 website to work
  data_bucket_name             = "athletic-net-summaries-data-bucket"
  summary_lambda_function_name = "docker-selenium-lambda-prod-athleticnetsummary"
  domain_name                  = "athleticsummary.net"
}
