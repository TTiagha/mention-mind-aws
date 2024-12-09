import os
from datetime import datetime

import boto3
import pytest
from moto import mock_dynamodb

from database import MentionDatabase


@pytest.fixture
def dynamodb_table():
    with mock_dynamodb():
        # Create mock DynamoDB resource
        db = MentionDatabase(table_name="test_mentions")
        db.create_table()
        yield db


def test_store_and_retrieve_mention(dynamodb_table):
    # Test data
    mention = {
        "mention_id": "test_id_1",
        "timestamp": int(datetime.now().timestamp()),
        "source": "reddit",
        "content": "Test mention content",
        "url": "https://reddit.com/test",
        "author": "test_user",
        "sentiment": "positive",
    }

    # Store mention
    assert dynamodb_table.store_mention(mention) == True

    # Retrieve mention
    retrieved = dynamodb_table.get_mention(mention["mention_id"], mention["timestamp"])
    assert retrieved is not None
    assert retrieved["mention_id"] == mention["mention_id"]
    assert retrieved["content"] == mention["content"]


def test_batch_store_mentions(dynamodb_table):
    # Create test mentions
    mentions = [
        {
            "mention_id": f"batch_id_{i}",
            "timestamp": int(datetime.now().timestamp()),
            "source": "twitter",
            "content": f"Test content {i}",
            "url": f"https://twitter.com/test/{i}",
            "author": f"user_{i}",
            "sentiment": "neutral",
        }
        for i in range(30)  # Create 30 test mentions to test batch processing
    ]

    # Store mentions in batch
    successful, failed = dynamodb_table.batch_store_mentions(mentions)
    assert len(successful) == 30
    assert len(failed) == 0


def test_query_mentions_by_source(dynamodb_table):
    # Store some test mentions with different sources
    current_time = int(datetime.now().timestamp())
    mentions = [
        {
            "mention_id": f"query_id_{i}",
            "timestamp": current_time,
            "source": "reddit" if i % 2 == 0 else "twitter",
            "content": f"Test content {i}",
            "url": f"https://example.com/{i}",
            "author": f"user_{i}",
            "sentiment": "neutral",
        }
        for i in range(10)
    ]

    # Store all mentions
    for mention in mentions:
        dynamodb_table.store_mention(mention)

    # Query reddit mentions
    reddit_mentions = dynamodb_table.query_mentions_by_source("reddit")
    assert len(reddit_mentions) == 5  # Should get 5 reddit mentions


def test_delete_mention(dynamodb_table):
    # Store a mention
    mention = {
        "mention_id": "delete_test_id",
        "timestamp": int(datetime.now().timestamp()),
        "source": "reddit",
        "content": "Content to delete",
        "url": "https://reddit.com/delete_test",
        "author": "test_user",
        "sentiment": "neutral",
    }

    dynamodb_table.store_mention(mention)

    # Delete the mention
    assert (
        dynamodb_table.delete_mention(mention["mention_id"], mention["timestamp"])
        == True
    )

    # Try to retrieve it - should return None
    retrieved = dynamodb_table.get_mention(mention["mention_id"], mention["timestamp"])
    assert retrieved is None
