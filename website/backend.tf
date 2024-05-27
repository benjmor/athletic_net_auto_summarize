terraform {
  backend "s3" {
    bucket = "238589881750-tf-remote-state"
    key    = "athleticsummary.tfstate"
    region = "us-east-1"
  }
}