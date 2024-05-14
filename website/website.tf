#########################################################
# WEBSITE BUCKET - S3 Bucket for the website content
#########################################################
resource "aws_s3_bucket" "website_bucket" {
  bucket = local.website_bucket_name
}

resource "aws_s3_bucket_public_access_block" "website_bucket" {
  bucket = aws_s3_bucket.website_bucket.id

  block_public_acls       = false
  block_public_policy     = false
  ignore_public_acls      = false
  restrict_public_buckets = false
}

resource "aws_s3_bucket_website_configuration" "website_bucket" {
  bucket = aws_s3_bucket.website_bucket.id
  index_document {
    suffix = "index.html"
  }
}

resource "aws_s3_object" "website_homepage" {
  depends_on = [aws_s3_bucket.website_bucket]
  bucket     = local.website_bucket_name
  key        = "index.html"
  source     = "${path.module}/index.html"
  etag       = filemd5("${path.module}/index.html")

  content_type = "text/html"
}

resource "aws_s3_object" "website_functions" {
  depends_on = [aws_s3_bucket.website_bucket]
  bucket     = local.website_bucket_name
  key        = "main.js"
  source     = "${path.module}/main.js"
  etag       = filemd5("${path.module}/main.js")

  # content_type = "text/html"
}

resource "aws_s3_object" "website_css" {
  depends_on = [aws_s3_bucket.website_bucket]
  bucket     = local.website_bucket_name
  key        = "stylesheet.css"
  source     = "${path.module}/stylesheet.css"
  etag       = filemd5("${path.module}/stylesheet.css")

  # content_type = "text/html"
}

resource "aws_s3_bucket_policy" "public_access_to_website" {
  depends_on = [aws_s3_bucket_public_access_block.website_bucket]
  bucket     = aws_s3_bucket.website_bucket.id
  policy     = data.aws_iam_policy_document.public_website_access.json
}

resource "aws_s3_bucket_cors_configuration" "example" {
  bucket = aws_s3_bucket.website_bucket.id

  cors_rule {
    allowed_headers = ["*"]
    allowed_methods = ["PUT", "POST"]
    allowed_origins = ["*"]
    expose_headers  = ["ETag"]
    max_age_seconds = 3000
  }

  cors_rule {
    allowed_methods = ["GET"]
    allowed_origins = ["*"]
  }
}

resource "aws_route53_zone" "my_domain" {
  name = local.domain_name
}

resource "aws_route53_record" "my_domain_a_record" {
  zone_id = aws_route53_zone.my_domain.zone_id
  name    = local.domain_name
  type    = "A"
  alias {
    name                   = aws_s3_bucket_website_configuration.website_bucket.website_endpoint
    zone_id                = aws_s3_bucket.website_bucket.hosted_zone_id
    evaluate_target_health = true
  }
}

#########################################################
# DATA BUCKET - S3 Bucket for the underlying data
#########################################################
resource "aws_s3_bucket" "data_bucket" {
  bucket = local.data_bucket_name
}
