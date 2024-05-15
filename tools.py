import base64
import os

from PIL import Image
import requests
from io import BytesIO


def inert_error_log(conn, cur, curl_command, routes, msg):
    sql = "rollback;"
    cur.execute(sql)
    conn.commit()
    sql = "insert into error_log(req_data, message, routes) values (%s, %s, %s);"
    cur.execute(sql, (curl_command, msg, routes))
    conn.commit()


def encode_image_to_base64(image_path):
    """ 将图片文件编码为 base64 字符串 """
    with Image.open(image_path) as image:
        buffered = BytesIO()
        image.save(buffered, format="JPEG")  # 或者根据你的图片格式调整
        return base64.b64encode(buffered.getvalue()).decode('utf-8')


def upload_to_imgur(base64_image, client_id):
    """ 上传 base64 编码的图片到 Imgur """
    # base64_image = encode_image_to_base64(image_path)

    url = "https://api.imgur.com/3/image"
    headers = {'Authorization': f'Client-ID {client_id}'}
    data = {
        'image': base64_image,
        'type': 'base64',
    }

    response = requests.post(url, headers=headers, data=data)
    return response.json()


def upload_img_execute(base64_image):
    # 使用示例
    client_id = os.environ.get('IMGUR_CLIENT_ID', '')
    result = upload_to_imgur(base64_image, client_id)

    status = result.get('status')
    is_success = result.get('success')
    if status == 200 and is_success:
        link = result.get('data').get('link')
        return link
    else:
        return None
