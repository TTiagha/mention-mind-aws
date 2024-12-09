from database import MentionDatabase


def main():
    print("Creating DynamoDB table for MentionMind...")
    db = MentionDatabase()
    table = db.create_table()
    print(f"Table {db.table_name} created successfully!")
    print(f"Table status: {table.table_status}")


if __name__ == "__main__":
    main()
