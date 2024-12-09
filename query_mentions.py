from datetime import datetime
from decimal import Decimal

from database import MentionDatabase


def query_reddit_mentions():
    db = MentionDatabase()

    print("Querying Reddit mentions...")
    mentions = db.query_mentions_by_source("reddit")

    print(f"\nFound {len(mentions)} Reddit mentions:")
    for mention in mentions:
        # Convert Decimal timestamp to readable date
        timestamp = int(mention["timestamp"])
        mention_date = datetime.fromtimestamp(timestamp)
        print(f"\nID: {mention['mention_id']}")
        print(f"Date: {mention_date}")
        print(f"Content: {mention['content']}")
        print(f"URL: {mention['url']}")
        print("---")


if __name__ == "__main__":
    query_reddit_mentions()
