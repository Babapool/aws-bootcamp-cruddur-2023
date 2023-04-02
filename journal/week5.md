# Week 5 — DynamoDB and Serverless Caching

## Required Homework

Before we start writing out we should first restrcture our directory in the following manner:
```
bin
|--db
   |--connect
   |--create
   |--drop
   |--schema-load
   |--seed
   |--session
   |--setup
|--ddb            # for dynamoDB
|--rds
   |--update-sg-rule
```

Because we restrcutured our scripts, we need to do the following changes:

a. In `bin/db/setup` update the following paths:
```py
bin_path="$(realpath .)/bin"
source "$bin_path/db/drop"
source "$bin_path/db/create"
source "$bin_path/db/schema-load"
source "$bin_path/db/seed"
```

b. Update the `.gitpod.yml` to update the path of the file thatr provides the IP address of the GitPod environment and update the SG rule accordingly:
```YAML
command: |
      export GITPOD_IP=$(curl ifconfig.me)
      source "$THEIA_WORKSPACE_ROOT/backend-flask/bin/rds/update-sg-rule"
```      

### DynamoDB scripts

- First we will need to add the `boto3` dependency into our `requirements.txt` file and then run `pip instal -r requirements.txt`.

- We will create the following scrpits in the `bin/ddb` repository:

a. schema-load (Use this to create DynamoDB table)

- Add the following code to our file:
```bash
#!/usr/bin/env python3

import boto3
import sys

attrs = {
  'endpoint_url': 'http://localhost:8000'
}

if len(sys.argv) == 2:
  if "prod" in sys.argv[1]:
    attrs = {}

ddb = boto3.client('dynamodb',**attrs)

table_name = 'cruddur-messages'


response = ddb.create_table(
  TableName=table_name,
  AttributeDefinitions=[
    {
      'AttributeName': 'pk',
      'AttributeType': 'S'
    },
    {
      'AttributeName': 'sk',
      'AttributeType': 'S'
    },
  ],
  KeySchema=[
    {
      'AttributeName': 'pk',
      'KeyType': 'HASH'
    },
    {
      'AttributeName': 'sk',
      'KeyType': 'RANGE'
    },
  ],
  #GlobalSecondaryIndexes=[
  #],
  BillingMode='PROVISIONED',
  ProvisionedThroughput={
      'ReadCapacityUnits': 5,
      'WriteCapacityUnits': 5
  }
)

print(response)
```

- Provide the necessary permissions using:
```bash
chmod u+x bin/ddb/schema-load
```

b. list-tables (To list the tables created)
- Add the following code to the `ddb/list-tables` file:
```bash
#! /usr/bin/bash
set -e # stop if it fails at any point

if [ "$1" = "prod" ]; then
  ENDPOINT_URL=""
else
  ENDPOINT_URL="--endpoint-url=http://localhost:8000"
fi

aws dynamodb list-tables $ENDPOINT_URL \
--query TableNames \
--output table
```

- Provide the necessary permissions using:
```bash
chmod u+x bin/ddb/list-tables
```

c. drop (To drop any created table)
- Add the following code to the `ddb/drop` file:
```bash
#! /usr/bin/bash

set -e # stop if it fails at any point

if [ -z "$1" ]; then
  echo "No TABLE_NAME argument supplied eg ./bin/ddb/drop cruddur-messages prod "
  exit 1
fi
TABLE_NAME=$1

if [ "$2" = "prod" ]; then
  ENDPOINT_URL=""
else
  ENDPOINT_URL="--endpoint-url=http://localhost:8000"
fi

echo "deleting table: $TABLE_NAME"

aws dynamodb delete-table $ENDPOINT_URL \
  --table-name $TABLE_NAME
```

- Provide the necessary permissions using:
```
chmod u+x bin/ddb/drop
```

d. seed (To seed data into the table)
- Add the following code to the `ddb/seed` file. You can see the contents of the `ddb/seed` file form [here](../backend-flask/bin/db/seed).

- Update the [seed.sql](../backend/db/seed/sql) to include the email ID. To seed the data into the DB, run the following commands:
```
./bin/db/create
./bin/db/schema-load
./bin/db/seed
```

- Add the following permissions:
```bash
chmod u+x ./bin/ddb/seed
```

e. scan (To scan the table rows)
- Add the following code to the `ddb/scan` file:
```py
#!/usr/bin/env python3

import boto3

attrs = {
  'endpoint_url': 'http://localhost:8000'
}
ddb = boto3.resource('dynamodb',**attrs)
table_name = 'cruddur-messages'

table = ddb.Table(table_name)
response = table.scan()

items = response['Items']
for item in items:
  print(item)
```

- Provide the necessary permissions using:
```
chmod u+x bin/ddb/scan
```

### Implement Pattern Scripts for Read and List Conversations

We will create pattern scripts which will help us to read and list the conversations we created. We will intialize a `bin/ddb/patterns` directory to store these
scripts.

a. List Conversations (Help us see how the consume capacity as well)
- Add the following lines of code to the `bin/ddb/patterns/get-conversation` file:
```py
#!/usr/bin/env python3

import boto3
import sys
import json
import datetime

attrs = {
  'endpoint_url': 'http://localhost:8000'
}

if len(sys.argv) == 2:
  if "prod" in sys.argv[1]:
    attrs = {}

dynamodb = boto3.client('dynamodb',**attrs)
table_name = 'cruddur-messages'

message_group_uuid = "5ae290ed-55d1-47a0-bc6d-fe2bc2700399"

# define the query parameters
current_year = datetime.datetime.now().year
query_params = {
  'TableName': table_name,
  'ScanIndexForward': False,
  'Limit': 20,
  'ReturnConsumedCapacity': 'TOTAL',
  'KeyConditionExpression': 'pk = :pk AND begins_with(sk,:year)',
  #'KeyConditionExpression': 'pk = :pk AND sk BETWEEN :start_date AND :end_date',
  'ExpressionAttributeValues': {
    ':year': {'S': '2023'},
    #":start_date": { "S": "2023-03-01T00:00:00.000000+00:00" },
    #":end_date": { "S": "2023-03-19T23:59:59.999999+00:00" },
    ':pk': {'S': f"MSG#{message_group_uuid}"}
  }
}


# query the table
response = dynamodb.query(**query_params)

# print the items returned by the query
print(json.dumps(response, sort_keys=True, indent=2))

# print the consumed capacity
print(json.dumps(response['ConsumedCapacity'], sort_keys=True, indent=2))

items = response['Items']
items.reverse()

for item in items:
  sender_handle = item['user_handle']['S']
  message       = item['message']['S']
  timestamp     = item['sk']['S']
  dt_object = datetime.datetime.strptime(timestamp, '%Y-%m-%dT%H:%M:%S.%f%z')
  formatted_datetime = dt_object.strftime('%Y-%m-%d %I:%M %p')
  print(f'{sender_handle: <12}{formatted_datetime: <22}{message[:40]}...')
```
- Add the following permissions:
```bash
chmod u+x ./bin/ddb/patterns/get-conversation
```

b. List Conversions
- Add the following lines of code to the `bin/ddb/patterns/list-conversations` file:
```py
#!/usr/bin/env python3

import boto3
import sys
import json
import os

current_path = os.path.dirname(os.path.abspath(__file__))
parent_path = os.path.abspath(os.path.join(current_path, '..', '..', '..'))
sys.path.append(parent_path)
from lib.db import db

attrs = {
  'endpoint_url': 'http://localhost:8000'
}

if len(sys.argv) == 2:
  if "prod" in sys.argv[1]:
    attrs = {}

dynamodb = boto3.client('dynamodb',**attrs)
table_name = 'cruddur-messages'

def get_my_user_uuid():
  sql = """
    SELECT 
      users.uuid
    FROM users
    WHERE
      users.handle =%(handle)s
  """
  uuid = db.query_value(sql,{
    'handle':  'andrewbrown'
  })
  return uuid

my_user_uuid = get_my_user_uuid()
print(f"my-uuid: {my_user_uuid}")

# define the query parameters
query_params = {
  'TableName': table_name,
  'KeyConditionExpression': 'pk = :pk',
  'ExpressionAttributeValues': {
    ':pk': {'S': f"GRP#{my_user_uuid}"}
  },
  'ReturnConsumedCapacity': 'TOTAL'
}

# query the table
response = dynamodb.query(**query_params)

# print the items returned by the query
print(json.dumps(response, sort_keys=True, indent=2))
```
- Also update our [db.py](../backend-flask/lib/db.py) file.

- - Add the following permissions:
```bash
chmod u+x ./bin/ddb/patterns/list-conversations
```
