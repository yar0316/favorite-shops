"""Initialize the isolated emulator table from the Terraform key schema."""
import os
import time
from pathlib import Path

import boto3
from botocore.exceptions import ClientError, EndpointConnectionError


def create_table(client):
    client.create_table(
        TableName="favorite-shops-local",
        BillingMode="PAY_PER_REQUEST",
        AttributeDefinitions=[{"AttributeName": name, "AttributeType": "S"} for name in ("PK", "SK", "GSI1PK", "GSI1SK")],
        KeySchema=[{"AttributeName": "PK", "KeyType": "HASH"}, {"AttributeName": "SK", "KeyType": "RANGE"}],
        GlobalSecondaryIndexes=[{
            "IndexName": "GSI1",
            "KeySchema": [{"AttributeName": "GSI1PK", "KeyType": "HASH"}, {"AttributeName": "GSI1SK", "KeyType": "RANGE"}],
            "Projection": {"ProjectionType": "ALL"},
        }],
    )


def main():
    for _ in range(60):
        if all(Path(os.environ[key]).is_file() for key in ("AWS_SHARED_CREDENTIALS_FILE", "AWS_CA_BUNDLE")):
            break
        time.sleep(1)
    else:
        raise RuntimeError("Emulator credentials/certificate were not created")
    client = boto3.client("dynamodb", region_name="ap-northeast-1")
    for attempt in range(60):
        try:
            create_table(client)
            print("Created favorite-shops-local")
            return
        except client.exceptions.ResourceInUseException:
            print("favorite-shops-local already exists")
            return
        except EndpointConnectionError:
            if attempt == 59:
                raise
            time.sleep(1)


if __name__ == "__main__":
    main()
