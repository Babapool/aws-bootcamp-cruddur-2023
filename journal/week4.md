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


- To create a scheme for our database, in our `backend-flask/db` directory, we are going to write a `schema.sql` file. To populate the DB with things, add the following:
```SQL
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
````
We use this extension to create UUIDs in Postgres.

- To import this schema to our `cruddur` database, run the following command:
```
psql cruddur < db/schema.sql -h localhost -U postgres
```

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

- To run/implement this, we need to our our `db-schema-load` script

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
