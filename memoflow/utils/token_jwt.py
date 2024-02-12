import jwt
import datetime
import secrets
import json
from functools import wraps
from webob.exc import HTTPUnauthorized
from webob import Request 


class TokenManager:
    secret_key = secrets.token_urlsafe(32)  # 类属性

    @classmethod
    def generate_token(cls, user_id):
        expiration_time = datetime.datetime.utcnow() + datetime.timedelta(hours=1)
        token = jwt.encode({"user_id": user_id, "exp": expiration_time}, cls.secret_key, algorithm="HS256")
        return token

    @classmethod
    def verify_token(cls, token):
        try:
            decoded_data = jwt.decode(token, cls.secret_key, algorithms=["HS256"])
            return decoded_data
        except jwt.ExpiredSignatureError:
            return None
        except jwt.InvalidTokenError:
            return None


def token_required(func):
    @wraps(func)
    def decorated_func(*args, **kwargs):
        if args and isinstance(args[1], Request):
            req = args[1]

        token = req.headers.get('Authorization')

        if not token:
            return HTTPUnauthorized(json.dumps({"error": "Token is missing"}))
        if not token.startswith('Bearer '):
            return HTTPUnauthorized(json.dumps({'error': 'Unauthorized - Invalid token format'}))

        decoded_data = TokenManager.verify_token(token[7:])
        if decoded_data:
            return func(*args, **kwargs)
        else:
            raise HTTPUnauthorized(json.dumps({"error": "Invalid credentials"}))

    return decorated_func


