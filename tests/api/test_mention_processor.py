"""
Tests for the mention processor
"""

import pytest

from src.api.exceptions import ValidationError
from src.api.mention_processor import MentionProcessor


@pytest.fixture
def processor() -> MentionProcessor:
    """Create a mention processor instance"""
    return MentionProcessor()


@pytest.fixture
def valid_mention():
    """Create a valid mention fixture"""
    return {
        "id": "mention123",
        "text": "Check out this #awesome product! @johndoe",
        "date": "2024-01-01T12:00:00Z",
        "source": "twitter",
        "url": "https://twitter.com/user/status/123",
        "author": "janedoe",
    }


def test_process_mention_success(processor: MentionProcessor, valid_mention) -> None:
    """Test successful mention processing"""
    result = processor.process_mention(valid_mention)

    # Check basic fields are preserved
    assert result["id"] == valid_mention["id"]
    assert result["text"] == valid_mention["text"]
    assert result["source"] == valid_mention["source"]

    # Check enriched fields
    assert result["hashtags"] == ["awesome"]
    assert result["mentioned_users"] == ["johndoe"]
    assert result["mention_type"] == "tweet"

    # Check storage fields
    assert "processed_at" in result
    assert "search_text" in result
    assert result["language"] == "unknown"
    assert result["sentiment"] == "neutral"


def test_process_mentions_multiple(processor: MentionProcessor) -> None:
    """Test processing multiple mentions"""
    mentions = [
        {
            "id": "mention1",
            "text": "First #test mention",
            "date": "2024-01-01T12:00:00Z",
            "source": "twitter",
        },
        {
            "id": "mention2",
            "text": "Second #test mention",
            "date": "2024-01-01T13:00:00Z",
            "source": "twitter",
        },
    ]

    results = processor.process_mentions(mentions)
    assert len(results) == 2
    assert all(r["hashtags"] == ["test"] for r in results)


def test_validate_mention_missing_field(processor: MentionProcessor) -> None:
    """Test validation of missing required field"""
    invalid_mention = {
        "id": "mention123",
        "text": "Test mention",
        # Missing date
        "source": "twitter",
    }

    with pytest.raises(ValidationError) as exc_info:
        processor.process_mention(invalid_mention)
    assert "Missing required field: date" in str(exc_info.value)


def test_validate_mention_invalid_date(processor: MentionProcessor) -> None:
    """Test validation of invalid date format"""
    invalid_mention = {
        "id": "mention123",
        "text": "Test mention",
        "date": "invalid-date",
        "source": "twitter",
    }

    with pytest.raises(ValidationError) as exc_info:
        processor.process_mention(invalid_mention)
    assert "Invalid date format" in str(exc_info.value)


def test_validate_mention_invalid_url(processor: MentionProcessor) -> None:
    """Test validation of invalid URL"""
    invalid_mention = {
        "id": "mention123",
        "text": "Test mention",
        "date": "2024-01-01T12:00:00Z",
        "source": "twitter",
        "url": "http://",  # Invalid URL with scheme but no domain
    }

    with pytest.raises(ValidationError) as exc_info:
        processor.process_mention(invalid_mention)
    assert "Invalid URL format" in str(exc_info.value)


def test_clean_mention_text(processor: MentionProcessor) -> None:
    """Test text cleaning"""
    mention = {
        "id": "mention123",
        "text": "  Multiple    spaces   and\nnewlines\r\n",
        "date": "2024-01-01T12:00:00Z",
        "source": "twitter",
    }

    result = processor.process_mention(mention)
    assert result["text"] == "Multiple spaces and newlines"


def test_clean_mention_url(processor: MentionProcessor) -> None:
    """Test URL normalization"""
    mention = {
        "id": "mention123",
        "text": "Test mention",
        "date": "2024-01-01T12:00:00Z",
        "source": "twitter",
        "url": "example.com/page",
    }

    result = processor.process_mention(mention)
    assert result["url"] == "https://example.com/page"


def test_enrich_mention_types(processor: MentionProcessor) -> None:
    """Test mention type detection"""
    mentions = [
        {
            "id": "1",
            "text": "Tweet",
            "date": "2024-01-01T12:00:00Z",
            "source": "twitter",
        },
        {
            "id": "2",
            "text": "News",
            "date": "2024-01-01T12:00:00Z",
            "source": "news article",
        },
        {
            "id": "3",
            "text": "Review",
            "date": "2024-01-01T12:00:00Z",
            "source": "product review",
        },
    ]

    results = processor.process_mentions(mentions)
    assert results[0]["mention_type"] == "tweet"
    assert results[1]["mention_type"] == "news"
    assert results[2]["mention_type"] == "review"


def test_prepare_for_storage_search_text(processor: MentionProcessor, valid_mention) -> None:
    """Test search text generation"""
    result = processor.process_mention(valid_mention)

    # Check that search text includes all relevant fields
    search_text = result["search_text"]
    assert valid_mention["text"].lower() in search_text
    assert valid_mention["author"].lower() in search_text
    assert "awesome" in search_text
    assert "johndoe" in search_text


def test_process_mention_minimal(processor: MentionProcessor) -> None:
    """Test processing a mention with minimal fields"""
    mention = {
        'text': 'Hello world',
        'source': 'test',
        'url': 'https://example.com',
        'author': 'test_user',
        'date': '2024-01-01T00:00:00Z',
        'status': 'new'
    }
    
    processed = processor.process_mention(mention)
    
    assert processed['text'] == 'Hello world'
    assert processed['source'] == 'test'
    assert processed['url'] == 'https://example.com'
    assert processed['author'] == 'test_user'
    assert processed['date'] == '2024-01-01T00:00:00Z'
    assert processed['status'] == 'new'
    assert processed['language'] == 'unknown'
    assert processed['sentiment'] == 'neutral'
    assert 'processed_at' in processed
