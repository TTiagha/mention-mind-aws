import logging
import os
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional, Tuple, Union

import boto3
from boto3.dynamodb.conditions import Key

logger = logging.getLogger(__name__)


class MentionDatabase:
    def __init__(self, table_name: str = os.environ.get("DYNAMODB_TABLE", "mentions")) -> None:
        self.dynamodb = boto3.resource("dynamodb")
        self.table_name = table_name
        self.table = self.dynamodb.Table(table_name)

    def create_table(self) -> None:
        """
        Creates the DynamoDB table for mentions if it doesn't exist.
        """
        try:
            table = self.dynamodb.create_table(
                TableName=self.table_name,
                KeySchema=[
                    {"AttributeName": "mention_id", "KeyType": "HASH"},  # Partition key
                    {"AttributeName": "timestamp", "KeyType": "RANGE"},  # Sort key
                ],
                AttributeDefinitions=[
                    {"AttributeName": "mention_id", "AttributeType": "S"},
                    {"AttributeName": "timestamp", "AttributeType": "N"},
                    {"AttributeName": "source", "AttributeType": "S"},
                ],
                GlobalSecondaryIndexes=[
                    {
                        "IndexName": "source-timestamp-index",
                        "KeySchema": [
                            {"AttributeName": "source", "KeyType": "HASH"},
                            {"AttributeName": "timestamp", "KeyType": "RANGE"},
                        ],
                        "Projection": {"ProjectionType": "ALL"},
                    }
                ],
                BillingMode="PAY_PER_REQUEST",
            )

            # Wait for the table to be created
            table.meta.client.get_waiter("table_exists").wait(TableName=self.table_name)

            # Enable TTL
            table.meta.client.update_time_to_live(
                TableName=self.table_name,
                TimeToLiveSpecification={"Enabled": True, "AttributeName": "ttl"},
            )

            logger.info(f"Table {self.table_name} created successfully")
            return table
        except self.dynamodb.meta.client.exceptions.ResourceInUseException:
            logger.info(f"Table {self.table_name} already exists")
            return self.table

    def store_mention(self, mention: Dict[str, Any]) -> bool:
        """
        Stores a mention in the database.

        Args:
            mention (Dict): Mention data including required fields:
                          mention_id, source, content, timestamp

        Returns:
            bool: True if successful, False otherwise
        """
        try:
            # Add TTL for mentions (30 days from now)
            ttl = int((datetime.now() + timedelta(days=30)).timestamp())

            item = {
                "mention_id": mention["mention_id"],
                "timestamp": int(mention["timestamp"]),
                "source": mention["source"],
                "content": mention["content"],
                "url": mention.get("url", ""),
                "author": mention.get("author", ""),
                "sentiment": mention.get("sentiment", "neutral"),
                "ttl": ttl,
            }

            self.table.put_item(Item=item)
            logger.info(f"Stored mention {mention['mention_id']}")
            return True
        except Exception as e:
            logger.error(f"Error storing mention: {str(e)}")
            return False

    def get_mention(self, mention_id: str, timestamp: int) -> Optional[Dict[str, Any]]:
        """
        Retrieves a specific mention by ID and timestamp.
        """
        try:
            response = self.table.get_item(
                Key={"mention_id": mention_id, "timestamp": timestamp}
            )
            return response.get("Item")
        except Exception as e:
            logger.error(f"Error retrieving mention: {str(e)}")
            return None

    def query_mentions_by_source(
        self,
        source: str,
        start_time: Optional[int] = None,
        end_time: Optional[int] = None,
        limit: int = 100,
    ) -> List[Dict[str, Any]]:
        """
        Queries mentions by source with optional time range.
        """
        try:
            key_condition = Key("source").eq(source)
            if start_time and end_time:
                key_condition &= Key("timestamp").between(start_time, end_time)
            elif start_time:
                key_condition &= Key("timestamp").gte(start_time)
            elif end_time:
                key_condition &= Key("timestamp").lte(end_time)

            response = self.table.query(
                IndexName="source-timestamp-index",
                KeyConditionExpression=key_condition,
                Limit=limit,
            )
            return response.get("Items", [])
        except Exception as e:
            logger.error(f"Error querying mentions: {str(e)}")
            return []

    def batch_store_mentions(
        self, mentions: List[Dict[str, Any]]
    ) -> Tuple[List[Dict[str, Any]], List[Dict[str, Any]]]:
        """
        Stores multiple mentions in batch.

        Returns:
            tuple: (successful_items, failed_items)
        """
        try:
            successful_items = []
            failed_items = []

            # Process in batches of 25 (DynamoDB limit)
            batch_size = 25
            for i in range(0, len(mentions), batch_size):
                batch = mentions[i : i + batch_size]

                # Prepare batch request
                with self.table.batch_writer() as writer:
                    for mention in batch:
                        try:
                            ttl = int((datetime.now() + timedelta(days=30)).timestamp())
                            item = {
                                "mention_id": mention["mention_id"],
                                "timestamp": int(mention["timestamp"]),
                                "source": mention["source"],
                                "content": mention["content"],
                                "url": mention.get("url", ""),
                                "author": mention.get("author", ""),
                                "sentiment": mention.get("sentiment", "neutral"),
                                "ttl": ttl,
                            }
                            writer.put_item(Item=item)
                            successful_items.append(mention)
                        except Exception as e:
                            logger.error(f"Error in batch write: {str(e)}")
                            failed_items.append(mention)

            return successful_items, failed_items
        except Exception as e:
            logger.error(f"Error in batch store operation: {str(e)}")
            return [], mentions

    def delete_mention(self, mention_id: str, timestamp: int) -> bool:
        """
        Deletes a specific mention from the database.
        """
        try:
            self.table.delete_item(
                Key={"mention_id": mention_id, "timestamp": timestamp}
            )
            logger.info(f"Deleted mention {mention_id}")
            return True
        except Exception as e:
            logger.error(f"Error deleting mention: {str(e)}")
            return False
