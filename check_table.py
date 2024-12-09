import boto3


def check_table_status():
    dynamodb = boto3.resource("dynamodb")
    table = dynamodb.Table("mentions")
    print(f"Table Status: {table.table_status}")
    return table.table_status


if __name__ == "__main__":
    check_table_status()
