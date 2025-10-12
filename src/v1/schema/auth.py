from pydantic import BaseModel, EmailStr

class Register(BaseModel):
    first_name:str
    last_name:str
    email: EmailStr
    password:str
    
class Login(BaseModel):
    email:EmailStr
    password:str #implement magic link later on