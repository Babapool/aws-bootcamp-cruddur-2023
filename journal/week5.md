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

![ddb-schema-load](/journal/assets/ddb-schema-load.png)

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
![ddb-list-tables](/journal/assets/ddb-list-tables.png)

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
![ddb-drop-table](/journal/assets/ddb-drop-table.png)

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
![ddb-seed](/journal/assets/ddb-seed.png)

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
![ddb-scan](/journal/assets/ddb-scan.png)

### Implement Pattern Scripts for Read and List Conversations

We will create pattern scripts which will help us to read and list the conversations we created. We will intialize a `bin/ddb/patterns` directory to store these
scripts.

- Followed all the steps in the video to implement all the access patterns and DynamoDB streams

#### Access Pattern A
![pattern A](/journal/assets/dynamodb-access-pattern-a.png)

#### Access Pattern B
![pattern B](/journal/assets/dynamodb-access-pattern-b.png)

#### Access Pattern C
![pattern C](/journal/assets/dynamodb-access-pattern-c.png)

#### Access Pattern D
![pattern d.i](/journal/assets/dynamodb-access-pattern-di.png)
![patternn d.ii](/journal/assets/dynamodb-access-pattern-dii.png)

#### Access Pattern E
![pattern E](/journal/assets/dynamodb-access-pattern-E.png)
