# Week 1 — App Containerization

## Required Homework

### Containerizing Applications

#### 1. Containerizing the Back end

To containerize the back end/flask module of our application, we need to create a Dockerfile and then build it to create a docker image.
In the `backend-flask` directory create a `Dockerfile` and add the following:

```
# We want to the use the 3.10-slim-buster version of python as the base of image of pur container
FROM python:3.10-slim-buster

# In our container a /backend-flask will be created and will set as the present working directory
WORKDIR /backend-flask

# Copy requirements.txt from this repo inside the container 
COPY requirements.txt requirements.txt

# Install the dependencies in the requirements.txt
RUN pip3 install -r requirements.txt

# Copy the current directory from of this repo into the current directory in the container
COPY . .

# Setting the environment variable
ENV FLASK_ENV=development

#Exposing port 4567 in the container for our flask application
EXPOSE ${PORT}

# Run the flask application the way we would run it on our system
CMD [ "python3", "-m" , "flask", "run", "--host=0.0.0.0", "--port=4567"]
```

Now we need to build our Dockerfile. The Dockerfile is basically the set of steps or a recipe on how we want are containers to be made. The building of the Dockerfiles are done in an layered manner. This means if a step fails, it can be restarted from the previous. To build this Dockerfile:

```
docker build -t  backend-flask ./backend-flask
```
After successfull completion an image named `backend-flask`  will be avaialable. 

For our Flask application to run we need to set these environment variables: 
- FRONTEND_URL='*'
- BACKEND_URL='*'

We can pass these environment ariables by ussing the `-e` parameter while using the `docker run` command.

To run our container in the background as a background process, use the following:
```
docker run -d -p 4567:4567 -it -e FRONTEND_URL='*' -e BACKEND_URL='*' backend-flask
```
We use the `-p` parameter to expose the Flask application running at port 4567 in the container at port 4567 in the host.

We can also ensure to run our container temporarily, i.e. after we exit the container, all its log will be deleted, use the `--rm` parameter:
```
docker run -rm -p 4567:4567 -it -e FRONTEND_URL='*' -e BACKEND_URL='*' backend-flask
```
#### 2. Containerizing the Front end

To containerize the front end/react module of our application, we need to create a Dockerfile and then build it to create a docker image.
In the `frontend-react-js` directory create a `Dockerfile` and add the following:

```
FROM node:16.18

ENV PORT=3000

COPY . /frontend-react-js
WORKDIR /frontend-react-js
RUN npm install
EXPOSE ${PORT}
CMD ["npm", "start"]
```

But we to generate the node_modules so that it can be copied into the container. To install the node_modules:
```
cd frontend-react-js
npm i
```

To build this Dockerfile, run:  (We get can image named as `frontend-react-js`)
```
docker build -t frontend-react-js ./frontend-react-js
```
To run this container. run:
 ```
 docker run -p 3000:3000 -d frontend-react-js
 ```
 
#### 3. Create multiple containers simulataneously using Docker compose
