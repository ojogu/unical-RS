import sqlalchemy as sa
from datetime import datetime
from src.v1.base.model import BaseModel

class Admin(BaseModel):
    __tablename__ = "admins"
    
class Visitor(BaseModel):
    __tablename__ = "visitors"
    
class Libarian(BaseModel):
    __tablename__ = "libarians"
    
class Student(BaseModel):
    __tablename__ = "students"
    
class Staff(BaseModel):
    __tablename__ = "staff"
    
class Resource(BaseModel):
    __tablename__ = "staff"
    
class MetaData(BaseModel):
    __tablename__ = "staff"


