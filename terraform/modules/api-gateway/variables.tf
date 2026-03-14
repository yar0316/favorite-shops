variable "api_name" {
  description = "Name of the REST API"
  type        = string
}

variable "environment" {
  description = "Environment (test or prod)"
  type        = string
}

variable "tags" {
  description = "Tags to apply to the resources"
  type        = map(string)
  default     = {}
}
