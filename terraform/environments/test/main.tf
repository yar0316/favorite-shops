terraform {
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
  }
}

provider "aws" {
  region = "ap-northeast-1"

  default_tags {
    tags = {
      Project     = "favorite-shops"
      Environment = "test"
      ManagedBy   = "terraform"
    }
  }
}

module "dynamodb" {
  source      = "../../modules/dynamodb"
  table_name  = "favorite-shops-test"
  environment = "test"
}

module "s3" {
  source      = "../../modules/s3"
  bucket_name = "favorite-shops-test-images"
  environment = "test"
}

module "api_gateway" {
  source      = "../../modules/api-gateway"
  api_name    = "favorite-shops-test-api"
  environment = "test"
}
