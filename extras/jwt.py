import jwt
import os

def JwtSign(content):
    secret_key = os.getenv('JWT_SECRET')
    token = jwt.encode(content, secret_key, algorithm="HS256")
    return token

def JwtVerify(token):
    secret_key = os.getenv('JWT_SECRET')
    try:
        user = jwt.decode(token, secret_key, algorithms=['HS256'])
        return {'user': user}
    except Exception as error:
        return None