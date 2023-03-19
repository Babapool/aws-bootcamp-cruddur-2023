import time
from flask import request
from lib.cognito_jwt_token import CognitoJwtToken, TokenVerifyError

class TokenVerificationMiddleware:
    def __init__(self, app, user_pool_id, user_pool_client_id, region):
        self.app = app
        self.jwt_token = CognitoJwtToken(user_pool_id, user_pool_client_id, region)

    def __call__(self, environ, start_response):
        request_headers = dict(environ)
        access_token = extract_access_token(request_headers)
        try:
            self.jwt_token.verify(access_token)
        except TokenVerifyError as e:
            response = {'message': 'Token verification failed', 'error': str(e)}
            start_response('401 Unauthorized', [('Content-Type', 'application/json')])
            return [json.dumps(response).encode('utf-8')]
        environ['user'] = self.jwt_token.claims
        return self.app(environ, start_response)
