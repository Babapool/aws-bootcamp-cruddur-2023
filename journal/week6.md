# Week 6 — Deploying Containers

## Adding Health Check Scripts

### 1. Testing RDS Connection

We will this `test script` in the `test` file in the `db` directory to easily check our connection from our container. Add the following code:

```py
#!/usr/bin/env python3

import psycopg
import os
import sys

connection_url = os.getenv("CONNECTION_URL")

conn = None
try:
  print('attempting connection')
  conn = psycopg.connect(connection_url)
  print("Connection successful!")
except psycopg.Error as e:
  print("Unable to connect to the database:", e)
finally:
  conn.close()
```
To make it executable, provide the following permisions:
```sh
chmod u+x ./bin/db/test
```
### 2. Testing the Flask Script

Add the following endpoint for our flask app:
```py
@app.route('/api/health-check')
def health_check():
  return {'success': True}, 200
```

Create a new script at `bin/flask/health-check` directory:
```sh
#!/usr/bin/env python3

import urllib.request

try:
  response = urllib.request.urlopen('http://localhost:4567/api/health-check')
  if response.getcode() == 200:
    print("[OK] Flask server is running")
    exit(0) # success
  else:
    print("[BAD] Flask server is not running")
    exit(1) # false
# This for some reason is not capturing the error....
#except ConnectionRefusedError as e:
# so we'll just catch on all even though this is a bad practice
except Exception as e:
  print(e)
  exit(1) # false
```
To make it executable, provide the following permisions:
```sh
chmod u+x ./bin/db/test
```

## Creatng a CloudWatch Log Group

We need to create a log group which will be required later for task-definitions. Use the following commands:
```
aws logs create-log-group --log-group-name /cruddur/fargate-cluster
aws logs put-retention-policy --log-group-name /cruddur/fargate-cluster --retention-in-days 1
```

## Creating an ECS Cluster

- To provision an ECS cluster, run the following command:
```sh
aws ecs create-cluster \
--cluster-name cruddur \
--service-connect-defaults namespace=cruddur
```

## Creating a ECR Repo and Pushing the Images

- We want to create our ECR container registry repo to avoid any problems that can be encountered with DockerHub while trying to pull any images.

### 1. Python Base Image

- We wil first create an ECR repo for the `Python base image`. To create the repository, run the following command:
```sh
aws ecr create-repository \
  --repository-name cruddur-python \
  --image-tag-mutability MUTABLE
```
- Next log into our ECR repo for pushing the images. To log into our ECR repo run the following command:
```
aws ecr get-login-password --region $AWS_DEFAULT_REGION | docker login --username AWS --password-stdin "$AWS_ACCOUNT_ID.dkr.ecr.$AWS_DEFAULT_REGION.amazonaws.com"
```

- Export the URL for the `cruddur-python` repo:
```
export ECR_PYTHON_URL="$AWS_ACCOUNT_ID.dkr.ecr.$AWS_DEFAULT_REGION.amazonaws.com/cruddur-python"
gp env ECR_PYTHON_URL="$AWS_ACCOUNT_ID.dkr.ecr.$AWS_DEFAULT_REGION.amazonaws.com/cruddur-python"
```

- Pull the `python` image from DockerHub by using the following commands
```
docker pull python:3.10-slim-buster
```

- To tag this image use the following command:
```
docker tag python:3.10-slim-buster $ECR_PYTHON_URL:3.10-slim-buster
```

- To push our image to the ECR repo, use the following command:
```
docker push $ECR_PYTHON_URL:3.10-slim-buster
```

### 2. Backend Flask

- We need to update the `backend-flask/Dockerfile` to use the Python ECR image from above. Replace the image URL with currently in the code with the Image URL 
from ECR.

-  Ceate an ECR repo for the `Backend flask image`. To create the repository, run the following command:
```sh
aws ecr create-repository \
  --repository-name backend-flask \
  --image-tag-mutability MUTABLE
```

- Export the URL for the `backend-file` repo:
```
export ECR_BACKEND_FLASK_URL="$AWS_ACCOUNT_ID.dkr.ecr.$AWS_DEFAULT_REGION.amazonaws.com/backend-flask"
gp env  ECR_BACKEND_FLASK_URL="$AWS_ACCOUNT_ID.dkr.ecr.$AWS_DEFAULT_REGION.amazonaws.com/backend-flask"
```
- Buil the image using:
```
docker build -t backend-flask .
```

- Tag the image using:
```
docker tag backend-flask:latest $ECR_BACKEND_FLASK_URL:latest
```

- Push it using:
```
docker push $ECR_BACKEND_FLASK_URL:latest
```
