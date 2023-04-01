# Week 4 — Postgres and RDS

## Required Homework

### Creating RDS Postgres Instance

To create a RDS Postgres Instance, run the following AWS CLI command to provision a Postgres DB instance:
```
aws rds create-db-instance \
  --db-instance-identifier cruddur-db-instance \
  --db-instance-class db.t3.micro \
  --engine postgres \
  --engine-version  14.6 \
  --master-username <your username> \
  --master-user-password <your password> \
  --allocated-storage 20 \
  --availability-zone us-east-1a \
  --backup-retention-period 0 \
  --port 5432 \
  --no-multi-az \
  --db-name cruddur \
  --storage-type gp2 \
  --publicly-accessible \
  --storage-encrypted \
  --enable-performance-insights \
  --performance-insights-retention-period 7 \
  --no-deletion-protection
```
![RDS Instance](assets/rds1.png)

### Creating Schema for Postgres

- To create a scheme for Postgres, we first need to launch the Postgres DB. To do this we need to run the `postgres` service we have in our `docker-compose.yml`. To run this 
container, we need to use the `docker compose up`.

- To connect to our Postgres (psql) , we are going to use the psql client CLI. Rin the following command:
```
psql -U postgres --host localhost
```
The password to connect is `password`.

- To create a DB in Postgres using the psql client, run the following command:
```
CREATE database cruddur;
```
- Run `\l` to check that the DB is created

![Postgre Tables](postgres2.png)

- To create a scheme for our database, in our `backend-flask/db` directory, we are going to write a `schema.sql` file. To populate the DB with things, add the following:
```SQL
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
````
We use this extension to create UUIDs in Postgres.

- To import this schema to our `cruddur` database, run the following command:
```
psql cruddur < db/schema.sql -h localhost -U postgres
```
![Dump schema](assets/postgres3.png)

- Add the the environment variables for our local database:
```
gp env CONNECTION_URL="postgresql://postgres:password@localhost:5433/cruddur"
```
Alternatively you can substitute `localhost` with `127.0.0.1`.

- Add the the environment variables for our RDS database:
```
gp env PROD_CONNECTION_URL="postgresql://<RDS masterusername><RD password>@<Endpint of DB>:5432/cruddur"
```

### Bash scripting for common database actions

- We will create a new folder `bin` in our `backend-flask` directory. This folder will store all the bash scripts (without the extensions) we are common going to frequently for common database functions.

a. Script to drop database:
- Create a file `db-drop` in the `backend-flask/bin` directory and add the following:
```bash
#! /usr/bin/bash

NO_DB_CONNECTION_URL=$(sed 's/\/cruddur//g' <<<"$CONNECTION_URL") #used to manipulate strings -> replaces \cruddur with blank space in $CONNECTION_URL
psql $NO_DB_CONNECTION_URL -c "DROP database cruddur;"
```
- Change the persmission for this file by running the following command:
```
chmod u+x bin/db-drop
```
![DB drop](assets/dbdrop.png)

b. Script to create database:
- Create a file `db-create` in the `backend-flask/bin` directory and add the following:
```bash
#! /usr/bin/bash

NO_DB_CONNECTION_URL=$(sed 's/\/cruddur//g' <<<"$CONNECTION_URL")
psql $NO_DB_CONNECTION_URL -c "CREATE database cruddur;"
```
- Change the persmission for this file by running the following command:
```
chmod u+x bin/db-create
```
![DB create](assets/dbcreate.png)

c. Script to load database schema:
- Create a file `db-load-schema` in the `backend-flask/bin` directory and add the following:
```bash
#! /usr/bin/bash

echo "db-schema-load"

schema_path="$(realpath .)/db/schema.sql"
echo $schema_path

if  [ "$1" == "prod" ]; then
    echo "using production"
    CON_URL=$PROD_CONNECTION_URL
else
    CON_URL=$CONNECTION_URL
fi

#NO_DB_CONNECTION_URL=$(sed 's/\/cruddur//g' <<<"$CONNECTION_URL")
psql $CON_URL cruddur < $schema_path
```

- Change the persmission for this file by running the following command:
```
chmod u+x bin/db-load-schema
```
![dbload scheme](assets/dbschemaload1.png)


d. Creating Tables
To create tables add the following in our `schema.sql` file:
```SQL

DROP TABLE IF EXISTS public.users;
DROP TABLE IF EXISTS public.activities;

CREATE TABLE public.users (
  uuid UUID DEFAULT uuid_generate_v4() PRIMARY KEY,
  display_name text,
  handle text,
  cognito_user_id text,
  created_at TIMESTAMP default current_timestamp NOT NULL
);

CREATE TABLE public.activities (
  uuid UUID DEFAULT uuid_generate_v4() PRIMARY KEY,
  user_uuid UUID NOT NULL,
  message text NOT NULL,
  replies_count integer DEFAULT 0,
  reposts_count integer DEFAULT 0,
  likes_count integer DEFAULT 0,
  reply_to_activity_uuid integer,
  expires_at TIMESTAMP,
  created_at TIMESTAMP default current_timestamp NOT NULL
);
```

- To run/implement this, we need to our our `db-seed` script



e. Script to connect to our database
- Create a file `db-connect` in the `backend-flask/bin` directory and add the following:
```bash
#! /usr/bin/bash

if [ "$1" = "prod" ]; then
  echo "Running in production mode"
  URL=$PROD_CONNECTION_URL
else
  URL=$CONNECTION_URL
fi

psql $URL
```

- Change the persmission for this file by running the following command:
```
chmod u+x bin/db-connect
```

![db connect](assets/dbconnect.png)

f.  Script to add data into out table via a schema/SQL file
- Create a file `db-seed` in the `backend-flask/bin` directory and add the following:
```bash
#! /usr/bin/bash

#echo "== db-seed"
CYAN='\033[1;36m'
NO_COLOR='\033[0m'
LABEL="db-seed"
printf "${CYAN}== ${LABEL}${NO_COLOR}\n"

seed_path="$(realpath .)/db/seed.sql"

echo $seed_path

psql $CONNECTION_URL cruddur < $seed_path
```

- Change the persmission for this file by running the following command:
```
chmod u+x bin/db-seed
```

- Also create `seeq.sql` file in our `db` directory containing the following:
```SQL
-- this file was manually created
INSERT INTO public.users (display_name, handle, cognito_user_id)
VALUES
  ('Andrew Brown', 'andrewbrown' ,'MOCK'),
  ('Andrew Bayko', 'bayko' ,'MOCK');

INSERT INTO public.activities (user_uuid, message, expires_at)
VALUES
  (
    (SELECT uuid from public.users WHERE users.handle = 'andrewbrown' LIMIT 1),
    'This was imported as seed data!',
    current_timestamp + interval '10 day'
  )

```
![db create table](assets/dbseed.png)

g. Script to see how many connection we are using
- Create a file `db-sessions` in the `backend-flask/bin` directory and add the following:
```bash
#! /usr/bin/bash
CYAN='\033[1;36m'
NO_COLOR='\033[0m'
LABEL="db-sessions"
printf "${CYAN}== ${LABEL}${NO_COLOR}\n"

if [ "$1" = "prod" ]; then
  echo "Running in production mode"
  URL=$PROD_CONNECTION_URL
else
  URL=$CONNECTION_URL
fi

NO_DB_URL=$(sed 's/\/cruddur//g' <<<"$URL")
psql $NO_DB_URL -c "select pid as process_id, \
       usename as user,  \
       datname as db, \
       client_addr, \
       application_name as app,\
       state \
from pg_stat_activity;"
```

- Change the persmission for this file by running the following command:
```
chmod u+x bin/db-sessions
```

![db-session](assets/dbsession.png)

h. Script to run the bunch of bash scripts created
- Create a file `db-setyp` in the `backend-flask/bin` directory and add the following:
```bash
#! /usr/bin/bash
-e # stop if it fails at any point

CYAN='\033[1;36m'
NO_COLOR='\033[0m'
LABEL="db-setup"
printf "${CYAN}==== ${LABEL}${NO_COLOR}\n"

bin_path="$(realpath .)/bin"

source "$bin_path/db-drop"
source "$bin_path/db-create"
source "$bin_path/db-schema-load"
source "$bin_path/db-seed"
```

- Change the persmission for this file by running the following command:
```
chmod u+x bin/db-setup
```

![db scripts](assets/dbsetup.png)

### Install Postgres driver in backend application

- Add the following dependencies to install the Postgres driver (`psycopg`) to our `requirements.txt` file:
```
psycopg[binary]
psycopg[pool]
```
Install them by running the `pip -r install requirements.txt`

- To create a connection pool for Postgres, create a file `db.py` in the `backend-flask/lib` directory and add the following:
```py
from psycopg_pool import ConnectionPool
import os

def query_wrap_object(template):
  sql = f"""
  (SELECT COALESCE(row_to_json(object_row),'{{}}'::json) FROM (
  {template}
  ) object_row);
  """
  return sql

def query_wrap_array(template):
  sql = f"""
  (SELECT COALESCE(array_to_json(array_agg(row_to_json(array_row))),'[]'::json) FROM (
  {template}
  ) array_row);
  """
  return sql

connection_url = os.getenv("CONNECTION_URL")
pool = ConnectionPool(connection_url)
  
```

- Add the `CONNECTION_URL` as a environment variable to the `backend-flask` service in our `docker-compose.yml` file:
```YAML 
backend-flask:
    environment:
      CONNECTION_URL: "postgresql://postgres:password@db:5433/cruddur"
  .....
```  

- In our `home_activities.py` we wIll replace our mock endpoint with real API call by doing the following modificiations:
```py
from datetime import datetime, timedelta, timezone
from opentelemetry import trace
tracer = trace.get_tracer("home.activities")

from lib.db import pool

class HomeActivities:
  #def run():#(Logger):
  def run(cognito_user_id=None): #adding user

    #Logger.info("HomeActivities")
    tracer = trace.get_tracer(__name__)
    with tracer.start_as_current_span("home-activities-mock-data"):
      span = trace.get_current_span()
      now = datetime.now(timezone.utc).astimezone()
      span.set_attribute("app.now", now.isoformat())

      sql = query_wrap_array("""
      SELECT
        activities.uuid,
        users.display_name,
        users.handle,
        activities.message,
        activities.replies_count,
        activities.reposts_count,
        activities.likes_count,
        activities.reply_to_activity_uuid,
        activities.expires_at,
        activities.created_at
      FROM public.activities
      LEFT JOIN public.users ON users.uuid = activities.user_uuid
      ORDER BY activities.created_at DESC
      """)
     print(sql)
  
      with pool.connection() as conn:
        with conn.cursor() as cur:
          cur.execute(sql)
          # this will return a tuple
          # the first field being the data
          json = cur.fetchall()
      return json[0]
      return results

```

- Run the application by using the `docker compose up` command and we get the following output

![Postgres seed](assets/rdsoutput.png)

### Connect Gitpod to RDS instance

- To connect to our RDS DB, run the following command:
```psql $PROD_CONNECTION_URL```

This will hang as we need to attach the Security Group having the Gitpod IP to allow connection to pass through.

- To find the IP of our Gitpod instance use the following command:
```
GITPOD_IP=$(curl ifconfig.me)
echo $GITPOD_IP
export GITPOD_IP=$(curl ifconfig.me)
```
To export the IP address automatically, add the following to your `.gitpod.yml` file:
```YAML
    command: |
      export GITPOD_IP=$(curl ifconfig.me)
      source "$THEIA_WORKSPACE_ROOT/backend-flask/bin/rds-update-sg-rule"
```      

- Edit the inbound security group for Postgres so that we can whitelist the Gitpod IP

![RDS SG](assets/rdssg.png)

- Now try to connect to the RDS instance

- Since everytime we will launch a Gitpod environment, a new IP address will be assigned, so we will make a script to update the Security groups. To modify the Security group of EC2 instance do the following:

a. Export the Security Group ID and the Security group rule ID
```
gp env DB_SG_ID="	sg-0fd3623daa99d5cc5"
gp env DB_SG_RULE_ID="sgr-055ca3271721be10a"
```

b. Create a following file `rds-update-sg-rule` the `backend-flask/bin` directory:
```bash
#! /usr/bin/bash

CYAN='\033[1;36m'
NO_COLOR='\033[0m'
LABEL="rds-update-sg-rule"
printf "${CYAN}==== ${LABEL}${NO_COLOR}\n"

aws ec2 modify-security-group-rules \
    --group-id $DB_SG_ID \
    --security-group-rules "SecurityGroupRuleId=$DB_SG_RULE_ID,SecurityGroupRule={Description=GITPOD,IpProtocol=tcp,FromPort=5432,ToPort=5432,CidrIpv4=$GITPOD_IP/32}"
```

c. Update the permisions by using:
```
chmod u+x ./bin/rds-update-sg-rule
```
![SG Bash script](assets/sgbash.png)
![SG Bash](assets/rdsgitpodconnection.png)

### Create AWS Cognito Lambda trigger to insert user data into database

- First we need to create a handler function in AWS Lambda in the same VPC as our RDS as shown below

- Add the following code to our lambda function:
```py
import json
import os
import psycopg2

def lambda_handler(event, context):
    user = event['request']['userAttributes']
    user_display_name = user["name"]
    user_email = user["email"]
    user_handle = user["preferred_username"]
    user_cognito_id = user["sub"]
        
    try:
        sql = f"""
        INSERT INTO public.users (
            display_name,
            email, 
            handle, 
            cognito_user_id
            ) 
        VALUES(
           '{user_display_name}',
           '{user_email}',
           '{user_handle}',
           '{user_cognito_id}'
            )
        """ 
            
        print(sql)
        conn = psycopg2.connect(os.getenv("CONNECTION_URL"))
        cur = conn.cursor()
        cur.execute(sql)
        conn.commit()
        print('Commit Done')

    except (Exception, psycopg2.DatabaseError) as error:
        print(error)
        
    finally:
        if conn is not None:
            cur.close()
            conn.close()
            print('Database connection closed.')

    return event
```
Click the `Deploy` button to save the code

- To add the following envars to our lambda code go to `Configuration`->`Environment Variables`->`Edit` and then add the following:


- We need to add a Lambda layer for `psycopg2`. This will allow us to run Postgres through the Lambda function. Go the `Layers` option and add a layer by specifying this ARN : 
`arn:aws:lambda:us-east-1:898466741470:layer:psycopg2-py38:2`

- For adding the Cognito trigger for the Lambda function do the following:

a. Head over to `Cognito`-> `User pools` -> `< Your User pool >` -> `User pool properties`- > `Add Lambda Trigger`. In there, add a lambda trigger with the following configuration:


- Add the following role to our Lambda function to make network calls.
a. Go to the `Configurations`->`Permissions`. 
b. From there go the `IAM` service page choose our current role and go to `Add Permissions`. 
c. Choose `Create Policy` and add the following JSON role:
```JSON
{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Effect": "Allow",
            "Action": [
                "ec2:CreateNetworkInterface",
                "ec2:DeleteNetworkInterface",
                "ec2:DescribeNetworkInterfaces",
                "ec2:AttachNetworkInterface",
                "ec2:DescribeInstances"
            ],
            "Resource": "*"
        }
    ]
}
```
Name it as `AWSLambdaVPCAccessExecutionRole`.
d. Choose our newly created policy and attach it to our role.

- Attach a VPC to our Lambda function by going to the `Configuration`->`VPC`->`Edit`.

- Now run the application using the `docker compose up` command and then sign up a new user to view the results

![RDS new users](assets/rds-newuser.png)

### Create new activities with a database insert

- To prevent SQL injection in our Lambda code, we do the following changes. You can view those changes in the [aws/lambdas/cruddur-post-confimation.py](aws/lambdas/cruddur-post-confimation.py) file.

- First we will modifiy our `db.py` to create a database object. Do the following modifications:
```py
from psycopg_pool import ConnectionPool
import os
import re
import sys
from flask import current_app as app

class Db:
  def __init__(self):
    self.init_pool()

  def template(self,*args):
    pathing = list((app.root_path,'db','sql',) + args)
    pathing[-1] = pathing[-1] + ".sql"

    template_path = os.path.join(*pathing)

    green = '\033[92m'
    no_color = '\033[0m'
    print("\n")
    print(f'{green} Load SQL Template: {template_path} {no_color}')

    with open(template_path, 'r') as f:
      template_content = f.read()
    return template_content

  def init_pool(self):
    connection_url = os.getenv("CONNECTION_URL")
    self.pool = ConnectionPool(connection_url)
  # we want to commit data such as an insert
  # be sure to check for RETURNING in all uppercases
  def print_params(self,params):
    blue = '\033[94m'
    no_color = '\033[0m'
    print(f'{blue} SQL Params:{no_color}')
    for key, value in params.items():
      print(key, ":", value)

  def print_sql(self,title,sql):
    cyan = '\033[96m'
    no_color = '\033[0m'
    print(f'{cyan} SQL STATEMENT-[{title}]------{no_color}')
    print(sql)
  def query_commit(self,sql,params={}):
    self.print_sql('commit with returning',sql)

    pattern = r"\bRETURNING\b"
    is_returning_id = re.search(pattern, sql)

    try:
      with self.pool.connection() as conn:
        cur =  conn.cursor()
        cur.execute(sql,params)
        if is_returning_id:
          returning_id = cur.fetchone()[0]
        conn.commit() 
        if is_returning_id:
          return returning_id
    except Exception as err:
      self.print_sql_err(err)
  # when we want to return a json object
  def query_array_json(self,sql,params={}):
    self.print_sql('array',sql)

    wrapped_sql = self.query_wrap_array(sql)
    with self.pool.connection() as conn:
      with conn.cursor() as cur:
        cur.execute(wrapped_sql,params)
        json = cur.fetchone()
        return json[0]
  # When we want to return an array of json objects
  def query_object_json(self,sql,params={}):

    self.print_sql('json',sql)
    self.print_params(params)
    wrapped_sql = self.query_wrap_object(sql)

    with self.pool.connection() as conn:
      with conn.cursor() as cur:
        cur.execute(wrapped_sql,params)
        json = cur.fetchone()
        if json == None:
          "{}"
        else:
          return json[0]
  def query_wrap_object(self,template):
    sql = f"""
    (SELECT COALESCE(row_to_json(object_row),'{{}}'::json) FROM (
    {template}
    ) object_row);
    """
    return sql
  def query_wrap_array(self,template):
    sql = f"""
    (SELECT COALESCE(array_to_json(array_agg(row_to_json(array_row))),'[]'::json) FROM (
    {template}
    ) array_row);
    """
    return sql
  def print_sql_err(self,err):
    # get details about the exception
    err_type, err_obj, traceback = sys.exc_info()

    # get the line number when exception occured
    line_num = traceback.tb_lineno

    # print the connect() error
    print ("\npsycopg ERROR:", err, "on line number:", line_num)
    print ("psycopg traceback:", traceback, "-- type:", err_type)

    # print the pgcode and pgerror exceptions
    print ("pgerror:", err.pgerror)
    print ("pgcode:", err.pgcode, "\n")

db = Db()
```

- Do the following modifications in the `home_activties.py`, so that we can use the object we have created above:
```py
from datetime import datetime, timedelta, timezone
from opentelemetry import trace
from lib.db import db
#tracer = trace.get_tracer("home.activities")


class HomeActivities:
  #def run():#(Logger):
  def run(cognito_user_id=None): #adding user

    #Logger.info("HomeActivities")
    #tracer = trace.get_tracer(__name__)
    #with tracer.start_as_current_span("home-activities-mock-data"):
      #span = trace.get_current_span()
      #now = datetime.now(timezone.utc).astimezone()
      #span.set_attribute("app.now", now.isoformat())
    sql = db.template('activities','home')
    results = db.query_array_json(sql)
    return results
```  

- Do the following modifications in the `create_activity.py`, so that we can use the object we have created above:
```py
from datetime import datetime, timedelta, timezone

from lib.db import db

class CreateActivity:
  def run(message, user_handle, ttl):
    model = {
      'errors': None,
      'data': None
    }

    now = datetime.now(timezone.utc).astimezone()

    if (ttl == '30-days'):
      ttl_offset = timedelta(days=30) 
    elif (ttl == '7-days'):
      ttl_offset = timedelta(days=7) 
    elif (ttl == '3-days'):
      ttl_offset = timedelta(days=3) 
    elif (ttl == '1-day'):
      ttl_offset = timedelta(days=1) 
    elif (ttl == '12-hours'):
      ttl_offset = timedelta(hours=12) 
    elif (ttl == '3-hours'):
      ttl_offset = timedelta(hours=3) 
    elif (ttl == '1-hour'):
      ttl_offset = timedelta(hours=1) 
    else:
      model['errors'] = ['ttl_blank']

    if user_handle == None or len(user_handle) < 1:
      model['errors'] = ['user_handle_blank']

    if message == None or len(message) < 1:
      model['errors'] = ['message_blank'] 
    elif len(message) > 280:
      model['errors'] = ['message_exceed_max_chars'] 

    if model['errors']:
      model['data'] = {
        'handle':  user_handle,
        'message': message
      }   
    else:
      expires_at = (now + ttl_offset)
      uuid = CreateActivity.create_activity(user_handle,message,expires_at)

      object_json = CreateActivity.query_object_activity(uuid)
      model['data'] = object_json
    return model

  def create_activity(handle, message, expires_at):
    sql = db.template('activities','create')
    uuid = db.query_commit(sql,{
      'handle': handle,
      'message': message,
      'expires_at': expires_at
    })
    return uuid
    
  def query_object_activity(uuid):
    sql = db.template('activities','object')
    return db.query_object_json(sql,{
      'uuid': uuid
    })
```

- We will can move the SQL used in the above codes to a separate location in the [db/sql/activities](../backend-flask/db/sql/activities) directory. Add the following SQL files:

a. create.sql
```py
INSERT INTO public.activities (
  user_uuid,
  message,
  expires_at
)
VALUES (
  (SELECT uuid 
    FROM public.users 
    WHERE users.handle = %(handle)s
    LIMIT 1
  ),
  %(message)s,
  %(expires_at)s
) RETURNING uuid;
```

b. home.sql
```py
SELECT
  activities.uuid,
  users.display_name,
  users.handle,
  activities.message,
  activities.replies_count,
  activities.reposts_count,
  activities.likes_count,
  activities.reply_to_activity_uuid,
  activities.expires_at,
  activities.created_at
FROM public.activities
LEFT JOIN public.users ON users.uuid = activities.user_uuid
ORDER BY activities.created_at DESC
```
c. object.sql
```py
SELECT
  activities.uuid,
  users.display_name,
  users.handle,
  activities.message,
  activities.created_at,
  activities.expires_at
FROM public.activities
INNER JOIN public.users ON users.uuid = activities.user_uuid 
WHERE 
  activities.uuid = %(uuid)s
```

![user activities](assets/rds-useractivities.png)

### `*NOTE*`

After testing this code, I was getting the NotNullViolation error. I did some research and found that in `app.py` under the `/api/activities` route of ` data_activities()` function I need to change the value of the `user_handle` feed to the actual username of the user I was using.

I also found another solution on the Discord forums (by @anle4s) that avoided this harcoding and ensures that we can create activties without hardcoding the value
of user handle.

![Discord forum](assets/rds-notnullviolation.png)
