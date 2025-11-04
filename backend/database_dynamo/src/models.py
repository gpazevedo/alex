"""
Database models and query builders for DynamoDB
Implements two-table design with enhanced position tracking
"""

from typing import Dict, List, Optional, Any
from datetime import datetime, date
from decimal import Decimal
from .client import DynamoDBClient
from .schemas import InstrumentCreate, UserCreate, AccountCreate, PositionCreate, JobCreate, JobUpdate
import logging

logger = logging.getLogger(__name__)


class Users:
    """Users table operations"""

    def __init__(self, table):
        self.table = table

    def find_by_clerk_id(self, clerk_user_id: str) -> Optional[Dict]:
        """Find user by Clerk ID"""
        response = self.table.get_item(
            Key={'PK': f'USER#{clerk_user_id}', 'SK': 'METADATA'}
        )
        return response.get('Item')

    def create_user(self, clerk_user_id: str, display_name: str = None,
                   years_until_retirement: int = None,
                   target_retirement_income: Decimal = None,
                   asset_class_targets: Dict = None,
                   region_targets: Dict = None) -> str:
        """Create a new user"""
        item = {
            'PK': f'USER#{clerk_user_id}',
            'SK': 'METADATA',
            'clerk_user_id': clerk_user_id,
            'created_at': datetime.utcnow().isoformat(),
            'updated_at': datetime.utcnow().isoformat()
        }

        if display_name:
            item['display_name'] = display_name
        if years_until_retirement is not None:
            item['years_until_retirement'] = years_until_retirement
        if target_retirement_income is not None:
            item['target_retirement_income'] = target_retirement_income
        if asset_class_targets:
            item['asset_class_targets'] = asset_class_targets
        if region_targets:
            item['region_targets'] = region_targets

        self.table.put_item(Item=item)
        return clerk_user_id

    def update(self, clerk_user_id: str, data: Dict) -> int:
        """Update user data"""
        job = self.find_by_clerk_id(clerk_user_id)
        if not job:
            return 0

        # Build update expression
        update_parts = []
        expr_values = {}
        for key, value in data.items():
            update_parts.append(f"{key} = :{key}")
            expr_values[f':{key}'] = value

        update_parts.append("updated_at = :updated_at")
        expr_values[':updated_at'] = datetime.utcnow().isoformat()

        self.table.update_item(
            Key={'PK': f'USER#{clerk_user_id}', 'SK': 'METADATA'},
            UpdateExpression=f"SET {', '.join(update_parts)}",
            ExpressionAttributeValues=expr_values
        )
        return 1


class Instruments:
    """Instruments table operations"""

    def __init__(self, table):
        self.table = table

    def find_by_symbol(self, symbol: str) -> Optional[Dict]:
        """Find instrument metadata by symbol"""
        response = self.table.get_item(
            Key={'symbol': symbol, 'SK': 'META'}
        )
        return response.get('Item')

    def find_all(self) -> List[Dict]:
        """Find all instruments (metadata only)"""
        response = self.table.scan(
            FilterExpression='SK = :meta',
            ExpressionAttributeValues={':meta': 'META'}
        )
        return response.get('Items', [])

    def batch_get_by_symbols(self, symbols: List[str]) -> Dict[str, Dict]:
        """Get metadata for multiple instruments efficiently"""
        if not symbols:
            return {}

        # Build keys for batch get
        keys = [{'symbol': sym, 'SK': 'META'} for sym in symbols]

        # Batch get (max 100 per request)
        results = {}
        for i in range(0, len(keys), 100):
            batch = keys[i:i+100]
            response = self.table.meta.client.batch_get_item(
                RequestItems={
                    self.table.name: {'Keys': batch}
                }
            )

            for item in response.get('Responses', {}).get(self.table.name, []):
                results[item['symbol']] = item

        return results

    def create_instrument(self, instrument: InstrumentCreate) -> str:
        """Create a new instrument with validation"""
        # Convert all numeric values to Decimal for DynamoDB
        def convert_to_decimal(d: dict) -> dict:
            """Convert all numeric values in a dict to Decimal"""
            return {k: Decimal(str(v)) if isinstance(v, (int, float)) else v for k, v in d.items()}

        item = {
            'symbol': instrument.symbol,
            'SK': 'META',
            'name': instrument.name,
            'instrument_type': instrument.instrument_type,
            'current_price': instrument.current_price,
            'allocation_regions': convert_to_decimal(instrument.allocation_regions),
            'allocation_sectors': convert_to_decimal(instrument.allocation_sectors),
            'allocation_asset_class': convert_to_decimal(instrument.allocation_asset_class),
            'created_at': datetime.utcnow().isoformat(),
            'updated_at': datetime.utcnow().isoformat()
        }

        self.table.put_item(Item=item)
        return instrument.symbol

    def update_price(self, symbol: str, new_price: Decimal, volume: int = None):
        """
        Update current price and append to history
        Two writes: 1) Update META, 2) Append history record
        """
        timestamp = datetime.utcnow().isoformat()

        # 1. Update current price in META
        self.table.update_item(
            Key={'symbol': symbol, 'SK': 'META'},
            UpdateExpression='SET current_price = :price, updated_at = :ts',
            ExpressionAttributeValues={
                ':price': new_price,
                ':ts': timestamp
            }
        )

        # 2. Append to price history
        item = {
            'symbol': symbol,
            'SK': timestamp,
            'price': new_price,
            'source': 'update'
        }
        if volume:
            item['volume'] = volume

        self.table.put_item(Item=item)

    def get_price_history(self, symbol: str, start_date: datetime,
                         end_date: datetime) -> List[Dict]:
        """Get price history for an instrument"""
        response = self.table.query(
            KeyConditionExpression='symbol = :symbol AND SK BETWEEN :start AND :end',
            ExpressionAttributeValues={
                ':symbol': symbol,
                ':start': start_date.isoformat(),
                ':end': end_date.isoformat()
            }
        )
        return response.get('Items', [])

    def get_price_at_date(self, symbol: str, target_date: datetime) -> Optional[Dict]:
        """Get the most recent price at or before a specific date"""
        response = self.table.query(
            KeyConditionExpression='symbol = :symbol AND SK <= :date',
            FilterExpression='SK <> :meta',  # Exclude META record
            ExpressionAttributeValues={
                ':symbol': symbol,
                ':date': target_date.isoformat(),
                ':meta': 'META'
            },
            ScanIndexForward=False,  # Descending order
            Limit=1
        )
        items = response.get('Items', [])
        return items[0] if items else None


class Accounts:
    """Accounts table operations"""

    def __init__(self, table):
        self.table = table

    def find_by_user(self, clerk_user_id: str) -> List[Dict]:
        """Find all accounts for a user"""
        response = self.table.query(
            KeyConditionExpression='PK = :pk AND begins_with(SK, :sk)',
            ExpressionAttributeValues={
                ':pk': f'USER#{clerk_user_id}',
                ':sk': 'ACCOUNT#'
            }
        )
        return response.get('Items', [])

    def find_by_id(self, account_id: str) -> Optional[Dict]:
        """Find account by ID"""
        # Query using account as PK to find the account record
        response = self.table.query(
            KeyConditionExpression='PK = :pk',
            ExpressionAttributeValues={
                ':pk': f'ACCOUNT#{account_id}'
            },
            Limit=1
        )
        items = response.get('Items', [])
        if items:
            return items[0]

        # If not found, scan for the account (less efficient but works)
        response = self.table.scan(
            FilterExpression='begins_with(SK, :sk) AND id = :id',
            ExpressionAttributeValues={
                ':sk': 'ACCOUNT#',
                ':id': account_id
            },
            Limit=1
        )
        items = response.get('Items', [])
        return items[0] if items else None

    def create_account(self, clerk_user_id: str, account_name: str,
                      account_purpose: str = None, cash_balance: Decimal = Decimal('0'),
                      cash_interest: Decimal = Decimal('0')) -> str:
        """Create a new account"""
        import uuid
        account_id = str(uuid.uuid4())

        item = {
            'PK': f'USER#{clerk_user_id}',
            'SK': f'ACCOUNT#{account_id}',
            'id': account_id,
            'clerk_user_id': clerk_user_id,
            'account_name': account_name,
            'account_purpose': account_purpose,
            'cash_balance': cash_balance,
            'cash_interest': cash_interest,
            'created_at': datetime.utcnow().isoformat(),
            'updated_at': datetime.utcnow().isoformat()
        }

        self.table.put_item(Item=item)
        return account_id


class Positions:
    """
    Positions table operations with ENHANCED HISTORY TRACKING

    Optimized SK pattern for efficient queries:
    - CURRENT#<symbol> → Fast access to current positions (no historical data retrieved)
    - HISTORY#<symbol>#<timestamp> → Historical records

    This pattern ensures:
    - Current position queries only read what's needed (no filtering of historical data)
    - Historical queries still efficient with begins_with
    - Significantly reduced read capacity for common operations
    """

    def __init__(self, users_table, instruments_table):
        self.table = users_table
        self.instruments_table = instruments_table

    def find_by_account(self, account_id: str) -> List[Dict]:
        """
        Get current positions for an account (optimized query - no historical data retrieved)

        Query pattern: PK = ACCOUNT#<id>, SK begins_with CURRENT#
        Only retrieves current positions, ignoring all historical records
        """
        response = self.table.query(
            KeyConditionExpression='PK = :pk AND begins_with(SK, :sk)',
            ExpressionAttributeValues={
                ':pk': f'ACCOUNT#{account_id}',
                ':sk': 'CURRENT#'
            }
        )

        # Parse results - SK format: CURRENT#SPY
        positions = []
        for item in response.get('Items', []):
            parts = item['SK'].split('#')
            if len(parts) >= 2:  # Should be ['CURRENT', 'SPY']
                symbol = parts[1]
                positions.append({
                    'symbol': symbol,
                    'quantity': item['quantity'],
                    'timestamp': item.get('timestamp'),
                    'account_id': account_id,
                    'as_of_date': item.get('as_of_date', date.today().isoformat())
                })

        return positions

    def add_or_update_position(self, account_id: str, symbol: str,
                               quantity: Decimal, action: str = "UPDATE"):
        """
        ENHANCED: Add or update a position with full history tracking

        Creates two records with optimized SK pattern:
        1. Historical record: HISTORY#<symbol>#<timestamp>
        2. CURRENT record: CURRENT#<symbol>

        The CURRENT record is overwritten with each update, maintaining only the latest state.
        """
        timestamp = datetime.utcnow().isoformat()

        # 1. Write historical record
        self.table.put_item(
            Item={
                'PK': f'ACCOUNT#{account_id}',
                'SK': f'HISTORY#{symbol}#{timestamp}',
                'quantity': quantity,
                'action': action,
                'timestamp': timestamp,
                'as_of_date': date.today().isoformat()
            }
        )

        # 2. Update CURRENT record (overwrites previous)
        self.table.put_item(
            Item={
                'PK': f'ACCOUNT#{account_id}',
                'SK': f'CURRENT#{symbol}',
                'quantity': quantity,
                'timestamp': timestamp,
                'as_of_date': date.today().isoformat()
            }
        )

        logger.info(f"Position updated: {account_id}/{symbol} -> {quantity} ({action})")

    def get_positions_at_date(self, account_id: str, target_date: datetime) -> List[Dict]:
        """
        ENHANCED: Get positions as they were at a specific date
        Returns the most recent position before target_date for each symbol

        Query pattern: PK = ACCOUNT#<id>, SK BETWEEN HISTORY# and HISTORY#~<date>
        """
        # Query all historical records up to target date
        response = self.table.query(
            KeyConditionExpression='PK = :pk AND SK BETWEEN :start AND :end',
            ExpressionAttributeValues={
                ':pk': f'ACCOUNT#{account_id}',
                ':start': 'HISTORY#',
                ':end': f'HISTORY#~{target_date.isoformat()}'
            }
        )

        # Group by symbol and keep most recent before target_date
        positions_by_symbol = {}
        for item in response.get('Items', []):
            # Parse SK: HISTORY#SPY#2025-01-15T14:30:00Z
            parts = item['SK'].split('#')
            if len(parts) < 3:
                continue

            symbol = parts[1]
            timestamp = parts[2]

            # Keep most recent position for each symbol
            if symbol not in positions_by_symbol:
                positions_by_symbol[symbol] = {
                    'symbol': symbol,
                    'quantity': item['quantity'],
                    'timestamp': timestamp,
                    'action': item.get('action')
                }
            elif timestamp > positions_by_symbol[symbol]['timestamp']:
                positions_by_symbol[symbol] = {
                    'symbol': symbol,
                    'quantity': item['quantity'],
                    'timestamp': timestamp,
                    'action': item.get('action')
                }

        return list(positions_by_symbol.values())

    def get_position_history(self, account_id: str, symbol: str,
                            start_date: datetime = None,
                            end_date: datetime = None) -> List[Dict]:
        """
        ENHANCED: Get complete change history for a single position
        Useful for auditing and transaction history

        Query pattern: PK = ACCOUNT#<id>, SK BETWEEN HISTORY#<symbol>#<start> and HISTORY#<symbol>#<end>
        """
        if not start_date:
            start_date = datetime(2020, 1, 1)
        if not end_date:
            end_date = datetime.utcnow()

        response = self.table.query(
            KeyConditionExpression='PK = :pk AND SK BETWEEN :start AND :end',
            ExpressionAttributeValues={
                ':pk': f'ACCOUNT#{account_id}',
                ':start': f'HISTORY#{symbol}#{start_date.isoformat()}',
                ':end': f'HISTORY#{symbol}#{end_date.isoformat()}'
            },
            ScanIndexForward=True
        )

        return response.get('Items', [])

    def get_portfolio_value(self, account_id: str) -> Dict:
        """Calculate current portfolio value"""
        return self.get_account_value_at_date(account_id, datetime.utcnow())

    def get_account_value_at_date(self, account_id: str,
                                  target_date: datetime = None) -> Dict:
        """
        ENHANCED: Calculate account value at any historical date
        Uses actual positions at that date + prices at that date
        """
        if target_date is None:
            target_date = datetime.utcnow()

        # 1. Get positions as they were at target_date
        positions = self.get_positions_at_date(account_id, target_date)

        if not positions:
            return {
                'total_value': 0,
                'num_positions': 0,
                'as_of_date': target_date.isoformat()
            }

        # 2. Get instruments for price lookup
        symbols = [pos['symbol'] for pos in positions]
        instruments = Instruments(self.instruments_table)

        # 3. Calculate total value with historical prices
        total_value = Decimal('0')
        for pos in positions:
            symbol = pos['symbol']
            quantity = Decimal(str(pos['quantity']))

            # Get historical price at target_date
            price_record = instruments.get_price_at_date(symbol, target_date)
            if price_record:
                price = Decimal(str(price_record['price']))
                total_value += quantity * price

        return {
            'total_value': float(total_value),
            'num_positions': len(positions),
            'as_of_date': target_date.isoformat(),
            'total_shares': sum(float(p['quantity']) for p in positions)
        }


class Jobs:
    """Jobs table operations"""

    def __init__(self, table):
        self.table = table

    def create_job(self, clerk_user_id: str, job_type: str,
                  request_payload: Dict = None) -> str:
        """Create a new job"""
        import uuid
        job_id = str(uuid.uuid4())
        timestamp = datetime.utcnow().isoformat()

        item = {
            'PK': f'USER#{clerk_user_id}',
            'SK': f'JOB#{timestamp}#{job_id}',
            'id': job_id,
            'clerk_user_id': clerk_user_id,
            'job_type': job_type,
            'status': 'pending',
            'request_payload': request_payload,
            'created_at': timestamp,
            # GSI attributes
            'GSI1PK': f'JOB#pending',
            'GSI1SK': f'USER#{clerk_user_id}#{timestamp}'
        }

        self.table.put_item(Item=item)
        return job_id

    def create(self, job_data: Dict) -> Dict:
        """Create a job from dict (compatible with old API)"""
        job_id = self.create_job(
            clerk_user_id=job_data['clerk_user_id'],
            job_type=job_data['job_type'],
            request_payload=job_data.get('request_payload')
        )
        return {'id': job_id}

    def find_by_id(self, job_id: str) -> Optional[Dict]:
        """Find job by ID"""
        response = self.table.scan(
            FilterExpression='id = :job_id',
            ExpressionAttributeValues={':job_id': job_id},
            Limit=1
        )
        items = response.get('Items', [])
        return items[0] if items else None

    def find_all(self, limit: int = 100) -> List[Dict]:
        """Find all jobs (for testing/admin)"""
        response = self.table.scan(
            FilterExpression='begins_with(SK, :sk)',
            ExpressionAttributeValues={':sk': 'JOB#'},
            Limit=limit
        )
        return response.get('Items', [])

    def update_status(self, job_id: str, status: str, error_message: str = None) -> int:
        """Update job status"""
        job = self.find_by_id(job_id)
        if not job:
            return 0

        update_expr = 'SET #status = :status, updated_at = :ts'
        expr_values = {
            ':status': status,
            ':ts': datetime.utcnow().isoformat()
        }

        if status == 'running':
            update_expr += ', started_at = :ts'
        elif status in ['completed', 'failed']:
            update_expr += ', completed_at = :ts'

        if error_message:
            update_expr += ', error_message = :error'
            expr_values[':error'] = error_message

        # Update GSI1PK for status queries
        update_expr += ', GSI1PK = :gsi1pk'
        expr_values[':gsi1pk'] = f'JOB#{status}'

        self.table.update_item(
            Key={'PK': job['PK'], 'SK': job['SK']},
            UpdateExpression=update_expr,
            ExpressionAttributeNames={'#status': 'status'},
            ExpressionAttributeValues=expr_values
        )
        return 1

    def update_report(self, job_id: str, report_payload: Dict) -> int:
        """Update job with Reporter agent's analysis"""
        job = self.find_by_id(job_id)
        if not job:
            return 0

        self.table.update_item(
            Key={'PK': job['PK'], 'SK': job['SK']},
            UpdateExpression='SET report_payload = :payload',
            ExpressionAttributeValues={':payload': report_payload}
        )
        return 1

    def update_charts(self, job_id: str, charts_payload: Dict) -> int:
        """Update job with Charter agent's visualization data"""
        job = self.find_by_id(job_id)
        if not job:
            return 0

        self.table.update_item(
            Key={'PK': job['PK'], 'SK': job['SK']},
            UpdateExpression='SET charts_payload = :payload',
            ExpressionAttributeValues={':payload': charts_payload}
        )
        return 1

    def update_retirement(self, job_id: str, retirement_payload: Dict) -> int:
        """Update job with Retirement agent's projections"""
        job = self.find_by_id(job_id)
        if not job:
            return 0

        self.table.update_item(
            Key={'PK': job['PK'], 'SK': job['SK']},
            UpdateExpression='SET retirement_payload = :payload',
            ExpressionAttributeValues={':payload': retirement_payload}
        )
        return 1

    def update_summary(self, job_id: str, summary_payload: Dict) -> int:
        """Update job with Planner's final summary"""
        job = self.find_by_id(job_id)
        if not job:
            return 0

        self.table.update_item(
            Key={'PK': job['PK'], 'SK': job['SK']},
            UpdateExpression='SET summary_payload = :payload',
            ExpressionAttributeValues={':payload': summary_payload}
        )
        return 1

    def find_by_user(self, clerk_user_id: str, status: str = None,
                    limit: int = 20) -> List[Dict]:
        """Find jobs for a user"""
        if status:
            # Use GSI to filter by status
            response = self.table.query(
                IndexName='GSI1',
                KeyConditionExpression='GSI1PK = :gsi1pk AND begins_with(GSI1SK, :user)',
                ExpressionAttributeValues={
                    ':gsi1pk': f'JOB#{status}',
                    ':user': f'USER#{clerk_user_id}'
                },
                Limit=limit,
                ScanIndexForward=False
            )
        else:
            # Query by user
            response = self.table.query(
                KeyConditionExpression='PK = :pk AND begins_with(SK, :sk)',
                ExpressionAttributeValues={
                    ':pk': f'USER#{clerk_user_id}',
                    ':sk': 'JOB#'
                },
                Limit=limit,
                ScanIndexForward=False
            )

        return response.get('Items', [])


class Database:
    """Main database interface providing access to all models"""

    def __init__(self, region: str = None):
        """Initialize database with all model classes"""
        self.client = DynamoDBClient(region)

        # Initialize all models
        self.users = Users(self.client.users_table)
        self.instruments = Instruments(self.client.instruments_table)
        self.accounts = Accounts(self.client.users_table)
        self.positions = Positions(self.client.users_table, self.client.instruments_table)
        self.jobs = Jobs(self.client.users_table)
