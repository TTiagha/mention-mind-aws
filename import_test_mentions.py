import uuid
from datetime import datetime, timedelta

from database import MentionDatabase


def create_test_mentions(count=10):
    base_time = datetime.now()
    mentions = []

    sources = ["reddit", "twitter"]
    for i in range(count):
        # Create mentions spread across last few days
        mention_time = base_time - timedelta(days=i % 3)

        mention = {
            "mention_id": str(uuid.uuid4()),
            "timestamp": int(mention_time.timestamp()),
            "source": sources[i % 2],  # Alternate between reddit and twitter
            "content": f"Test mention #{i + 1}: This is test content for {sources[i % 2]}",
            "url": f"https://{sources[i % 2]}.com/test/{i + 1}",
            "author": f"test_user_{i + 1}",
            "sentiment": "neutral",
        }
        mentions.append(mention)

    return mentions


def main():
    db = MentionDatabase()
    mentions = create_test_mentions(10)

    print("Importing 10 test mentions...")
    successful, failed = db.batch_store_mentions(mentions)

    print(f"Successfully imported: {len(successful)} mentions")
    if failed:
        print(f"Failed to import: {len(failed)} mentions")

    # Print out the imported mentions
    print("\nImported Mentions:")
    for mention in successful:
        print(f"ID: {mention['mention_id']}")
        print(f"Source: {mention['source']}")
        print(f"Content: {mention['content']}")
        print("---")


if __name__ == "__main__":
    main()
