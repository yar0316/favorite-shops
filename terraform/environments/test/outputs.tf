output "dynamodb_table_name" {
  value = module.dynamodb.table_name
}

output "s3_bucket_name" {
  value = module.s3.bucket_name
}

output "api_gateway_id" {
  value = module.api_gateway.rest_api_id
}
