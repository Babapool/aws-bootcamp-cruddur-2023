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

- To create a scheme for Postgres, we need to launch the Postgres DB. To do this we need to run the `postgres` service we have in our `docker-compose.yml`. To run this 
container, we need to use the `docker compose up`.

- To connect to our Postgres (psql) , we are going to use the psql client CLI. Rin the following command:
```
psql -U postgres --host localhost
```
The password to connect is `password`.

- To create a DB using the psql client, run the following command:
a. 
```
gp env CONNECTION_URL = "postgresql://postgres:password@localhODt:5433/cruddur"
```
b.
```
gp env PROD_CONNECTION_URL="postgresql://<RDS masterusername><RD password>@Endpint of DB

CREATE database cruddur;
```
- Run `\l` to check that the DB is created

- Set the follwowing as environmentsl

- To create a scheme for our database, in our `backend-flask directory, we are going to write a `schema.sql` file (Its local should be inside a `db` directory in the `backend-flask`).

### Bash scripting for common database actions
