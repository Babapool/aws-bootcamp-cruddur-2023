# Week 3 — Decentralized Authentication

## Required Homework

### Setting Up Cognito User Pool

AWS Cognito has 2 main parts: User pool and Indentity pool. 
- User pools are user directories that provide sign-up and sign-in options for your app users. 
- Identity pools enable you to grant your users access to other AWS services.

To create a User pool, go the the Cognito service page on the AWS Console. Select `User Pools` option and choose `Create user pool`.



### Implement Custom Signin Page

- To create our Custom Sigin page in our front end using AWS Cognito we need to install the `AWS Amplify` library. To install run the following command in the `frontend-react` directory:
```
npm i aws-amplify --save
```
- Add the following code to our `App.js` file:
```JS
import { Amplify } from 'aws-amplify';

Amplify.configure({
  "AWS_PROJECT_REGION": process.env.REACT_AWS_PROJECT_REGION,
  "aws_cognito_region": process.env.REACT_APP_AWS_COGNITO_REGION,
  "aws_user_pools_id": process.env.REACT_APP_AWS_USER_POOLS_ID,
  "aws_user_pools_web_client_id": process.env.REACT_APP_CLIENT_ID,
  "oauth": {},
  Auth: {
    // We are not using an Identity Pool
    // identityPoolId: process.env.REACT_APP_IDENTITY_POOL_ID, // REQUIRED - Amazon Cognito Identity Pool ID
    region: process.env.REACT_APP_AWS_PROJECT_REGION,           // REQUIRED - Amazon Cognito Region
    userPoolId: process.env.REACT_APP_AWS_USER_POOLS_ID,         // OPTIONAL - Amazon Cognito User Pool ID
    userPoolWebClientId: process.env.REACT_APP_CLIENT_ID,   // OPTIONAL - Amazon Cognito Web Client ID (26-char alphanumeric string)
  }
});
```
- Add the following envars in the `envrionment` section of the `frontend-react-js` service in our `docker-compose.yml` file:
```YAML 
  ....
    REACT_APP_AWS_PROJECT_REGION: "${AWS_DEFAULT_REGION}"
    REACT_APP_AWS_COGNITO_REGION: "${AWS_DEFAULT_REGION}"
    REACT_APP_AWS_USER_POOLS_ID: "<Your User Pool ID>"
    REACT_APP_CLIENT_ID: "<Your Client ID>"   #Inside our User pool choose `App integration` and scroll down to find `App client list`
  ...   
  
```
- To test our code, we will want to conditionally show components based on logged in or logged out. To do this add the following to the `HomeFeed.js` file:
```JS
import { Auth } from 'aws-amplify';

...
// Replace Line 40-49 with this piece of code:
// check if we are authenicated
const checkAuth = async () => {
  Auth.currentAuthenticatedUser({
    // Optional, By default is false. 
    // If set to true, this call will send a 
    // request to Cognito to get the latest user data
    bypassCache: false 
  })
  .then((user) => {
    console.log('user',user);
    return Auth.currentAuthenticatedUser()
  }).then((cognito_user) => {
      setUser({
        display_name: cognito_user.attributes.name,
        handle: cognito_user.attributes.preferred_username
      })
  })
  .catch((err) => console.log(err));
};
...

```
- Update the `ProfileInfo.js` file to include the following:
```JS
import { Auth } from 'aws-amplify';
....

const signOut = async () => {
  try {
      await Auth.signOut({ global: true });
      window.location.href = "/"
  } catch (error) {
      console.log('error signing out: ', error);
  }
}
....
```

- Let us now modify our `SigninPage.js` file:
```JS
import { Auth } from 'aws-amplify';
....

const [cognitoErrors, setCognitoErrors] = React.useState('');

const onsubmit = async (event) => {
   event.preventDefault();
      Auth.signIn(email, password)
        .then(user => {
          localStorage.setItem("access_token", user.signInUserSession.accessToken.jwtToken)
          window.location.href = "/"
        })
        .catch(error => { 
          if (error.code == 'UserNotConfirmedException') {
            window.location.href = "/confirm"
          }
          setErrors(error.message)
         });
         
```

- Let us create a random user to test whether or session is working or not. Go to the `User` section in our User pool and choose `Create User`. After you create the user, confrim the user. To confirm the user run the following command:
```
aws cognito-idp admin-set-user-password --user-pool-id <your user-pool-id> --username <your username> --password <your password> --permanent
```

Now sign in using these credentials to verify whether we are able to login or not.


### Implement Custom Signup Page

- In the `SignupPage.js` add the following changes:
```JS
import { Auth } from 'aws-amplify';
...
const onsubmit = async (event) => {
  event.preventDefault();
  setErrors('')
  try {
      const { user } = await Auth.signUp({
        username: email,
        password: password,
        attributes: {
            name: name,
            email: email,
            preferred_username: username,
        },
        autoSignIn: { // optional - enables auto sign in after user is confirmed
            enabled: true,
        }
      });
      console.log(user);
      window.location.href = `/confirm?email=${email}`
  } catch (error) {
      console.log(error);
      setErrors(error.message)
  }
  return false
}
```

### Implementing Custom Confirmation Page

- Add the following modifications to `ConfirmationPage.js`:
```JS
import { Auth } from 'aws-amplify';
....

const resend_code = async (event) => {
  setErrors('')
  try {
    await Auth.resendSignUp(email);
    console.log('code resent successfully');
    setCodeSent(true)
  } catch (err) {
    // does not return a code
    // does cognito always return english
    // for this to be an okay match?
    console.log(err)
    if (err.message == 'Username cannot be empty'){
      setErrors("You need to provide an email in order to send Resend Activiation Code")   
    } else if (err.message == "Username/client id combination not found."){
      setErrors("Email is invalid or cannot be found.")   
    }
  }
}

const onsubmit = async (event) => {
  event.preventDefault();
  setErrors('')
  try {
    await Auth.confirmSignUp(email, code);
    window.location.href = "/"
  } catch (error) {
    setErrors(error.message)
  }
  return false
}
```
### Implementing Custom Recovery Page

- To implement a custom Recovery page, do the following changes in our `RecoveryPage.js` file:
```JS
import { Auth } from 'aws-amplify';
...

const onsubmit_send_code = async (event) => {
  event.preventDefault();
  setErrors('')
  Auth.forgotPassword(username)
  .then((data) => setFormState('confirm_code') )
  .catch((err) => setErrors(err.message) );
  return false
}
```

### Verifying JWT tokens on server side

We want to send the a JWT token to the backend server, verify it and render a provide a different Home page based on the outcome of the verification and authentication of the token.

- While sending an API call from the frontend to the backend, we need to ensure that the JWT token is also sent so that our request can be verifed in the backend. 
To add the JWT token as part of the request header when a API call is sent do the following changes in `pages/HomeFeedPage.js` file:
```JS
const loadData = async () => {
    try {
      const backend_url = `${process.env.REACT_APP_BACKEND_URL}/api/activities/home`
      const res = await fetch(backend_url, {
        headers: {
          Authorization: `Bearer ${localStorage.getItem("access_token")}` //Adds the token as part of the request header
        },
        method: "GET"
      });
```

- To verify the the token received, we will add a external library as a requirement we need to install. In our `requirements.txt` add the following requirement:
 ```
Flask-AWSCognito
```
Then run the `pip install -r requirements.txt` command

- We want to now verify the JWT token recieved through Cognito. For this we are going to create a new `lib` directory. Within this library we will code a module that will be used in verifying the token. Create a `cognito_jwt_token.py`. You can view the contents of [cognito_jwt_token.py](backend-flask/lib/cognito_jwt_token.py] here.

- In the `app.py` we will add the following modifications to CORS intialization so that communication is not aborted due to a CORS errors:
```py
cors = CORS(
  app, 
  resources={r"/api/*": {"origins": origins}},
  expose_headers="location,link",
  allow_headers="content-type,if-modified-since",
  headers=['Content-Type', 'Authorization'], 
  expose_headers='Authorization',
  methods="OPTIONS,GET,HEAD,POST"
)
```
- In the `app.py` file, a object of type CognitoJwtToken is imported and initialized by adding the following in our code:
```py
import sys
...

from lib.cognito_jwt_token import CognitoJwtToken, extract_access_token, TokenVerifyError
...

cors = CORS(
  app, 
  resources={r"/api/*": {"origins": origins}},
  headers=['Content-Type', 'Authorization'], 
  expose_headers='Authorization',
  methods="OPTIONS,GET,HEAD,POST"
)
...

```

- In the same file we want to modify the `data_home()` method as as well. Do the following changes:
```py
def data_home():
  access_token = extract_access_token(request.headers)
  try:
    claims = cognito_jwt_token.verify(access_token)
    # authenicatied request
    app.logger.debug("authenicated")
    app.logger.debug(claims)
    app.logger.debug(claims['username'])
    data = HomeActivities.run(cognito_user_id=claims['username'])
  except TokenVerifyError as e:
    # unauthenicatied request
    app.logger.debug(e)
    app.logger.debug("unauthenicated")
    data = HomeActivities.run()
  return data, 200
```
logger is used to see if a after the token is send is the user request authenticated or not.

- In the `home_activities.py` file we will modify to add another user entry that can only be viewed if the user is authentication and logged in. Do the following changes:
```py
class HomeActivities:
  def run(cognito_user_id=None): #adding user
    .....

      if cognito_user_id != None:
        extra_crud = {
          'uuid': '248959df-3079-4947-b847-9e0892d1bab4',
          'handle':  'Kick Buttowksi',
          'message': 'Cloud bootcamp here I come!',
          'created_at': (now - timedelta(hours=1)).isoformat(),
          'expires_at': (now + timedelta(hours=12)).isoformat(),
          'likes': 1042,
          'replies': []
        }
        results.insert(0,extra_crud)
        
     span.set_attribute("app.result_length", len(results))
     return results
```

- Add the following environment variables to the `backend-flask` service in our `docker-compose.yml` file:
```YAML
services:
  backend-flask:
    environment:
      ....
      AWS_COGNITO_USER_POOL_ID: "<Add your user pool ID>"
      AWS_COGNITO_USER_POOL_CLIENT_ID: "<Add your client ID>"
      ....
```

- After the user signs out we want to remove the token which is stored in our local storage. To do this we will make the following modification to 
signOut method in `components/ProfileInfo.js` file:
```JS
const signOut = async () => {
    try {
        await Auth.signOut({ global: true });
        window.location.href = "/"
        localStorage.removeItem("access_token") //Remove the token when the user logs out
    } catch (error) {
        console.log('error signing out: ', error);
    }
  }
```  
