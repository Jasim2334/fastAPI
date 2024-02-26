from passlib.context import CryptContext
from fastapi.security import OAuth2PasswordBearer
from datetime import timedelta,datetime
from jose import jwt,JWTError
from models import Users
from fastapi import HTTPException,Depends
from typing import Annotated
from fastapi import APIRouter


router = APIRouter()
SECRET_KEY = 'django-insecure-8nmiyrwyvl$z-n5khh2030=c+u*b=-c66s8xoc(dwl4*7&i6lm'
ALGORITHM = 'HS256'

bcrypt_context = CryptContext(schemes=['bcrypt'],deprecated='auto')
oauth2_bearer = OAuth2PasswordBearer(tokenUrl='auth/token')


def authenticate_user(name:str,password:str,db):
    user_data = db.query(Users).filter(Users.name==name).first()
    if not user_data:
        raise HTTPException(status_code=401,detail="User not found")
    if not bcrypt_context.verify(password,user_data.password):
        raise HTTPException(status_code=401,detail='Incorrect password')
    return user_data

def create_access_token(name:str,user_id:int,expiry_time:timedelta):
    encode = {'sub':name,'id':user_id}
    expires = datetime.utcnow() + expiry_time
    encode.update({'exp':expires})
    return jwt.encode(encode,SECRET_KEY,algorithm=ALGORITHM)


async def get_current_user(token:Annotated[str,Depends(oauth2_bearer)]):
    try:
        payload = jwt.decode(token,SECRET_KEY,algorithms=[ALGORITHM])
        # name : str = payload.get('sub')
        user_id : int = payload.get('id')
        if user_id is None:
            raise HTTPException(status_code=401,detail="User not found")
        return {'id':user_id}
    except JWTError:
        raise HTTPException(status_code=401,detail="User not found")
        
    
@router.get('/')
def router_data_get():
    return {'message':"Hello World"}