# Alex Database Infrastructure - DynamoDB

Terraform configuration for DynamoDB-based database infrastructure.

## What This Deploys

- **alex-users-data** - DynamoDB table for user-specific data
  - Users, accounts, positions with history, jobs
  - GSI for job status queries

- **alex-instruments** - DynamoDB table for instrument reference data
  - Instrument metadata and price history
  - Optional TTL for automatic cleanup

- **IAM Role** - Lambda execution role with DynamoDB permissions

## Cost Estimate

**Monthly cost (on-demand pricing):**
- Storage: ~$0.25/GB/month (estimated <1GB = ~$0.25)
- Reads/Writes: $1.25 per million requests
- Estimated total: **$5-15/month** depending on usage

**Savings vs Aurora Serverless v2:** ~85% ($43+/month → $5-15/month)

## Deployment

1. **Configure variables:**
```bash
cp terraform.tfvars.example terraform.tfvars
# Edit terraform.tfvars with your AWS region
```

2. **Deploy:**
```bash
terraform init
terraform apply
```

3. **Save outputs:**
```bash
terraform output
```

4. **Update .env file:**
Copy the values from terraform output to your `.env` file in the project root.

## Table Schemas

### alex-users-data
Single-table design with multiple entity types:

| PK | SK | Purpose |
|---|---|---|
| USER#<clerk_id> | METADATA | User profile |
| USER#<clerk_id> | ACCOUNT#<uuid> | Account |
| USER#<clerk_id> | JOB#<timestamp>#<uuid> | Analysis job |
| ACCOUNT#<uuid> | POSITION#<symbol>#CURRENT | Current position (fast lookup) |
| ACCOUNT#<uuid> | POSITION#<symbol>#<timestamp> | Historical position record |

**GSI1:** Job status index
- GSI1PK: JOB#<status>
- GSI1SK: USER#<clerk_id>#<timestamp>

### alex-instruments
Instrument metadata and price history:

| symbol | SK | Purpose |
|---|---|---|
| SPY | META | Instrument metadata |
| SPY | 2025-01-15T09:30:00Z | Price at 9:30 AM |
| SPY | 2025-01-15T16:00:00Z | Price at 4:00 PM |

## Cleanup

To destroy all resources:
```bash
terraform destroy
```

⚠️ **Warning:** This will delete all data. Ensure you have backups if needed.

## Next Steps

After deploying:
1. Seed the database (see `backend/database_dynamo/README.md`)
2. Update agents to use DynamoDB (`terraform/6_agents/`)
3. Deploy agents and test end-to-end
