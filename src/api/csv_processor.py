"""
Process mentions from CSV files into standardized format
"""

import csv
from datetime import datetime
from typing import Dict, List

from .mention_processor import MentionProcessor


class CSVProcessor:
    """Process mentions from CSV files"""

    def __init__(self) -> None:
        self.mention_processor = MentionProcessor()

    def process_reddit_csv(self, csv_path: str) -> List[Dict]:
        """
        Process Reddit CSV file into standardized mentions

        Args:
            csv_path: Path to Reddit CSV file

        Returns:
            List of processed mentions
        """
        mentions = []
        with open(csv_path, "r", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for row in reader:
                # Combine title and snippet for text
                text = row["title"]
                if row.get("snippet"):
                    text = f"{text}\n{row['snippet']}"

                mention = {
                    "id": row["id"],
                    "project_id": row["project_id"],
                    "source": row["source"],
                    "text": text,
                    "url": row["url"],
                    "author": row["author"],
                    "date": row["date_added"],  # Already in ISO format
                    "status": row["status"],
                }

                try:
                    processed = self.mention_processor.process_mention(mention)
                    mentions.append(processed)
                except Exception as e:
                    print(f"Error processing mention {mention['id']}: {str(e)}")

        return mentions

    def process_twitter_csv(self, csv_path: str) -> List[Dict]:
        """
        Process Twitter CSV file into standardized mentions

        Args:
            csv_path: Path to Twitter CSV file

        Returns:
            List of processed mentions
        """
        mentions = []
        with open(csv_path, "r", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for row in reader:
                # Combine title and snippet for text
                text = row["Title"]
                if row.get("Snippet"):
                    text = f"{text}\n{row['Snippet']}"

                mention = {
                    "id": row.get(
                        "ID", f"twitter_{datetime.now().timestamp()}"
                    ),  # Generate ID if not present
                    "source": "twitter",
                    "text": text,
                    "url": row["URL"],
                    "author": row["Account Name"],
                    "date": row["Date added"],  # Already in ISO format
                    "status": row["Status"],
                }

                try:
                    processed = self.mention_processor.process_mention(mention)
                    mentions.append(processed)
                except Exception as e:
                    print(f"Error processing mention from {mention['url']}: {str(e)}")

        return mentions
