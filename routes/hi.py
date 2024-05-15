from fastapi import APIRouter, Query

from fastapi.responses import JSONResponse
from security import verify_password, get_password_hash
from token_api import create_access_token, ACCESS_TOKEN_EXPIRE_HOURS, create_refresh_token
from datetime import timedelta
from models import User, UserIn, UserOut, UserInDB
import connection

router = APIRouter()


@router.get("")
async def hi():
    return {"message": "hi"}
