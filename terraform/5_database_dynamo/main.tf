terraform {
  required_version = ">= 1.5"

  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
  }

  # Using local backend - state will be stored in terraform.tfstate in this directory
  # This is automatically gitignored for security
}

provider "aws" {
  region = var.aws_region
}

# Data source for current caller identity
data "aws_caller_identity" "current" {}

# ========================================
# Table 1: Users Data (user-specific data)
# ========================================

resource "aws_dynamodb_table" "users" {
  name         = "alex-users-data"
  billing_mode = "PAY_PER_REQUEST"

  hash_key  = "PK"
  range_key = "SK"

  attribute {
    name = "PK"
    type = "S"
  }

  attribute {
    name = "SK"
    type = "S"
  }

  attribute {
    name = "GSI1PK"
    type = "S"
  }

  attribute {
    name = "GSI1SK"
    type = "S"
  }

  # GSI for job status queries
  global_secondary_index {
    name            = "GSI1"
    hash_key        = "GSI1PK"
    range_key       = "GSI1SK"
    projection_type = "ALL"
  }

  # Enable point-in-time recovery (optional, adds cost)
  point_in_time_recovery {
    enabled = var.enable_point_in_time_recovery
  }

  # Enable encryption at rest
  server_side_encryption {
    enabled = true
  }

  tags = {
    Project = "alex"
    Part    = "5"
    Purpose = "User accounts and positions with history and jobs"
  }
}

# ========================================
# Table 2: Instruments (reference data + price history)
# ========================================

resource "aws_dynamodb_table" "instruments" {
  name         = "alex-instruments"
  billing_mode = "PAY_PER_REQUEST"

  hash_key  = "symbol"
  range_key = "SK"

  attribute {
    name = "symbol"
    type = "S"
  }

  attribute {
    name = "SK"
    type = "S"
  }

  # Optional: TTL for automatic cleanup of old price history
  ttl {
    attribute_name = "expiry_time"
    enabled        = var.enable_ttl
  }

  # Enable encryption at rest
  server_side_encryption {
    enabled = true
  }

  tags = {
    Project = "alex"
    Part    = "5"
    Purpose = "Instrument metadata and price history"
  }
}

# ========================================
# IAM Role for Lambda Functions
# ========================================

resource "aws_iam_role" "lambda_dynamodb_role" {
  name = "alex-lambda-dynamodb-role"

  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Action = "sts:AssumeRole"
        Effect = "Allow"
        Principal = {
          Service = "lambda.amazonaws.com"
        }
      }
    ]
  })

  tags = {
    Project = "alex"
    Part    = "5"
  }
}

# IAM policy for DynamoDB access
resource "aws_iam_role_policy" "lambda_dynamodb_policy" {
  name = "alex-lambda-dynamodb-policy"
  role = aws_iam_role.lambda_dynamodb_role.id

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect = "Allow"
        Action = [
          "dynamodb:GetItem",
          "dynamodb:PutItem",
          "dynamodb:UpdateItem",
          "dynamodb:DeleteItem",
          "dynamodb:Query",
          "dynamodb:Scan",
          "dynamodb:BatchGetItem",
          "dynamodb:BatchWriteItem"
        ]
        Resource = [
          aws_dynamodb_table.users.arn,
          aws_dynamodb_table.instruments.arn,
          "${aws_dynamodb_table.users.arn}/index/*",
        ]
      },
      {
        Effect = "Allow"
        Action = [
          "logs:CreateLogGroup",
          "logs:CreateLogStream",
          "logs:PutLogEvents"
        ]
        Resource = "arn:aws:logs:${var.aws_region}:${data.aws_caller_identity.current.account_id}:*"
      }
    ]
  })
}

# Attach basic Lambda execution role
resource "aws_iam_role_policy_attachment" "lambda_dynamodb_basic" {
  role       = aws_iam_role.lambda_dynamodb_role.name
  policy_arn = "arn:aws:iam::aws:policy/service-role/AWSLambdaBasicExecutionRole"
}
