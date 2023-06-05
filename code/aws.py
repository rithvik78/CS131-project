import boto3
from boto3.dynamodb.conditions import Key
import json
import os
from decimal import Decimal

# Load AWS credentials
with open("aws_credentials.json") as json_file:
    credentials = json.load(json_file)

os.environ["AWS_ACCESS_KEY_ID"] = credentials["aws_access_key_id"]
os.environ["AWS_SECRET_ACCESS_KEY"] = credentials["aws_secret_access_key"]


def get_s3_client():
    s3 = boto3.client(
        "s3",
        region_name="us-west-1",  # replace 'your-region' with your S3 bucket region
        aws_access_key_id=credentials["aws_access_key_id"],
        aws_secret_access_key=credentials["aws_secret_access_key"],
    )
    return s3


def get_table_resource(table_name):
    dynamodb = boto3.resource(
        "dynamodb",
        region_name="us-east-2",  # replace 'your-region' with your DynamoDB table region
        aws_access_key_id=credentials["aws_access_key_id"],
        aws_secret_access_key=credentials["aws_secret_access_key"],
    )
    table = dynamodb.Table(table_name)
    return table


def upload_file_to_bucket(bucket_name, file_path):
    s3 = get_s3_client()
    file_name = file_path.split("/")[-1]
    s3.upload_file(file_path, bucket_name, file_name)
    return file_name


def get_last_item(table_name):
    table = get_table_resource(table_name)
    response = table.scan()
    items = response.get("Items", [])
    if items:
        last_item = max(items, key=lambda x: x.get("sno", 0))
        return last_item
    else:
        return {"sno": 0}  # Dummy value for 'sno' key


def add_metadata_to_dynamodb(
    table_name, username, description, image_s3_key, audio_s3_key
):
    table = get_table_resource(table_name)
    last_item = get_last_item(table_name)
    sno = (
        Decimal(int(last_item["sno"]) + 1) if last_item else Decimal(1)
    )  # use Decimal here
    response = table.put_item(
        Item={
            "sno": sno,
            "username": username,
            "description": description,
            "image_s3_key": image_s3_key,
            "audio_s3_key": audio_s3_key,
        }
    )
    return response


def update_metadata_in_dynamodb(table_name, sno, username, new_description):
    table = get_table_resource(table_name)
    response = table.update_item(
        Key={
            "sno": Decimal(sno),  # Convert the string 'sno' to a Decimal
            "username": username,  # Add username to the key
        },
        UpdateExpression="SET description = :desc",
        ExpressionAttributeValues={
            ":desc": new_description,
        },
        ReturnValues="UPDATED_NEW",
    )
    return response
