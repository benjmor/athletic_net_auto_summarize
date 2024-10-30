data "aws_caller_identity" "current" {}
data "aws_region" "current" {}


data "archive_file" "lambda_source" {
  type        = "zip"
  source_file = "${path.module}/website_lambda/website_lambda.py"
  output_path = "${path.module}/website_lambda/website_lambda.zip"
}

data "aws_iam_policy_document" "public_website_access" {
  statement {
    principals {
      type        = "AWS"
      identifiers = ["*"]
    }

    actions = [
      "s3:GetObject",
      "s3:ListBucket",
    ]

    resources = [
      aws_s3_bucket.website_bucket.arn,
      "${aws_s3_bucket.website_bucket.arn}/*",
    ]
  }
}

data "aws_iam_policy_document" "lambda_s3_writes" {
  statement {

    actions = [
      "s3:GetObject*",
      "s3:PutObject",
      "s3:ListBucket",
    ]

    resources = [
      aws_s3_bucket.data_bucket.arn,
      "${aws_s3_bucket.data_bucket.arn}/*",
    ]
  }
  statement {
    actions = [
      "lambda:InvokeFunction",
    ]
    resources = [
      "arn:aws:lambda:${data.aws_region.current.name}:${data.aws_caller_identity.current.account_id}:function:${local.summary_lambda_function_name}",
    ]
  }
  # TODO - scope down these permissions to just what is needed
  statement {
    actions = [
      "bedrock-runtime:*",
      "bedrock:*",
    ]
    resources = [
      "*",
    ]
  }
}

data "aws_iam_policy_document" "summmarizer_role" {
  statement {

    actions = [
      "s3:GetObject*",
      "s3:PutObject",
      "s3:ListBucket",
    ]

    resources = [
      aws_s3_bucket.data_bucket.arn,
      "${aws_s3_bucket.data_bucket.arn}/*",
    ]
  }

  statement {
    actions = [
      "sns:Publish",
    ]
    resources = [
      "*",
    ]
  }
}