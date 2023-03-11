# Week 2 — Distributed Tracing

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


### Creating our custim span/instrumentation and adding attributes
 We will harcode a span in Honeycomb for the Home page. So add the following in our `home_activities`.py file:
 
 1. Acquiring a Tracer
 To create spans, you need to get a Tracer. When you create a Tracer, OpenTelemetry requires you to give it a name as a string. This string is the only required parameter.
 
 ```py
from opentelemetry import trace
tracer = trace.get_tracer("home.activities")
```

1. Creating Spans
Now we have a tracer configured, we can create spans to describe what is happening in your application. For example, this could be a HTTP handler, a long running operation, or a database fetch. Spans are created in a parent-child pattern, so each time you create a new span, the current active span is used as its parent.

```py
with tracer.start_as_current_span("home-activities-mock-data"):
```   
`home-activities-mock-data` is the name of our span.

1. Run our application
To see if our code works, run the `docker compose up` command.

1. Verify our output
You can see Tracer with 2 spans, go and check it out.

The `library.name` tells us which library was used to create our span.

1. Adding Attributes to Spans 
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

We can use another custom query below as shown in the image:

We will also try to see the heatmap of the duration, to see the latency as percieved by the other users. See the below image:

You can see the query output in the following image:

