import base64
from typing import Optional

from fastapi import APIRouter, Depends, UploadFile, File, Form
from fastapi.responses import JSONResponse

import connection
import exception_tool
from models import User
from token_api import get_current_user
from tools import inert_error_log, upload_img_execute

router = APIRouter()


@router.post("/create", summary="Create raw material", description="Create raw material", tags=["raw_material"])
async def create(file: Optional[UploadFile] = File(...), price: int = Form(...), name: str = Form(...), unit: str = Form(...), current_user: User = Depends(get_current_user)):
    if current_user.role != "admin":
        return JSONResponse(status_code=400, content={"message": "You are not admin"})
    conn = connection.connect_to_mysql()
    cur = conn.cursor()
    try:
        image_data = await file.read()
        # 转换为 Base64 编码字符串
        image_base64 = base64.b64encode(image_data).decode('utf-8')
        img_link = upload_img_execute(image_base64)
        if img_link is None:
            return JSONResponse(status_code=500, content={"message": "upload image fail"})
        sql = "select * from raw_material where name = %s;"
        cur.execute(sql, (name,))
        result = cur.fetchone()
        if result:
            return JSONResponse(status_code=400, content={"message": "raw material name already exists"})
        sql = "insert into raw_material(name, unit, image, price) values (%s, %s, %s, %s);"
        cur.execute(sql, (name, unit, img_link, price))
        last_id = cur.lastrowid
        conn.commit()
        return JSONResponse(status_code=200, content={"message": "success", "img_link": img_link, "id": last_id})
    except Exception as e:
        lineNum, detail = exception_tool.exception_tool(e)
        msg = f"{detail}, error in line {lineNum}"
        inert_error_log(conn, cur, "", "raw_material/create", msg)
        return JSONResponse(status_code=400, content={'error': msg})


@router.get("/list", summary="Get raw material list", description="Get raw material list", tags=["raw_material"])
async def list(current_user: User = Depends(get_current_user)):
    if current_user.role != "admin":
        return JSONResponse(status_code=400, content={"message": "You are not admin"})
    conn = connection.connect_to_mysql()
    cur = conn.cursor()
    try:
        sql = "select id, name, unit, image, price from raw_material where is_active=%s;"
        cur.execute(sql, (True,))
        result = cur.fetchall()
        data = []
        for item in result:
            data.append({
                "id": item[0],
                "name": item[1],
                "unit": item[2],
                "image": item[3],
                "price": item[4]
            })
        return JSONResponse(status_code=200, content={"message": "success", "data": data})
    except Exception as e:
        lineNum, detail = exception_tool.exception_tool(e)
        msg = f"{detail}, error in line {lineNum}"
        inert_error_log(conn, cur, "", "raw_material/list", msg)
        return JSONResponse(status_code=400, content={'error': msg})


@router.post('/update')
async def update(file: UploadFile = File(None), price: int = Form(...), name: str = Form(...), unit: str = Form(...), id: int = Form(...), current_user: User = Depends(get_current_user)):
    if current_user.role != "admin":
        return JSONResponse(status_code=400, content={"message": "You are not admin"})
    conn = connection.connect_to_mysql()
    cur = conn.cursor()
    try:
        sql = "select * from raw_material where name = %s and id != %s;"
        cur.execute(sql, (name, id))
        result = cur.fetchone()
        if result:
            return JSONResponse(status_code=400, content={"message": "raw material name already exists"})
        sql = "select image from raw_material where id = %s;"
        cur.execute(sql, (id,))
        result = cur.fetchone()
        img_link = result[0]
        if file:
            image_data = await file.read()
            # 转换为 Base64 编码字符串
            image_base64 = base64.b64encode(image_data).decode('utf-8')
            img_link = upload_img_execute(image_base64)
        if img_link is None:
            return JSONResponse(status_code=500, content={"message": "upload image fail"})
        sql = "update raw_material set name= %s, unit= %s, image= %s, price= %s where id=%s;"
        cur.execute(sql, (name, unit, img_link, price, id))
        conn.commit()
        return JSONResponse(status_code=200, content={"message": "success", "img_link": img_link, "id": id})
    except Exception as e:
        lineNum, detail = exception_tool.exception_tool(e)
        msg = f"{detail}, error in line {lineNum}"
        inert_error_log(conn, cur, "", "raw_material/update", msg)
        return JSONResponse(status_code=400, content={'error': msg})


@router.post('/delete')
async def delete(id: int = Form(...), current_user: User = Depends(get_current_user)):
    if current_user.role != "admin":
        return JSONResponse(status_code=400, content={"message": "You are not admin"})
    conn = connection.connect_to_mysql()
    cur = conn.cursor()
    try:
        sql = "update raw_material set is_active= %s where id=%s;"
        cur.execute(sql, (False, id))
        conn.commit()
        return JSONResponse(status_code=200, content={"message": "success", "id": id})
    except Exception as e:
        lineNum, detail = exception_tool.exception_tool(e)
        msg = f"{detail}, error in line {lineNum}"
        inert_error_log(conn, cur, "", "raw_material/delete", msg)
        return JSONResponse(status_code=400, content={'error': msg})
