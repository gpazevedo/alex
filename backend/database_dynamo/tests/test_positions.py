#!/usr/bin/env python3
"""
Test enhanced position tracking with history
"""

import pytest
from datetime import datetime, timedelta
from decimal import Decimal


def test_position_history_tracking():
    """
    Test that position changes are tracked with history
    ENHANCED POSITION TRACKING: Each change creates timestamped record + CURRENT pointer
    """
    from src.models import Database

    db = Database()
    account_id = f'test_account_{datetime.utcnow().strftime("%Y%m%d%H%M%S")}'

    # Day 1: Buy 50 shares of SPY
    db.positions.add_or_update_position(
        account_id, 'SPY', Decimal('50'), action='BUY'
    )

    # Day 2: Buy 25 more shares (total 75)
    db.positions.add_or_update_position(
        account_id, 'SPY', Decimal('75'), action='BUY'
    )

    # Day 3: Sell 25 shares (total 50)
    db.positions.add_or_update_position(
        account_id, 'SPY', Decimal('50'), action='SELL'
    )

    # Get current position (should use CURRENT pointer)
    current_positions = db.positions.find_by_account(account_id)
    assert len(current_positions) == 1
    assert current_positions[0]['quantity'] == Decimal('50')
    assert current_positions[0]['symbol'] == 'SPY'

    # Get position history (should show all 3 changes)
    history = db.positions.get_position_history(account_id, 'SPY')
    assert len(history) >= 3  # At least 3 records

    # Verify actions are tracked
    actions = [h.get('action') for h in history]
    assert 'BUY' in actions
    assert 'SELL' in actions

    print(f"✅ Position history tracking test passed")


def test_positions_at_historical_date():
    """
    Test retrieving positions as they were on a specific date
    ENHANCED: Time-travel to see portfolio at any point in history
    """
    from src.models import Database

    db = Database()
    account_id = f'test_account_{datetime.utcnow().strftime("%Y%m%d%H%M%S")}_hist'

    # Timeline:
    # Now: Buy 100 SPY
    now = datetime.utcnow()
    db.positions.add_or_update_position(account_id, 'SPY', Decimal('100'), action='BUY')

    # Future query: What do I own now?
    future = now + timedelta(seconds=5)
    positions_now = db.positions.get_positions_at_date(account_id, future)

    assert len(positions_now) >= 1
    spy_position = [p for p in positions_now if p['symbol'] == 'SPY'][0]
    assert spy_position['quantity'] == Decimal('100')

    print(f"✅ Historical position query test passed")


def test_portfolio_value_calculation():
    """
    Test calculating portfolio value with current prices
    Uses enhanced position tracking + price history
    """
    from src.models import Database

    db = Database()
    account_id = f'test_account_{datetime.utcnow().strftime("%Y%m%d%H%M%S")}_value'

    # Add position
    db.positions.add_or_update_position(account_id, 'SPY', Decimal('10'), action='BUY')

    # Calculate value
    value = db.positions.get_account_value_at_date(account_id, datetime.utcnow())

    assert value['num_positions'] == 1
    assert value['total_value'] > 0  # Should have calculated value from SPY price

    print(f"✅ Portfolio value calculation test passed")
    print(f"   Total value: ${value['total_value']:.2f}")


def test_current_pointer_performance():
    """
    Test that CURRENT pointer provides O(1) access to latest position
    """
    from src.models import Database

    db = Database()
    account_id = f'test_account_{datetime.utcnow().strftime("%Y%m%d%H%M%S")}_perf'

    # Add many historical records
    for i in range(10):
        db.positions.add_or_update_position(
            account_id, 'SPY', Decimal(str(50 + i * 10)), action='UPDATE'
        )

    # Get current position (should be fast via CURRENT pointer)
    import time
    start = time.time()
    current_positions = db.positions.find_by_account(account_id)
    elapsed = time.time() - start

    assert len(current_positions) == 1
    assert current_positions[0]['quantity'] == Decimal('140')  # Last update
    assert elapsed < 1.0  # Should be fast (< 1 second even with network latency)

    print(f"✅ CURRENT pointer performance test passed ({elapsed*1000:.2f}ms)")


if __name__ == "__main__":
    print("Running enhanced position tracking tests...\n")

    test_position_history_tracking()
    test_positions_at_historical_date()
    test_portfolio_value_calculation()
    test_current_pointer_performance()

    print("\n🎉 All position tracking tests passed!")
