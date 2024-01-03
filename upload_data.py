import json

import boto3

dynamodb = boto3.resource("dynamodb")

table = dynamodb.Table("CSE546-student-database")
items = []

with open("student_data.json", "r") as f:
    data = json.load(f)


with table.batch_writer() as batch:
    for item in data:
        batch.put_item(Item=item)
