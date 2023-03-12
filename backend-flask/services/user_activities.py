from datetime import datetime, timedelta, timezone
#from aws_xray_sdk.core import xray_recorder

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
        
        #subsegment = xray_recorder.begin_subsegment('mock-data') #opening the subsegemnt
        # ---X-Ray ---
        # dict = {
        #   "now": now.isoformat(),
        #   "results-size": len(model['data'])
        # }
        #subsegment.put_metadata('key', dict, 'namespace') #Adding data to subsegement
        #xray_recorder.end_subsegment() 
      #finally:  
      #Closing the segment
      # xray_recorder.end_subsegment()

      return model    