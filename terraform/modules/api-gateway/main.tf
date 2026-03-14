resource "aws_api_gateway_rest_api" "this" {
  name        = var.api_name
  description = "API Gateway for favorite-shops ${var.environment} environment"

  endpoint_configuration {
    types = ["REGIONAL"]
  }

  tags = merge(
    var.tags,
    {
      Name        = var.api_name
      Environment = var.environment
    }
  )
}

# The deployment and stage will be managed either here later or in the environment layer once Lambdas are attached.
# For now, we just create the REST API container.
