output "users_table_name" {
  description = "Name of the users data table"
  value       = aws_dynamodb_table.users.name
}

output "users_table_arn" {
  description = "ARN of the users data table"
  value       = aws_dynamodb_table.users.arn
}

output "instruments_table_name" {
  description = "Name of the instruments table"
  value       = aws_dynamodb_table.instruments.name
}

output "instruments_table_arn" {
  description = "ARN of the instruments table"
  value       = aws_dynamodb_table.instruments.arn
}

output "lambda_role_arn" {
  description = "ARN of the Lambda execution role"
  value       = aws_iam_role.lambda_dynamodb_role.arn
}

output "region" {
  description = "AWS region where resources are deployed"
  value       = var.aws_region
}

# Instructions for next steps
output "next_steps" {
  description = "Next steps after deploying DynamoDB"
  value = <<-EOT

    ✅ DynamoDB tables deployed successfully!

    📝 Add these to your .env file:

    DYNAMODB_USERS_TABLE=${aws_dynamodb_table.users.name}
    DYNAMODB_INSTRUMENTS_TABLE=${aws_dynamodb_table.instruments.name}
    DEFAULT_AWS_REGION=${var.aws_region}

    🚀 Next steps:

    1. Update .env file with the values above
    2. Seed the database:
       cd ../../backend/database_dynamo
       uv run seed_data.py

    3. Verify the setup:
       uv run verify_database.py

    4. Continue to Guide 6 (Agent migration)

  EOT
}
