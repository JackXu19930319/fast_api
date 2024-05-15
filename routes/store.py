from fastapi import APIRouter, Depends
from fastapi.responses import JSONResponse

import connection
import exception_tool
# import exception_tool
from models import User, StoreIn, Store, RemoveOrAddUserInStore, SetUserStore
from token_api import get_current_user, get_curl_command
from tools import inert_error_log

router = APIRouter()


@router.post("/create", description="create store")
async def create_store(form_data: StoreIn, current_user: User = Depends(get_current_user), curl_command: str = Depends(get_curl_command)):
    conn = connection.connect_to_mysql()
    cur = conn.cursor()
    try:
        if current_user.role != "admin":
            return JSONResponse(status_code=400, content={"message": "You are not admin"})
        name = form_data.name
        address = form_data.address
        phone = form_data.phone
        sql = "SELECT id FROM store WHERE name=%s;"
        cur.execute(sql, (name,))
        r = cur.fetchone()
        if r is not None:
            return JSONResponse(status_code=400, content={"message": "store name exists"})
        sql = "INSERT INTO store (name, address, phone) VALUES (%s, %s, %s);"
        cur.execute(sql, (name, address, phone))
        inserted_id = cur.lastrowid
        conn.commit()
        connection.close_connection(conn)
        return JSONResponse(status_code=200, content={"store_id": inserted_id, "name": name, "phone": phone, "address": address})
    except Exception as e:
        lineNum, detail = exception_tool.exception_tool(e)
        msg = f"{detail}, error in line {lineNum}"
        inert_error_log(conn, cur, curl_command, "/store/create", msg)
        return JSONResponse(status_code=400, content={'error': msg})
    finally:
        connection.close_connection(conn)


@router.get("/list", description="get store list")
async def get_store_list(current_user: User = Depends(get_current_user), curl_command: str = Depends(get_curl_command)):
    conn = connection.connect_to_mysql()
    cur = conn.cursor()
    try:
        if current_user.role != "admin":
            return JSONResponse(status_code=400, content={"message": "You are not admin"})
        sql = "SELECT id, name, address, phone FROM store where is_active= %s;"
        cur.execute(sql, (True,))
        rows = cur.fetchall()
        store_list = []
        for row in rows:
            store_id = row[0]
            store_name = row[1]
            store_address = row[2]
            store_phone = row[3]
            sql = "SELECT id FROM users WHERE store_id=%s;"
            cur.execute(sql, (store_id,))
            user_rows = cur.fetchall()
            user_ids = [row[0] for row in user_rows]
            if user_ids:
                placeholders = ', '.join(['%s'] * len(user_ids))
                sql = f"SELECT name, phone, role, is_owner FROM users WHERE id IN ({placeholders});"
                cur.execute(sql, tuple(user_ids))
                users = cur.fetchall()
            else:
                users = []
            user_list = []
            for user_row in users:
                user = User()
                user.user_id = user_row[0]
                user.name = user_row[0]
                user.phone = user_row[1]
                user.role = user_row[2]
                if user_row[3] == 1:
                    user.is_owner = True
                else:
                    user.is_owner = False
                user_list.append(user.dict())
            store = Store()
            store.id = store_id
            store.name = store_name
            store.address = store_address
            store.phone = store_phone
            store.user_list = user_list
            store_list.append(store.dict())
        connection.close_connection(conn)
        return JSONResponse(status_code=200, content={"store_list": store_list})
    except Exception as e:
        lineNum, detail = exception_tool.exception_tool(e)
        msg = f"{detail}, error in line {lineNum}"
        inert_error_log(conn, cur, curl_command, "/store/list", msg)
        return JSONResponse(status_code=400, content={'error': msg})
    finally:
        connection.close_connection(conn)


@router.post("/update", description="update store detail")
async def update_store(form_data: StoreIn, current_user: User = Depends(get_current_user), curl_command: str = Depends(get_curl_command)):
    conn = connection.connect_to_mysql()
    cur = conn.cursor()
    try:
        if current_user.role != "admin":
            return JSONResponse(status_code=400, content={"message": "You are not admin"})
        store_id = form_data.id
        name = form_data.name
        address = form_data.address
        phone = form_data.phone
        sql = "SELECT id FROM store WHERE name=%s;"
        cur.execute(sql, (name,))
        r = cur.fetchone()
        if r is not None and r[0] != store_id:
            return JSONResponse(status_code=400, content={"message": "store name exists"})
        sql = "UPDATE store SET name= %s, address= %s, phone= %s WHERE id=%s;"
        cur.execute(sql, (name, address, phone, store_id))
        conn.commit()
        connection.close_connection(conn)
        return JSONResponse(status_code=200, content={"id": store_id, "name": name, "phone": phone, "address": address})
    except Exception as e:
        lineNum, detail = exception_tool.exception_tool(e)
        msg = f"{detail}, error in line {lineNum}"
        inert_error_log(conn, cur, curl_command, "/store/update", msg)
        return JSONResponse(status_code=400, content={'error': msg})
    finally:
        connection.close_connection(conn)


@router.post("/add_user", description="add users[list] to store")
async def add_user_to_store(form_data: RemoveOrAddUserInStore, current_user: User = Depends(get_current_user), curl_command: str = Depends(get_curl_command)):
    conn = connection.connect_to_mysql()
    cur = conn.cursor()
    try:
        if current_user.role != "admin":
            return JSONResponse(status_code=400, content={"message": "You are not admin"})
        store_id = form_data.store_id
        user_ids = form_data.user_list
        sql = "SELECT id FROM store WHERE id=%s;"
        cur.execute(sql, (store_id,))
        r = cur.fetchone()
        if r is None:
            return JSONResponse(status_code=400, content={"message": "store not exists"})
        for user_id in user_ids:
            sql = "SELECT id FROM users WHERE id=%s;"
            cur.execute(sql, (user_id,))
            r = cur.fetchone()
            if r is None:
                return JSONResponse(status_code=400, content={"message": "user not exists"})
            sql = "SELECT * FROM users WHERE id=%s AND store_id=%s;"
            cur.execute(sql, (user_id, store_id))
            r = cur.fetchone()
            if r is not None:
                continue
                # return JSONResponse(status_code=400, content={"message": "user already in store"})
            sql = "update users set store_id= %s where id= %s;"
            cur.execute(sql, (store_id, user_id))
        conn.commit()
        connection.close_connection(conn)
        return JSONResponse(status_code=200, content={"message": "add user to store"})
    except Exception as e:
        lineNum, detail = exception_tool.exception_tool(e)
        msg = f"{detail}, error in line {lineNum}"
        inert_error_log(conn, cur, curl_command, "/store/add_user", msg)
        return JSONResponse(status_code=400, content={'error': msg})
    finally:
        connection.close_connection(conn)


@router.post("/remove_user", description="remove users[list] from store")
async def remove_user_from_store(form_data: RemoveOrAddUserInStore, current_user: User = Depends(get_current_user), curl_command: str = Depends(get_curl_command)):
    conn = connection.connect_to_mysql()
    cur = conn.cursor()
    try:
        if current_user.role != "admin":
            return JSONResponse(status_code=400, content={"message": "You are not admin"})
        store_id = form_data.store_id
        user_ids = form_data.user_list
        sql = "SELECT id FROM store WHERE id=%s;"
        cur.execute(sql, (store_id,))
        r = cur.fetchone()
        if r is None:
            return JSONResponse(status_code=400, content={"message": "store not exists"})
        for user_id in user_ids:
            sql = "SELECT id FROM users WHERE id=%s;"
            cur.execute(sql, (user_id,))
            r = cur.fetchone()
            if r is None:
                continue
            sql = "update users set store_id= %s, is_owner= %s where id= %s;"
            cur.execute(sql, (None, False, user_id))
        conn.commit()
        connection.close_connection(conn)
        return JSONResponse(status_code=200, content={"message": "remove user from store"})
    except Exception as e:
        lineNum, detail = exception_tool.exception_tool(e)
        msg = f"{detail}, error in line {lineNum}"
        inert_error_log(conn, cur, curl_command, "/store/remove_user", msg)
        return JSONResponse(status_code=400, content={'error': msg})
    finally:
        connection.close_connection(conn)


@router.get("/not_in_store_user", description="取得此加盟店還沒有被加入的user list")
async def get_not_in_store_user(store_id, current_user: User = Depends(get_current_user), curl_command: str = Depends(get_curl_command)):
    conn = connection.connect_to_mysql()
    cur = conn.cursor()
    try:
        if current_user.role != "admin":
            return JSONResponse(status_code=400, content={"message": "You are not admin"})
        sql = "SELECT id FROM store WHERE id=%s;"
        cur.execute(sql, (store_id,))
        r = cur.fetchone()
        if r is None:
            return JSONResponse(status_code=400, content={"message": "store not exists"})
        sql = "SELECT id FROM users WHERE (store_id != %s or store_id IS NULL) and is_active=%s;"
        cur.execute(sql, (store_id, True))
        user_rows = cur.fetchall()
        user_ids = [row[0] for row in user_rows]
        users = None
        if user_ids:
            placeholders = ', '.join(['%s'] * len(user_ids))
            sql = f"SELECT u.id, u.name, u.phone, u.role, s.name, u.is_owner FROM users u left join store s on s.id = u.store_id WHERE u.id IN ({placeholders});"
            cur.execute(sql, tuple(user_ids))
            users = cur.fetchall()
        # else:
        #     sql = "SELECT id, name, phone, role FROM users where is_active= %s;"
        #     cur.execute(sql, (True,))
        #     users = cur.fetchall()
        user_list = []
        if users is None:
            return JSONResponse(status_code=200, content={"user_list": user_list})
        for user_row in users:
            user = User()
            user.user_id = user_row[0]
            user.name = user_row[1]
            user.phone = user_row[2]
            user.role = user_row[3]
            user.store_name = user_row[4]
            if user_row[5] == 1:
                user.is_owner = True
            else:
                user.is_owner = False
            user_list.append(user.dict())
        connection.close_connection(conn)
        return JSONResponse(status_code=200, content={"user_list": user_list})
    except Exception as e:
        lineNum, detail = exception_tool.exception_tool(e)
        msg = f"{detail}, error in line {lineNum}"
        inert_error_log(conn, cur, curl_command, "/store/not_in_store_user", msg)
        return JSONResponse(status_code=400, content={'error': msg})
    finally:
        connection.close_connection(conn)


@router.get("/store_user_list", description="取得此加盟店的user list")
async def get_store_user_list(store_id, current_user: User = Depends(get_current_user), curl_command: str = Depends(get_curl_command)):
    conn = connection.connect_to_mysql()
    cur = conn.cursor()
    try:
        if current_user.role != "admin":
            return JSONResponse(status_code=400, content={"message": "You are not admin"})
        sql = "SELECT id, name, phone, role, is_owner FROM users WHERE store_id= %s;"
        cur.execute(sql, (store_id,))
        users = cur.fetchall()
        user_list = []
        for user_row in users:
            user = User()
            user.user_id = user_row[0]
            user.name = user_row[1]
            user.phone = user_row[2]
            user.role = user_row[3]
            if user_row[4] == 1:
                user.is_owner = True
            else:
                user.is_owner = False
            user_list.append(user.dict())
        connection.close_connection(conn)
        return JSONResponse(status_code=200, content={"user_list": user_list})
    except Exception as e:
        lineNum, detail = exception_tool.exception_tool(e)
        msg = f"{detail}, error in line {lineNum}"
        inert_error_log(conn, cur, curl_command, "/store/store_user_list", msg)
        return JSONResponse(status_code=400, content={'error': msg})
    finally:
        connection.close_connection(conn)


@router.post("/set_store_owner", description="設定加盟店店長, role需為[store_user]")
async def set_store_owner(form_data: SetUserStore, current_user: User = Depends(get_current_user), curl_command: str = Depends(get_curl_command)):
    conn = connection.connect_to_mysql()
    cur = conn.cursor()
    try:
        store_id = form_data.store_id
        user_id = form_data.user_id
        is_set = form_data.is_set
        if current_user.role != "admin":
            return JSONResponse(status_code=400, content={"message": "You are not admin"})
        sql = "SELECT id FROM store WHERE id=%s;"
        cur.execute(sql, (store_id,))
        r = cur.fetchone()
        if r is None:
            return JSONResponse(status_code=400, content={"message": "store not exists"})
        sql = "SELECT id, role FROM users WHERE id=%s;"
        cur.execute(sql, (user_id,))
        r = cur.fetchone()
        user_role = r[1]
        if r is None:
            return JSONResponse(status_code=400, content={"message": "user not exists"})
        if user_role != "store_user":
            return JSONResponse(status_code=400, content={"message": "user role not store_user"})
        sql = "select * from users where store_id= %s and id= %s;"
        cur.execute(sql, (store_id, user_id))
        r = cur.fetchone()
        if r is None:
            return JSONResponse(status_code=400, content={"message": "user not in store"})
        # sql = "select id from users where store_id= %s and is_owner=1;"
        # cur.execute(sql, (store_id,))
        # r = cur.fetchone()
        # old_owner_id = r[0] if r is not None else None
        # if old_owner_id == user_id:
        #     return JSONResponse(status_code=400, content={"message": "user is already store owner"})
        # if old_owner_id is not None:
        #     sql = "update users set is_owner= where id= %s;"
        #     cur.execute(sql, (old_owner_id,))
        sql = "update users set is_owner= %s where id= %s;"
        cur.execute(sql, (is_set, user_id,))
        conn.commit()
        return JSONResponse(status_code=200, content={"message": f"set store owner{' success' if is_set else ' cancel'}"})
    except Exception as e:
        lineNum, detail = exception_tool.exception_tool(e)
        msg = f"{detail}, error in line {lineNum}"
        inert_error_log(conn, cur, curl_command, "/store/set_store_owner", msg)
        return JSONResponse(status_code=400, content={'error': msg})
    finally:
        connection.close_connection(conn)


@router.post("/del", description="delete store")
async def del_store(store_id, current_user: User = Depends(get_current_user), curl_command: str = Depends(get_curl_command)):
    conn = connection.connect_to_mysql()
    cur = conn.cursor()
    try:
        sql = "SELECT id FROM store WHERE id=%s;"
        cur.execute(sql, (store_id,))
        r = cur.fetchone()
        if r is None:
            return JSONResponse(status_code=400, content={"message": "store not exists"})
        sql = "update users set store_id= %s, is_owner= %s where store_id= %s;"
        cur.execute(sql, (None, False, store_id))
        sql = "update store set is_active= %s where id= %s;"
        cur.execute(sql, (False, store_id))
        conn.commit()
        return JSONResponse(status_code=200, content={"message": "delete store"})
    except Exception as e:
        lineNum, detail = exception_tool.exception_tool(e)
        msg = f"{detail}, error in line {lineNum}"
        inert_error_log(conn, cur, curl_command, "/store/del", msg)
        return JSONResponse(status_code=400, content={'error': msg})
    finally:
        connection.close_connection(conn)
