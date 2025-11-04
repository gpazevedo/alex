variable "aws_region" {
  description = "AWS region for DynamoDB tables"
  type        = string
  default     = "us-east-1"
}

variable "enable_point_in_time_recovery" {
  description = "Enable point-in-time recovery for DynamoDB tables (adds cost)"
  type        = bool
  default     = false
}

variable "enable_ttl" {
  description = "Enable TTL for automatic cleanup of old price history"
  type        = bool
  default     = true
}
