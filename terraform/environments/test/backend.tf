terraform {
  backend "s3" {
    bucket         = "favorite-shops-tfstate"
    key            = "test/terraform.tfstate"
    region         = "ap-northeast-1"
    dynamodb_table = "favorite-shops-tfstate-lock"
    encrypt        = true
  }
}
