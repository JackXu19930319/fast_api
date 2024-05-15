from datetime import timedelta

import uvicorn
from fastapi import FastAPI
from routes.user import router as users_router
from routes.hi import router as hi_router
from routes.store import router as store_router
from routes.raw_material import router as raw_material_router
from starlette.middleware.cors import CORSMiddleware
import os

app = FastAPI()
# CORS 中间件配置
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 允许所有域名访问，可以根据需要指定域名
    allow_credentials=True,
    allow_methods=["*"],  # 允许所有方法（GET, POST, DELETE, etc.）
    allow_headers=["*"],  # 允许所有头
)

app.include_router(users_router, prefix="/api/v1/users", tags=["users"])
app.include_router(store_router, prefix="/api/v1/store", tags=["store"])
app.include_router(raw_material_router, prefix="/api/v1/raw_material", tags=["raw_material"])
app.include_router(hi_router, prefix="/api/v1/hi", tags=["hi"])

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=int(os.environ.get('SERVER_PORT', '8000')))
