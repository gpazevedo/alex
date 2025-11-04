"""
DynamoDB Client Wrapper
Provides a simple interface for database operations
"""

import boto3
import os
from typing import Optional
import logging

logger = logging.getLogger(__name__)

# Try to load .env file if it exists
try:
    from dotenv import load_dotenv
    load_dotenv(override=True)
except ImportError:
    pass


class DynamoDBClient:
    """Wrapper for DynamoDB to simplify database operations"""

    def __init__(self, region: str = None):
        """
        Initialize DynamoDB client

        Args:
            region: AWS region (or from env DEFAULT_AWS_REGION)
        """
        self.region = region or os.environ.get("DEFAULT_AWS_REGION", "us-east-1")

        # Get table names from environment
        users_table_name = os.environ.get("DYNAMODB_USERS_TABLE", "alex-users-data")
        instruments_table_name = os.environ.get("DYNAMODB_INSTRUMENTS_TABLE", "alex-instruments")

        # Support for local DynamoDB (testing)
        endpoint_url = os.environ.get('DYNAMODB_ENDPOINT')

        if endpoint_url:
            self.dynamodb = boto3.resource(
                'dynamodb',
                region_name=self.region,
                endpoint_url=endpoint_url
            )
        else:
            self.dynamodb = boto3.resource('dynamodb', region_name=self.region)

        # Initialize table connections
        self.users_table = self.dynamodb.Table(users_table_name)
        self.instruments_table = self.dynamodb.Table(instruments_table_name)

        logger.info(f"DynamoDB client initialized: {users_table_name}, {instruments_table_name}")
