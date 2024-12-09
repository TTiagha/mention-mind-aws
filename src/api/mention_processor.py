"""
Process mentions to enrich with metadata
"""

import re
from datetime import datetime
from typing import Dict, List
from urllib.parse import urlparse

import pytz

from .exceptions import ValidationError


class MentionProcessor:
    """Process mentions to enrich with metadata"""

    def __init__(self) -> None:
        """Initialize the mention processor"""
        # Common patterns we want to extract
        self.hashtag_pattern = re.compile(r"#(\w+)")
        self.mention_pattern = re.compile(r"@(\w+)")
        self.url_pattern = re.compile(
            r"http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*(),]|"
            r"(?:%[0-9a-fA-F][0-9a-fA-F]))+"
        )

    def process_mentions(self, mentions: List[Dict]) -> List[Dict]:
        """
        Process a list of mentions to enrich with metadata

        Args:
            mentions: List of mentions to process

        Returns:
            List of processed mentions
        """
        return [self.process_mention(mention) for mention in mentions]

    def process_mention(self, mention: Dict) -> Dict:
        """
        Process a single mention to enrich with metadata

        Args:
            mention: Mention to process

        Returns:
            Processed mention with metadata
        """
        # Validate required fields
        required_fields = ["text", "source", "url", "author", "date", "status"]
        for field in required_fields:
            if field not in mention:
                raise ValidationError(f"Missing required field: {field}")

        # Clean and validate fields
        mention["text"] = self._clean_text(mention["text"])
        mention["url"] = self._clean_url(mention["url"])
        mention["date"] = self._validate_date(mention["date"])

        # Extract metadata
        mention["hashtags"] = self._extract_hashtags(mention["text"])
        mention["mentioned_users"] = self._extract_mentions(mention["text"])
        mention["search_text"] = self._generate_search_text(mention)
        mention["processed_at"] = datetime.now(pytz.UTC).isoformat()
        mention["sentiment"] = self._analyze_sentiment(mention["text"])
        mention["language"] = self._detect_language(mention["text"])

        return mention

    def _clean_text(self, text: str) -> str:
        """Clean text by removing extra whitespace"""
        return " ".join(text.split())

    def _clean_url(self, url: str) -> str:
        """Clean and validate URL"""
        if not self.url_pattern.match(url):
            raise ValidationError("Invalid URL format")
        parsed = urlparse(url)
        return f"{parsed.scheme}://{parsed.netloc}{parsed.path}"

    def _validate_date(self, date: str) -> str:
        """Validate date is in ISO format"""
        try:
            datetime.fromisoformat(date.replace("Z", "+00:00"))
            return date
        except ValueError:
            raise ValidationError("Invalid date format")

    def _extract_hashtags(self, text: str) -> List[str]:
        """Extract hashtags from text"""
        return self.hashtag_pattern.findall(text)

    def _extract_mentions(self, text: str) -> List[str]:
        """Extract @mentions from text"""
        return self.mention_pattern.findall(text)

    def _generate_search_text(self, mention: Dict) -> str:
        """Generate searchable text from mention"""
        parts = [
            mention["text"].lower(),
            mention["author"].lower(),
            " ".join(mention["hashtags"]),
            " ".join(mention["mentioned_users"]),
        ]
        return " ".join(parts)

    def _detect_language(self, text: str) -> str:
        """Detect language of text (placeholder)"""
        return "unknown"

    def _analyze_sentiment(self, text: str) -> str:
        """Analyze sentiment of text (placeholder)"""
        return "neutral"
