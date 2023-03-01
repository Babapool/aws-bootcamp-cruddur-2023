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
