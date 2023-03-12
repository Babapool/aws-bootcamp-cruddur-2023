# Week 2 — Distributed Tracing

## Required Homework
## Honeycomb

### Instrument Honeycomb with OTEL

OpenTelemetry (OTel) is an open source observability framework that provides IT teams with standardized protocols and tools for collecting and routing telemetry data.
The OTel Collector is an application that allows you to process that telemetry and send it out to various destinations.

- Let us create an environment in the Honecomb website named `bootcamp`, and then seitch to this environment.

Now export your Honeycomb environment API key in gitpod, using the `gp env` command:
```
gp env HONEYCOMB_API_KEY=" Enter your key here"
```

Export the service name using the `gp env` command. The service name is used to tell Honeycomb which service name we need to use in our spans/
```
gp env HONEYCOMB_SERVICE)NAME="Enter your service name here"
```

- Add the following environment variables in the `backend-flask` service of our `docker-compose.yml`. These variables are used to configure the OTEL to send it to Honeycomb.

```YAML
OTEL_EXPORTER_OTLP_ENDPOINT: "https://api.honeycomb.io"
OTEL_EXPORTER_OTLP_HEADERS: "x-honeycomb-team=${HONEYCOMB_API_KEY}"
OTEL_SERVICE_NAME: "${HONEYCOMB_SERVICE_NAME}"
```
Here, we will for $HONEYCOMB_SERVICE_NAME we will use `backend-flask`.

-  We require these packages to instrument a Flask app with OpenTelemetry. Add them to our `backend-flask/requirements.txt` file and run the `pip install -r requirements.txt` or alternatively you can restart the environment to allow Gitpod to do it for us (based on the changes done in the `gitpod.yml` file):

```
opentelemetry-api
opentelemetry-sdk
opentelemetry-exporter-otlp-proto-http
opentelemetry-instrumentation-flask
opentelemetry-instrumentation-requests
```

- Add the Intializers in our `app.py` file. Add these lines to your existing Flask app initialization file app.py (or similar). These updates will create and initialize a tracer and Flask instrumentation to send data to Honeycomb:

```py
#Honeycomb
from opentelemetry import trace
from opentelemetry.instrumentation.flask import FlaskInstrumentor
from opentelemetry.instrumentation.requests import RequestsInstrumentor
from opentelemetry.exporter.otlp.proto.http.trace_exporter import OTLPSpanExporter
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor
```

```py
#Honeycomb
# Initialize tracing and an exporter that can send data to Honeycomb
provider = TracerProvider()
processor = BatchSpanProcessor(OTLPSpanExporter())
provider.add_span_processor(processor)
trace.set_tracer_provider(provider)
tracer = trace.get_tracer(__name__)
````
`OTLPSpanExporter()` reads the enviornment variables, where to send our configuration spans

Add this following below the `app = Flask(__name__)` line in our file:
```py
#Honeycomb
# Initialize automatic instrumentation with Flask
FlaskInstrumentor().instrument_app(app)
RequestsInstrumentor().instrument()
```

- To see if our code works, run the `docker compose up` command.

![span output](assets/honeycomb-span-output.png)
![Span output](assets/honeycomb-span-ui-output.png)
![Span output](assets/honeycomb-default-span.png)


### Another way to create a different span

We will create a simple span processor and with a console span exporter. Add the following lines to our code:

```py
from opentelemetry.sdk.trace.export import SimpleSpanProcessor, ConsoleSpanExporter
```
```py
# Show is thin logs within the backend-flask as STDOUT
simple_processor= SimpleSpanProcessor(ConsoleSpanExporter())
provider.add_span_processor(simple_processor)
```
Run the `docker compose up` command, to verify our changes.
![deafult](assets/honeycomb-default-span.png)
![default](assets/honeycomb-span-output.png)

### Creating our custom span/instrumentation and adding attributes
 We will harcode a span in Honeycomb for the Home page. So add the following in our `home_activities`.py file:
 
 - Acquiring a Tracer
 To create spans, you need to get a Tracer. When you create a Tracer, OpenTelemetry requires you to give it a name as a string. This string is the only required parameter.
 
 ```py
from opentelemetry import trace
tracer = trace.get_tracer("home.activities")
```

- Creating Spans
Now we have a tracer configured, we can create spans to describe what is happening in your application. For example, this could be a HTTP handler, a long running operation, or a database fetch. Spans are created in a parent-child pattern, so each time you create a new span, the current active span is used as its parent.

```py
with tracer.start_as_current_span("home-activities-mock-data"):
```   
`home-activities-mock-data` is the name of our span.

- Run our application
To see if our code works, run the `docker compose up` command.

- Verify our output
You can see Tracer with 2 spans, go and check it out.

![Custom Span](assets/honeycomb-2span-ui-1.png)
![Span output](assets/honeycomb-ui-query-output1.png)

The `library.name` tells us which library was used to create our span.

- Adding Attributes to Spans 
It is often beneficial to add context to a currently executing span in a trace. For example, you may have an application or service that handles users and you want to associate the user with the span when querying your dataset in Honeycomb. In order to do this, get the current span from the context and set an attribute with `now` variable:

```py
with tracer.start_as_current_span("home-activities-mock-data"):
      span = trace.get_current_span()
      now = datetime.now(timezone.utc).astimezone()
      span.set_attribute("app.now", now.isoformat())
      
......
     span.set_attribute("app.result_length",len(results))
      return results
```

1. Let us verify this using the Query option
In the left hand side of the Honeycomb UI, you can see the `New Query` option. In the visualization field select `Count` and in the Group_By field, select `trace.trace_id`. In the time duration opton above, select, `last 10 minutes`.

- We can use another custom query below as shown in the image:

![Custom Span](assets/honeycomb-2span-ui-2.png)
![Custom Span](assets/honeycomb-2span-ui-3.png)

- We will also try to see the heatmap of the duration, to see the latency as percieved by the other users. See the below image:
![heatMap](assets/honeycomb-ui-query-heatmap.png)

- You can see the query output in the following image:
![query](assets/honeycomb-ui-query.png)
![custom span](assets/honeycomb-ui-query-output2.png)

## AWS X-Ray
AWS X-Ray is a service that collects data about requests that your application serves, and provides tools that you can use to view, filter, and gain insights into that data to identify issues and opportunities for optimization. For any traced request to your application, you can see detailed information not only about the request and response, but also about calls that your application makes to downstream AWS resources, microservices, databases, and web APIs.

AWS X-Ray receives traces from your application, in addition to AWS services your application uses that are already integrated with X-Ray. Instrumenting your application involves sending trace data for incoming and outbound requests and other events within your application, along with metadata about each request.AWS services that are integrated with X-Ray can add tracing headers to incoming requests, send trace data to X-Ray, or run the X-Ray daemon.

Instead of sending trace data directly to X-Ray, each client SDK sends JSON segment documents to a daemon process listening for UDP traffic. The X-Ray daemon buffers segments in a queue and uploads them to X-Ray in batches. 

![XRAY](https://docs.aws.amazon.com/images/xray/latest/devguide/images/architecture-dataflow.png)

X-Ray uses trace data from the AWS resources that power your cloud applications to generate a detailed service map. Use the service map to identify bottlenecks, latency spikes, and other issues to solve to improve the performance of your applications.

- Installing the requirements
Add the following requirements in the `requirements.txt` file to install `aws-xray-sdk`:
```
aws-xray-sdk
```
Run the `pip install -r requirements.txt` to install this requirements.

- Setting up X-Ray Resources

- To setup the sampling rules create a JSON file in `aws/json` directory:
```JSON
{
    "SamplingRule": {
        "RuleName": "backend-flask",
        "ResourceARN": "*",
        "Priority": 9000,
        "FixedRate": 0.1,
        "ReservoirSize": 5,
        "ServiceName": "Cruddur",
        "ServiceType": "*",
        "Host": "*",
        "HTTPMethod": "*",
        "URLPath": "*",
        "Version": 1
    }
  }
```  
- Creating X-Ray groups

To create X-Ray group, run the following command:
```
FLASK_ADDRESS="https://4567-${GITPOD_WORKSPACE_ID}.${GITPOD_WORKSPACE_CLUSTER_HOST}"
aws xray create-group \
   --group-name "Cruddur" \
   --filter-expression "service(\"backend-flask\")"
```
![X-Ray group](assets/xray-group.png)

- To create the sampling rules, run the command:
```
aws xray create-sampling-rule --cli-input-json file://aws/json/xray.json
```
![X-ray sampling rules](assets/xray-samplingrules.png)
![Sampling rules](assets/xray-samplingrules-1.png)


- X-Ray Daemon
The AWS X-Ray daemon is a software application that listens for traffic on UDP port 2000, gathers raw segment data, and relays it to the AWS X-Ray API. The daemon works in conjunction with the AWS X-Ray SDKs and must be running so that data sent by the SDKs can reach the X-Ray service.

We want to install and run the daemon as a container as we want to run the daemon inside the container in the cluster to get the reporting. In the `docker-compose.yml` add the following `xray-daemon` as new service:
```YAML
  xray-daemon:
    image: "amazon/aws-xray-daemon"
    environment:
      AWS_ACCESS_KEY_ID: "${AWS_ACCESS_KEY_ID}"
      AWS_SECRET_ACCESS_KEY: "${AWS_SECRET_ACCESS_KEY}"
      AWS_REGION: "us-east-1"
    command:
      - "xray -o -b xray-daemon:2000"
    ports:
      - 2000:2000/udp
```

- Writing the X-Ray code
- Import and intialize the X-Ray recorder and the middleware by using these lines of code:
```py
# ---X-Ray---
from aws_xray_sdk.core import xray_recorder
from aws_xray_sdk.ext.flask.middleware import XRayMiddleware

xray_url = os.getenv("AWS_XRAY_URL")
#xray_recorder.configure(service='backend-flask', dynamic_naming=xray_url)
xray_recorder.configure(service='backend-flask') # To ensure all traces can be grouped under the Cruudr group created

......
......

app = Flask(__name__)

#---X-Ray----
XRayMiddleware(app, xray_recorder)
```
- Verifying the reports

Run the `docker compose up` command to see the Traces in the AWS Console in the AWS X-Ray service.
![output](assets/xray-trace-output-1.png)

### CloudWatch Logs

- We need to add the `watchtower` dependency into our `requirements.txt` file. Add the following:
```
watchtower
```
Then run ```pip install -r requirements.txt```

- Import watchtower. In our `app.py` add the following lines of code to import watchtower:
```py
import watchtower
import logging
from time import strftime
```

- Before we can use CloudWatch, we need to configure Logger. To configure logger, add the following lines in `app.py`:
```py
# Configuring Logger to Use CloudWatch
LOGGER = logging.getLogger(__name__)
LOGGER.setLevel(logging.DEBUG)
console_handler = logging.StreamHandler()
cw_handler = watchtower.CloudWatchLogHandler(log_group='cruddur')
LOGGER.addHandler(console_handler)
LOGGER.addHandler(cw_handler)
LOGGER.info("Test Log")
```
`cw_handler = watchtower.CloudWatchLogHandler(log_group='cruddur')` will create a Log group called `cruddur` where all our logs will be stored.

- If we want to do some error logging, we can add the following function to our `app.py` file:
```py
@app.after_request
def after_request(response):
    timestamp = strftime('[%Y-%b-%d %H:%M]')
    LOGGER.error('%s %s %s %s %s %s', timestamp, request.remote_addr, request.method, request.scheme, request.full_path, response.status)
    return response
```
- Add the following set of lines to make sure that we able to use the LOGGER for our endpoint:
```
@app.route("/api/activities/home", methods=['GET'])
def data_home():
  data = HomeActivities.run(Logger=LOGGER)
  return data, 200
```

- Set the following environment variables for the `backend-flask` service in the `docker-compose.yml` file. Add the following environment variables:
```YAML
      ....
      AWS_DEFAULT_REGION: "${AWS_DEFAULT_REGION}"
      AWS_ACCESS_KEY_ID: "${AWS_ACCESS_KEY_ID}"
      AWS_SECRET_ACCESS_KEY: "${AWS_SECRET_ACCESS_KEY}"
```      
1.Custom Logging in CloudWatch
- We want to do some custom logging for our `activities_home.py` page. To get some info about the Logger we can add:
```py
...
class HomeActivities:
  def run(logger):

    logger.info("HomeActivities")
....
```

- Start the application using `docker compose up` and go to `cruddur` Log group in AWS Cloudwatch Log Groups to see the results.
![log groups](assets/cloudwatch-log-group.png)
![log](assets/cloudwatch-log-group-output.png)

### Rollbar

- First, log into our Rollbar account. Create a Project called `Cruddur`.
- Create a `New SDK` and choose Flask. In the code snippet shown you will see your access tokens.
![Rollbar flask](assets/rollbar-flask.png)

- In our `requirements.txt` add the following requirements:
```
blinker
rollbar
```
Install the dependencies using:
```
pip install -r requirements.txt
```
- Export your access tokens found in the code snippet, using:
```
gp env ROLLBAR_ACCESS_TOKEN="<Enter your token here">
```
- Also add this as an envrionment variable in the `backend-flask` service in our `docker-compose.yml` file:
```YAML
  ....
  ROLLBAR_ACCESS_TOKEN: "${ROLLBAR_ACCESS_TOKEN}"
  .....
```  
 
- To instrument our code, we will import Rollbar. In our `app.py`, add the following lines of code:
```py
import os
import rollbar
import rollbar.contrib.flask
from flask import got_request_exception
```
- Add the rollbar init code in our file:
```py
app = Flask(__name__)
.....

rollbar_access_token = os.getenv('ROLLBAR_ACCESS_TOKEN')
@app.before_first_request
def init_rollbar():
    """init rollbar module"""
    rollbar.init(
        # access token
        rollbar_access_token,
        # environment name
        'production',
        # server root directory, makes tracebacks prettier
        root=os.path.dirname(os.path.realpath(__file__)),
        # flask already sets up logging
        allow_logging_basic_config=False)

    # send exceptions from `app` to rollbar, using flask's signal system.
    got_request_exception.connect(rollbar.contrib.flask.report_exception, app)
.....

```
- Add the test endpoint to our, to view the traces:
```py
app = Flask(__name__)
.....

@app.route('/rollbar/test')
def rollbar_test():
    rollbar.report_message('Hello World!', 'warning')
    return "Hello World!"
....

```
- Start our application using the `docker compose up` command.
![output](assets/rollbar-op-1.png)
![output](assets/rollbar-op-2.png)

- Let us make an error in our code. We will see the following output:
![error output](assets/rollbar-op-3.png)
![error output](assets/rollbar-op-4.png)

## Homework Challenges

### Create Custom Subsegments in AWS X-Ray

We want to create a custom segement and subsegmenst to see the trace reports according to our needs. For this we are going to create a custom subsegement in the `user_activities.py` file.

- The first step would be to instrument the endpoint. We can instrument the the endpoint by adding `@xray_recorder.capture('user_activities')`  decorator on our Flask function, in our case would be `def data_handle(handle)` handle function. Add the following lines:

```py
@app.route("/api/activities/@<string:handle>", methods=['GET'])
@xray_recorder.capture('user_activities_home')
def data_handle(handle):
```
The `'user_activities_home` is the name of our endpoint. The `capture` method is used to create a custom X-Ray subsgement that is associated with our endpoint function. The parameter passed the name of the endpoint which we going to view while seeing the Traces in the console.

- To create our custom subsegement, we need to do the following changes in the `user_activities.py` file/ The modified content of the file is as follows:
```py
from datetime import datetime, timedelta, timezone
from aws_xray_sdk.core import xray_recorder
class UserActivities:
  def run(user_handle):
    try:
      model = {
        'errors': None,
        'data': None
      }

      now = datetime.now(timezone.utc).astimezone()
      
      if user_handle == None or len(user_handle) < 1:
        model['errors'] = ['blank_user_handle']
      else:
        now = datetime.now()
        results = [{
          'uuid': '248959df-3079-4947-b847-9e0892d1bab4',
          'handle':  'Andrew Brown',
          'message': 'Cloud is fun!',
          'created_at': (now - timedelta(days=1)).isoformat(),
          'expires_at': (now + timedelta(days=31)).isoformat()
        },
        {
          'uuid': '248959df-3079-4947-b847-9e0892c1bab4',
          'handle':  'Kick Buttowksi',
          'message': 'Cloud bootcamp is fun. It makes learning easy!!!',
          'created_at': (now - timedelta(days=1)).isoformat(),
          'expires_at': (now + timedelta(days=31)).isoformat()
        }
        ]
        model['data'] = results
    
    #opening the subsegment
      subsegment = xray_recorder.begin_subsegment('mock-data')
      # ---X-Ray ---
      dict = {
        "now": now.isoformat(),
        "results-size": len(model['data'])
      }
      subsegment.put_metadata('key', dict, 'namespace') #putting data in subsegment
      xray_recorder.end_subsegment()
    finally:  
    #   Closing  the segment
      xray_recorder.end_subsegment()
    return model
```
- Run the `docker compose up` command and verify the Traces in the AWS Console.
![custom](assets/xray-subsegment-op-1.png)
![subsegment](assets/xray-subsegment-op-2.png)
![subsegment](assets/xray-subsegment-op-3.png)
![subsegemt](assets/xray-subsegment-op-3.png)

### Create Custom Sapn for UserID and Query in Honeycomb

We want to capture the UserID by creating a custom span for our `user_activities.py` file. Do the following changes in our `user_activities.py` file:

```py
from datetime import datetime, timedelta, timezone
#--HoneyComb----
from opentelemetry import trace
tracer = trace.get_tracer("user-activities")

class UserActivities:
  def run(user_handle):
    with tracer.start_as_current_span("user-activities"): # starting a custom spam called user-activities
      span = trace.get_current_span()
      #try:
      model = {
        'errors': None,
        'data': None
        }

      now = datetime.now(timezone.utc).astimezone()
      span.set_attribute("user.now", now.isoformat()) #Setting the span attribute

      if user_handle == None or len(user_handle) < 1:
        model['errors'] = ['blank_user_handle']
      else:
        now = datetime.now()
        span.set_attribute("UserID", user_handle)   #Setting UserID as the span attribute
        results = [{
          'uuid': '248959df-3079-4947-b847-9e0892d1bab4',
            'handle':  'Andrew Brown',
            'message': 'Cloud is fun!',
            'created_at': (now - timedelta(days=1)).isoformat(),
            'expires_at': (now + timedelta(days=31)).isoformat()
          },
          {
            'uuid': '248959df-3079-4947-b847-9e0892c1bab4',
            'handle':  'Kick Buttowksi',
            'message': 'Cloud bootcamp is fun. It makes learning easy!!!',
            'created_at': (now - timedelta(days=1)).isoformat(),
            'expires_at': (now + timedelta(days=31)).isoformat()
          }
        ]
        span.set_attribute("user.activities.len", len(results)) # Set the number of active UserIDs as an attribute
        model['data'] = results
        
      return model    #Return the number of UserIDs as output in our query
```
![Custom span](assets/honeycomb-customspan-output.png)
![Custom span](assets/honeycomb-customspan-output1.png)

- Let us create a Custom query for Latency grouped by UserID. Also we crated this query to show the Heatmap of the duration taken to access the user activities service.
![custom query](assets/honeycomb-customquery-output.png)
![Custom query](assets/honeycomb-customquery-output1.png)
