import json
from datetime import datetime, timedelta

from fastapi import HTTPException, Depends, Header, Request
from jose import jwt
from typing import Optional
import os
from fastapi.security import OAuth2PasswordBearer

from models import User

SECRET_KEY = os.environ.get("SECRET_KEY", "")  # 生產環境中應該使用更安全的方式生成和存儲密鑰
ALGORITHM = os.environ.get("ALGORITHM", "")
ACCESS_TOKEN_EXPIRE_HOURS = timedelta(hours=int(os.environ.get('ACCESS_TOKEN_EXPIRE_HOURS', '30')))

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")  # tokenUrl 是获取 token 的路径


def create_access_token(data: dict, expires_delta: timedelta):
    to_encode = data.copy()
    expire = datetime.utcnow() + expires_delta
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


def create_refresh_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


def verify_token(token: str, credentials_exception):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        json_data_str: str = payload.get("sub")
        if json_data_str is None:
            raise credentials_exception
        json_data = json.loads(json_data_str)
        return json_data
    except jwt.JWTError:
        raise credentials_exception


def get_current_user(token: str = Depends(oauth2_scheme)) -> User:
    credentials_exception = HTTPException(
        status_code=401,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    josn_data = verify_token(token, credentials_exception)
    return User(**josn_data)


async def get_curl_command(request: Request, authorization: Optional[str] = Header(None)):
    method = request.method
    url = str(request.url)
    headers = request.headers
    body = await request.body()

    # 构造 curl 命令
    curl = f"curl -X {method} '{url}'"
    for key, value in headers.items():
        if key.lower() != 'content-length':  # 排除不必要的头
            curl += f" -H '{key}: {value}'"
    if body:
        curl += f" -d '{body.decode()}'"

    return curl


