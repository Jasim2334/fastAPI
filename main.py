from fastapi import FastAPI,Depends,HTTPException
from database import SessionLocal
from sqlalchemy.orm import Session 
from schemas import UserPostSchema,UserUpdateSchema,UserGetSchema,Token
from models import Users
from database import Base,engine
from auth import bcrypt_context
from fastapi.security import OAuth2PasswordRequestForm
from typing import Annotated
from auth import create_access_token,authenticate_user,get_current_user
from datetime import timedelta
import auth
from typing import Optional


app = FastAPI()
app.include_router(auth.router,prefix="/admin",
    tags=["Route API"]
)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
Base.metadata.create_all(bind=engine)
user_dependency = Annotated[dict,Depends(get_current_user)]

@app.get("/cur_user",status_code=200)
async def get_cur_user(user:user_dependency,db:Session=Depends(get_db)):
    user_data = db.query(Users).filter(Users.id==user['id']).first()
    if user is None:
        raise HTTPException(status_code=401,detail='Authentication Failed')
    return {'id':user['id'],'name':user_data.name,'email':user_data.email}


@app.get('/',response_model=list[UserGetSchema]) #Here UserGetSchema is inside List because it return data in list all()
def read_data(db:Session=Depends(get_db)):
    data = db.query(Users).all()
    return data

@app.get('/{user_id}',response_model=UserGetSchema) #Here UserGetSchema it is not inside list because its returns single data first()
def read_single_data(user_id:int,db:Session=Depends(get_db)):
    data = db.query(Users).filter(Users.id==user_id).first()
    if data == None:
        raise HTTPException(status_code=401,detail=f"Data with ID {user_id} not available")
    return data

@app.post('/')
def create_data(request:UserPostSchema,db:Session=Depends(get_db)):
    data = db.query(Users).all()
    for i in data:
        if i.email == request.email:
            raise HTTPException(status_code=401,detail="User already exists")
    data = Users(name=request.name,email=request.email,password=bcrypt_context.hash(request.password))
    db.add(data)
    db.commit()
    return {"message":"User Created"}


@app.put('/{user_id}')
def update_data(user_id:int,request:UserUpdateSchema,db:Session=Depends(get_db)):
    data = db.query(Users).filter(Users.id==user_id).first()
    if data == None:
        raise HTTPException(status_code=401,detail=f"Data with ID {user_id} not found")
    data.name = request.name
    data.password = bcrypt_context.hash(request.password)
    db.add(data)
    db.commit()
    return {"message":"Data updated!"}

@app.delete('/{user_id}')
def delete_data(user_id:int,db:Session=Depends(get_db)):
    data = db.query(Users).filter(Users.id==user_id).first()
    if data == None:
        raise HTTPException(status_code=401,detail=f'Data with ID {user_id} not available') 
    db.delete(data)
    db.commit()
    return {'message':"Data deleted successfully."}

@app.post('/auth/token',response_model=Token)
def login_for_access_token(form_data:Annotated[OAuth2PasswordRequestForm,Depends()],db:Session=Depends(get_db)):
    user = authenticate_user(form_data.username,form_data.password,db)
    if not user:
        raise HTTPException(status_code=401,detail="User not found")
    token = create_access_token(user.name,user.id,timedelta(minutes=20))
    return {'access_token':token,'token_type':'bearer'}

#This is emample for query params
@app.get('/params/')
def common_params(name:str,age:int,gender:Optional[str]=None):
    return {'message':f"Age of {name} is {age} and gender is {gender}"}