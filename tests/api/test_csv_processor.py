"""
Test CSV processing functionality
"""

import os

import pytest

from src.api.csv_processor import CSVProcessor


@pytest.fixture
def processor() -> CSVProcessor:
    return CSVProcessor()


def test_process_reddit_csv(processor: CSVProcessor) -> None:
    """Test processing Reddit CSV file"""
    csv_path = os.path.join("tests", "MentionMind-Twitter - Reddit.csv")
    mentions = processor.process_reddit_csv(csv_path)

    assert len(mentions) > 0

    # Check first mention has required fields
    mention = mentions[0]
    assert mention["source"] == "reddit"
    assert mention["url"].startswith("https://")
    assert mention["author"]
    assert mention["date"]
    assert mention["status"]

    # Check enriched fields
    assert "hashtags" in mention
    assert "mentioned_users" in mention
    assert "search_text" in mention
    assert "processed_at" in mention
    assert mention["language"] == "unknown"
    assert mention["sentiment"] == "neutral"


def test_process_twitter_csv(processor: CSVProcessor) -> None:
    """Test processing Twitter CSV file"""
    csv_path = os.path.join("tests", "MentionMind-Twitter - Twitter.csv")
    mentions = processor.process_twitter_csv(csv_path)

    assert len(mentions) > 0

    # Check first mention has required fields
    mention = mentions[0]
    assert mention["source"] == "twitter"
    assert mention["url"].startswith("https://")
    assert mention["author"]
    assert mention["date"]
    assert mention["status"]

    # Check enriched fields
    assert "hashtags" in mention
    assert "mentioned_users" in mention
    assert "search_text" in mention
    assert "processed_at" in mention
    assert mention["language"] == "unknown"
    assert mention["sentiment"] == "neutral"
