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

There are many situations where we need to use multiple containers at the same. It is not feasible to manually run the `docker run` command multiple. We can write a `docker-compose.yml` file. This file provides instructions to Docker on how to manage our many containers simultaneoulsy. In the root directory of the project, we are going to add this file:

```YAML
version: "3.8"
services:
  backend-flask:
    environment:
      FRONTEND_URL: "https://3000-${GITPOD_WORKSPACE_ID}.${GITPOD_WORKSPACE_CLUSTER_HOST}"
      BACKEND_URL: "https://4567-${GITPOD_WORKSPACE_ID}.${GITPOD_WORKSPACE_CLUSTER_HOST}"
    build: ./backend-flask
    ports:
      - "4567:4567"
    volumes:
      - ./backend-flask:/backend-flask
  frontend-react-js:
    environment:
      REACT_APP_BACKEND_URL: "https://4567-${GITPOD_WORKSPACE_ID}.${GITPOD_WORKSPACE_CLUSTER_HOST}"
    build: ./frontend-react-js
    ports:
      - "3000:3000"
    volumes:
      - ./frontend-react-js:/frontend-react-js

# the name flag is a hack to change the default prepend folder
# name when outputting the image names
networks: 
  internal-network:
    driver: bridge
    name: cruddur
```

- The `build` parameter states which Dockerfile we want to build. Alternatively use the `image` parameter to specify the image you want to use.
- The `ports` parameter states which ports needed to be mapped from the container to the host.
- The `volumes` parameter states how we want to want the persistent storage for our containers.
- The `environment` parameter is used to provide any environment variables.

To run the `docker-compose.yml` file, run:
```
docker compose up
```

To stop the `docker-compose.yml` file, run:
```
docker compose down
```
#### Note : For creating the Notification Endpoint in both the frontend and backend we will need to explore the code and to understand it.

### Write Notification Endpoint for Flask backend

Perform `docker compose up` command.

Move into the `/backend-flask` directory.

First we are going to add the notification endpoint by adding the API notation using Open API. Here we specify the actions the `api/activities/notifications` will perform. In the `backend-flask/openapi-3.0yml` file:
```YAML
/api/activities/notifications:
    get:
      description: 'Return a feed of activities for all those the user follows'
      tags:
       - activities
      parameters: []
      responses:
        '200':
          description: 'Returns an array of activities'
          content:
           application/json:
            schema:
             type: array
             items:
              $ref: '#/components/schemas/Activity'
```
 We now will make the neccessary changes in our backend code base. We first need to create `notification_activities` service and then create an API route for this API in the `app.py` file. You can view the changes done in the code base [here](https://github.com/Babapool/aws-bootcamp-cruddur-2023/commit/d2e2380f8758f82895f8cef8276ff25dbc302a2e).
 
 Refresh the application and ahead to the `/api/activities/notifications` URL can you will see results we had added in the `notifications_activities.py` file.
 
 ### Write Notification Endpoint for React Frontend
  
 We need to first need to create a [`NotificationsFeedPage.js`](https://github.com/Babapool/aws-bootcamp-cruddur-2023/blob/week-1/frontend-react-js/src/pages/NotificationsFeedPage.js) file in the `pages` component. The `pages` is in the directory `/frontend-react-js/src/pages`.
 
 After we made our changes in the `Pages` component we will head to the [`App.js`](https://github.com/Babapool/aws-bootcamp-cruddur-2023/blob/week-1/frontend-react-js/src/App.js) and do the neccessary changes. We will first import the file we had just created by using:
 
 ```JS
 import NotificationsFeedPage from './pages/NotificationsFeedPage';
```
 We now have to make the following changes in the `createBrowserRouter` function:
 ```JS
 {
    path: "/notifications",
    element: <NotificationsFeedPage />
  },
  ```
  
  This means whenever in the frontend we will provide the URL `/notifications` we should be redirected towards the `NotificationFeedPage` element.
 
