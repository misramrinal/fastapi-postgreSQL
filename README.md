# fastapi-postgreSQL

## A backend database made with PostGRE SQL using FastAPI which can perform basic CRUD operatiions

## Installation
### In order to use this package, go through the following steps:

Open Commant Prompt
```bash
cd fastapi_postgresql
```
After that start the FastAPI by using the following command:
```bash
uvicorn main:app --reload
```
## To run in docker:
### In order to create a container of this in docker:
```bash
docker-compose build
docker-compose up
```

## EndPoints
### In your web browser go to the following IP address:
```bash
127.0.01:5050
```
#### This will open pyadmin4 where you will be able to access the database.
#### Username: admin@admin
#### Password: admin

#### Once the server is open, go to project explorer and under the server tab, create a new server with the following specifications:
#### Name: db
#### Host Name: db
#### Username: postgres
#### Password: password

#### This will create a database server of the name db which can be accesses by out fastAPI endpoints.

#### Now in the browser go the the IP address:
```bash
127.0.0.1:8000/docs
```

#### This will show us the list of all endpoints where we can give any test value and execute. After executing if the response is 200, then the execution is successfull and now we can again go to the database at post 5050 and see the changes in the database

