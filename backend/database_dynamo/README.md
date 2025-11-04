# Alex Database - DynamoDB Implementation

DynamoDB-based database package for Alex Financial Planner with enhanced position tracking.

## Features

- **Two-table design** - Optimized for access patterns
- **Enhanced position tracking** - Complete history with CURRENT pointer
- **Price history** - Integrated into instruments table
- **Time-travel queries** - Calculate portfolio value at any historical date
- **API compatible** - Drop-in replacement for Aurora version

## Tables

### alex-users-data
User-specific data with single-table design:
- Users (PK: USER#<id>, SK: METADATA)
- Accounts (PK: USER#<id>, SK: ACCOUNT#<uuid>)
- Current positions (PK: ACCOUNT#<uuid>, SK: CURRENT#<symbol>)
- Position history (PK: ACCOUNT#<uuid>, SK: HISTORY#<symbol>#<timestamp>)
- Jobs (PK: USER#<id>, SK: JOB#<timestamp>#<uuid>)

### alex-instruments
Instrument reference data with price history:
- Metadata (PK: <symbol>, SK: META)
- Price history (PK: <symbol>, SK: <ISO8601 timestamp>)

## Enhanced Position Tracking

**Optimized SK Pattern** for efficient queries:

Every position change creates two records:

1. **Historical record**: `HISTORY#SPY#2025-01-15T14:30:00Z`
   - Stores quantity, action (BUY/SELL/TRANSFER), timestamp
   - Enables complete audit trail
   - Grouped by HISTORY# prefix for efficient historical queries

2. **CURRENT record**: `CURRENT#SPY`
   - Fast access to latest positions (no historical data retrieved)
   - Grouped by CURRENT# prefix for optimized queries
   - Overwritten with each update

Benefits:
- ✅ **Optimized queries** - Current positions don't retrieve historical data
- ✅ **Reduced read capacity** - Only reads what's needed for current positions
- ✅ **True portfolio evolution** - Actual position changes over time
- ✅ **Complete audit trail** - Regulatory compliance, tax reporting
- ✅ **Time-travel queries** - Calculate portfolio value at any historical date
- ✅ **Fast current lookups** - SK begins_with CURRENT# returns only current positions

## Usage

```python
from src import Database

db = Database()

# Create user
db.users.create_user("user_123", "John Doe")

# Add position with history tracking
db.positions.add_or_update_position(
    account_id="acc_001",
    symbol="SPY",
    quantity=100,
    action="BUY"
)

# Get current positions (fast)
positions = db.positions.find_by_account("acc_001")

# Get position history
history = db.positions.get_position_history("acc_001", "SPY")

# Calculate portfolio value at any date
value = db.positions.get_account_value_at_date(
    "acc_001",
    datetime(2025, 1, 15)
)
```

## Setup

1. Deploy DynamoDB tables:
```bash
cd terraform/5_database_dynamo
terraform init
terraform apply
```

2. Set environment variables:
```bash
export DYNAMODB_USERS_TABLE=alex-users-data
export DYNAMODB_INSTRUMENTS_TABLE=alex-instruments
```

3. Seed data:
```bash
cd backend/database_dynamo
uv run seed_data.py
```

4. Verify:
```bash
uv run verify_database.py
```

## Testing

```bash
# Unit tests (with moto mocks)
uv run pytest tests/

# Integration tests (requires AWS)
uv run tests/test_positions.py
```

## Cost

Estimated monthly cost:
- Price updates: 100 instruments × 26 updates/day × 20 days = ~$0.13/month
- Position changes: Minimal
- Storage: ~65MB/year = ~$0.016/month
- **Total: ~$5-15/month** (vs ~$43+/month for Aurora)
