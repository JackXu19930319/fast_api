import json
from typing import Optional

from fastapi import APIRouter, Depends, Request
from fastapi.responses import JSONResponse
from pydantic import Field

from security import verify_password, get_password_hash
from token_api import create_access_token, create_refresh_token, ACCESS_TOKEN_EXPIRE_HOURS, get_current_user
from jose import JWTError, jwt
from models import User, UserIn, UserOut, UserInDB, RegisterUser, UserUpdate
import connection
import os

router = APIRouter()


@router.post("/token")
async def login_for_access_token(form_data: UserIn):
    conn = connection.connect_to_mysql()
    cur = conn.cursor()
    sql = "SELECT password, name, role, phone, id FROM users where phone=%s;"
    cur.execute(sql, (form_data.phone,))
    r = cur.fetchone()
    if r is None:
        return JSONResponse(status_code=400, content={"message": "Incorrect phone or password"})
    name = r[1]
    role = r[2]
    phone = r[3]
    user_id = r[4]
    connection.close_connection(conn)
    if not verify_password(form_data.password, r[0]):
        return JSONResponse(status_code=400, content={"message": "Incorrect phone or password"})
    sub_data = {}
    sub_data["phone"] = form_data.phone
    sub_data["name"] = name
    sub_data["role"] = role
    sub_data["user_id"] = user_id
    sub_data = json.dumps(sub_data)
    access_token = create_access_token(data={"sub": sub_data}, expires_delta=ACCESS_TOKEN_EXPIRE_HOURS)
    refresh_token = create_refresh_token(data={"sub": sub_data})
    return JSONResponse(status_code=200, content={"access_token": access_token, "name": name, "role": role, "phone": phone, "user_id": user_id, "token_type": "bearer", "refresh_token": refresh_token})


@router.post("/refresh")
async def refresh_access_token(request: Request):
    refresh_token = request.headers.get('referer', None)
    SECRET_KEY = os.environ.get("SECRET_KEY", "")  # 生產環境中應該使用更安全的方式生成和存儲密鑰
    ALGORITHM = os.environ.get("ALGORITHM", "")
    try:
        payload = jwt.decode(refresh_token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            return JSONResponse(status_code=400, content={"message": "Invalid token"})
        new_access_token = create_access_token(data={"sub": username}, expires_delta=ACCESS_TOKEN_EXPIRE_HOURS)
        return JSONResponse(status_code=200, content={"access_token": new_access_token, "token_type": "bearer"})
    except JWTError:
        return JSONResponse(status_code=400, content={"message": "Invalid token"})


@router.post("/register", description="admin can add user(store_id is optional)")
async def register_user(form_data: RegisterUser, current_user: User = Depends(get_current_user)):
    if current_user.role != 'admin':
        return JSONResponse(status_code=403, content={"message": "You don't have permission to register a user"})
    role = form_data.role
    name = form_data.name
    phone = form_data.phone
    store_id = form_data.store_id
    password = phone  # 預設密碼與手機相同
    conn = connection.connect_to_mysql()
    cur = conn.cursor()
    sql = "SELECT * FROM users where phone=%s;"
    cur.execute(sql, (phone,))
    r = cur.fetchone()
    if r is not None:
        return JSONResponse(status_code=400, content={"message": "The user already exists"})
    account_pwd_hash = get_password_hash(password)
    sql = "INSERT INTO users (phone, password, role, name, store_id) VALUES (%s, %s, %s, %s, %s);"
    cur.execute(sql, (phone, account_pwd_hash, role, name, store_id))
    last_id = cur.lastrowid
    conn.commit()
    connection.close_connection(conn)
    return JSONResponse(status_code=200, content={"user_id": last_id, "name": name, "role": role, "phone": phone})


@router.get("/list", description="get user list")
async def get_user_list(current_user: User = Depends(get_current_user)):
    if current_user.role != 'admin':
        return JSONResponse(status_code=403, content={"message": "You don't have permission to get user list"})
    conn = connection.connect_to_mysql()
    cur = conn.cursor()
    sql = "SELECT users.phone, role, users.name, users.id, is_owner, s.name FROM users left join store s on s.id = users.store_id where users.is_active = TRUE;"
    cur.execute(sql)
    r = cur.fetchall()
    connection.close_connection(conn)
    user_list = []
    for i in r:
        user = User()
        user.phone = i[0]
        user.role = i[1]
        user.name = i[2]
        user.user_id = i[3]
        user.is_owner = i[4]
        user.store_name = i[5]
        user_list.append(user.dict())
    return JSONResponse(status_code=200, content={"user_list": user_list})


@router.post("/update", description="update user detail")
async def update_user(form_data: UserUpdate, current_user: User = Depends(get_current_user)):
    if current_user.role != 'admin':
        return JSONResponse(status_code=403, content={"message": "You don't have permission to update user"})
    token_user_id = current_user.user_id
    if token_user_id == form_data.user_id:
        role = current_user.role
    else:
        role = form_data.role
    id = form_data.user_id
    name = form_data.name
    store_id = form_data.store_id
    password = form_data.password
    conn = connection.connect_to_mysql()
    cur = conn.cursor()
    if password is not None:
        password = get_password_hash(password)
        sql = "UPDATE users SET role= %s, name= %s, store_id= %s, password= %s WHERE id=%s;"
        cur.execute(sql, (role, name, store_id, password, id))
        conn.commit()
        connection.close_connection(conn)
        return JSONResponse(status_code=200, content={"user_id": id, "role": role, "name": name, "store_id": store_id})
    sql = "UPDATE users SET role= %s, name= %s, store_id= %s WHERE id=%s;"
    cur.execute(sql, (role, name, store_id, id))
    conn.commit()
    connection.close_connection(conn)
    return JSONResponse(status_code=200, content={"user_id": id, "role": role, "name": name, "store_id": store_id})


@router.post("/del", description="delete user")
async def del_user(user_id, current_user: User = Depends(get_current_user)):
    if current_user.role != "admin":
        return JSONResponse(status_code=400, content={"message": "You are not admin"})
    conn = connection.connect_to_mysql()
    cur = conn.cursor()
    token_user_id = current_user.user_id
    if token_user_id == user_id:
        return JSONResponse(status_code=400, content={"message": "You can't delete yourself"})
    sql = "update users set is_active= %s, is_owner= %s, store_id= %s where id= %s;"
    cur.execute(sql, (False, False, None, user_id))
    conn.commit()
    return JSONResponse(status_code=200, content={"message": "delete user"})
