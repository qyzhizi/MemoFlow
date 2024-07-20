import logging
import jwt
import datetime
import secrets
import json
from functools import wraps
from webob.exc import HTTPUnauthorized
from webob import Request 

from memoflow.conf import CONF
LOG = logging.getLogger(__name__)

class TokenManager:
    secret_key = secrets.token_urlsafe(32)  # 类属性

    @classmethod
    def generate_token(cls, user_id, expiration_time=None):
        if not expiration_time:
            expiration_time = datetime.datetime.utcnow() + datetime.timedelta(hours=24)
        token = jwt.encode({"user_id": user_id, "exp": expiration_time}, cls.secret_key, algorithm="HS256")
        return token
    
    @classmethod
    def invalidate_token(cls, token):
        # 将 token 的过期时间设置为当前时间，使其立即失效
        invalid_token = jwt.decode(token, cls.secret_key, algorithms=["HS256"])
        invalid_token['exp'] = datetime.utcnow()
        return jwt.encode(invalid_token, cls.secret_key, algorithm="HS256")

    @classmethod
    def verify_token(cls, token):
        try:
            decoded_data = jwt.decode(token, cls.secret_key, algorithms=["HS256"])
            return decoded_data
        except jwt.ExpiredSignatureError:
            LOG.error("error: jwt ExpiredSignatureError")
            return None
        except jwt.InvalidTokenError:
            LOG.error("error: jwt InvalidTokenError")
            return None


def token_required(func):
    @wraps(func)
    def decorated_func(*args, **kwargs):
        if args and isinstance(args[1], Request):
            req = args[1]
        else:
            req = kwargs.get('req')

        token = req.headers.get('MemoFlowAuth')
        if not token:
            # Try getting token from cookies if not found in headers
            token = req.cookies.get('MemoFlowAuth')

        if not token:
            LOG.error("error: Token is missing")
            return HTTPUnauthorized(json.dumps({"error": "Token is missing"}))
        if not token.startswith('Bearer '):
            LOG.error("error: Unauthorized - Invalid token format")
            return HTTPUnauthorized(json.dumps({'error': 'Unauthorized - Invalid token format'}))

        decoded_data = TokenManager.verify_token(token[7:])
        if decoded_data:
            req.environ['user_id'] = decoded_data.get('user_id', None)
            return func(*args, **kwargs)
        else:
            LOG.error("error: Invalid credentials")
            return HTTPUnauthorized(json.dumps({"error": "Invalid credentials"}))

    return decorated_func


