locals {
  account_id            = data.aws_caller_identity.current.account_id
  protected_branch_name = "main"
  # rvm_assumption_policy = jsonencode({
  #   "Version" : "2012-10-17",
  #   "Statement" : [
  #     {
  #       "Effect" : "Allow",
  #       "Action" : [
  #         "sts:TagSession",
  #         "sts:SetSourceIdentity",
  #         "sts:AssumeRole"
  #       ],
  #       "Resource" : [
  #         "arn:aws:iam::*:role/${var.iam_assuming_role_name}"
  #       ]
  #     }
  #   ]
  # })
  # rvm_readonly_assumption_policy = jsonencode({
  #   "Version" : "2012-10-17",
  #   "Statement" : [
  #     {
  #       "Effect" : "Allow",
  #       "Action" : [
  #         "sts:TagSession",
  #         "sts:SetSourceIdentity",
  #         "sts:AssumeRole"
  #       ],
  #       "Resource" : [
  #         "arn:aws:iam::*:role/${var.iam_assuming_role_name}-readonly"
  #       ]
  #     }
  #   ]
  # })
  athleticnet_modify_policy = jsonencode({
    "Version" : "2012-10-17",
    "Statement" : [
      {
        "Effect" : "Allow",
        "Action" : [
          "s3:*",
        ],
        "Resource" : [
          "arn:aws:s3:::athleticsummary.net/",
          "arn:aws:s3:::athleticsummary.net/*",
          "arn:aws:s3:::docker-selenium-lambda-pr-serverlessdeploymentbuck-*",
        ]
      },
      {
        "Effect" : "Allow",
        "Action" : [
          "lambda:*",
        ],
        "Resource" : [
          "arn:aws:lambda:us-east-1:238589881750:function:athleticsummary_api_lambda_function",
          "arn:aws:lambda:us-east-1:238589881750:function:docker-selenium-lambda-prod-athleticnetsummary",
        ]
      },
      {
        "Effect" : "Allow",
        "Action" : [
          "ecr:*",
        ],
        "Resource" : [
          "arn:aws:ecr:us-east-1:238589881750:repository/serverless-docker-selenium-lambda-prod"
        ]
      },
      {
        "Effect" : "Allow",
        "Action" : [
          "cloudformation:*",
        ],
        "Resource" : [
          "arn:aws:cloudformation:us-east-1:238589881750:stack/docker-selenium-lambda-prod",
          "arn:aws:cloudformation:us-east-1:238589881750:stack/docker-selenium-lambda-prod/*"
        ]
      },
      {
        "Effect" : "Allow",
        "Action" : [
          "events:PutRule",
          "events:PutTargets",
          "events:DeleteRule",
          "events:RemoveTargets"
        ],
        "Resource" : [
          "*",
        ]
      }
    ]
  })
  terraform_state_policy = jsonencode({
    "Version" : "2012-10-17",
    "Statement" : [
      {
        "Effect" : "Allow",
        "Action" : [
          "s3:ListBucket",
          "s3:GetObject",
          "s3:PutObject",
          "s3:DeleteObject",
        ],
        "Resource" : [
          "arn:aws:s3:::${local.account_id}-${var.bucket_suffix}",
          "arn:aws:s3:::${local.account_id}-${var.bucket_suffix}/*",
        ]
      },
      {
        "Effect" : "Allow",
        "Action" : [
          "dynamodb:GetItem",
          "dynamodb:PutItem",
          "dynamodb:DeleteItem"
        ],
        "Resource" : [
          "arn:aws:dynamodb:*:${local.account_id}:table/${var.ddb_lock_table_name}"
        ]
      }
    ]
  })
}