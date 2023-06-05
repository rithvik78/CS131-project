import json
import boto3

# Load credentials from JSON file
with open("aws_credentials.json", "r") as file:
    creds = json.load(file)

# Initialize the DynamoDB resource
dynamodb = boto3.resource(
    "dynamodb",
    region_name="us-east-2",  # Set this to the region of your DynamoDB table
    aws_access_key_id=creds["aws_access_key_id"],
    aws_secret_access_key=creds["aws_secret_access_key"],
)

# Your table name
table_name = "translationprojectcs131"


def scan_table(table_name):
    table = dynamodb.Table(table_name)
    response = table.scan()
    return response["Items"]


# Print all items in the table
items = scan_table(table_name)
for item in items:
    print(item)
