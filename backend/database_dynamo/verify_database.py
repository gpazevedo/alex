#!/usr/bin/env python3
"""
Verify DynamoDB database integrity
Tests against actual AWS DynamoDB tables
"""

from src import Database
from dotenv import load_dotenv
from datetime import datetime
from decimal import Decimal

load_dotenv()


def verify_tables_exist():
    """Verify all required tables exist"""
    print("📋 Checking tables...")
    db = Database()

    try:
        # Check users table
        response = db.client.users_table.table_status
        print(f"  ✅ Users table: {response}")
    except Exception as e:
        print(f"  ❌ Users table error: {e}")
        return False

    try:
        # Check instruments table
        response = db.client.instruments_table.table_status
        print(f"  ✅ Instruments table: {response}")
    except Exception as e:
        print(f"  ❌ Instruments table error: {e}")
        return False

    return True


def verify_seed_data():
    """Verify seed data was loaded"""
    print("\n📊 Checking seed data...")
    db = Database()

    # Check for instruments
    instruments = db.instruments.find_all()
    print(f"  ✅ Found {len(instruments)} instruments")

    if len(instruments) < 22:
        print(f"  ⚠️  Expected at least 22 instruments, found {len(instruments)}")
        return False

    # Check SPY specifically
    spy = db.instruments.find_by_symbol('SPY')
    if not spy:
        print("  ❌ SPY not found in instruments")
        return False

    print(f"  ✅ SPY found: ${spy['current_price']}")

    return True


def verify_operations():
    """Verify CRUD operations work"""
    print("\n🔧 Testing operations...")
    db = Database()

    # Test user creation
    test_user_id = f"test_verify_{datetime.utcnow().strftime('%Y%m%d%H%M%S')}"

    try:
        # Create user
        user_id = db.users.create_user(
            clerk_user_id=test_user_id,
            display_name='Verification Test User'
        )
        print(f"  ✅ Created test user: {user_id}")

        # Retrieve user
        user = db.users.find_by_clerk_id(test_user_id)
        if user:
            print(f"  ✅ Retrieved test user")
        else:
            print(f"  ❌ Could not retrieve test user")
            return False

        # Create account
        account_id = db.accounts.create_account(
            clerk_user_id=test_user_id,
            account_name="Test Account",
            cash_balance=Decimal('1000')
        )
        print(f"  ✅ Created test account: {account_id}")

        # Add position
        db.positions.add_or_update_position(
            account_id,
            'SPY',
            Decimal('10'),
            action='BUY'
        )
        print(f"  ✅ Added test position")

        # Get positions
        positions = db.positions.find_by_account(account_id)
        if len(positions) == 1 and positions[0]['symbol'] == 'SPY':
            print(f"  ✅ Retrieved test position")
        else:
            print(f"  ❌ Position retrieval failed")
            return False

        # Test position history
        history = db.positions.get_position_history(account_id, 'SPY')
        if len(history) >= 1:
            print(f"  ✅ Position history works ({len(history)} records)")
        else:
            print(f"  ❌ Position history failed")
            return False

        print(f"  ✅ All operations successful")

    except Exception as e:
        print(f"  ❌ Operation test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

    return True


if __name__ == "__main__":
    print("=" * 60)
    print("DynamoDB Database Verification")
    print("=" * 60)

    if not verify_tables_exist():
        exit(1)

    if not verify_seed_data():
        exit(1)

    if not verify_operations():
        exit(1)

    print("\n" + "=" * 60)
    print("🎉 DATABASE VERIFICATION COMPLETE")
    print("=" * 60)
    print("✅ All tables exist")
    print("✅ Seed data loaded")
    print("✅ CRUD operations working")
    print("✅ Enhanced position tracking works")
    print("✅ Database is ready for agents!")
