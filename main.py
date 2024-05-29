from sqlalchemy import Boolean, Column, Integer, String, create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import Session
# Establish a connection to the database

DATABASE_URL = "postgresql://postgres:change1t@localhost:5432/cherrydb"

#"postgresql://postgres:change1t@host/cherrydb"
engine = create_engine(DATABASE_URL)
session = Session(engine)

# Define the base model class
Base = declarative_base()

# Define the User model
class User(Base):
 __tablename__ = "users"
 id = Column(Integer, primary_key=True, index=True)
 name = Column(String, index=True)
 email = Column(String, unique=True, index=True)
 is_active = Column(Boolean, default=True)

# Create the table
Base.metadata.create_all(bind=engine)


from fastapi import FastAPI
from fastapi import HTTPException
from typing import List
from pydantic import BaseModel
app = FastAPI()

# Pydantic models
class UserBase(BaseModel):
 name: str
 email: str
 is_active: bool = True

class UserCreate(UserBase):
 pass

class User(UserBase):
 id: int
class Config:
 orm_mode = True

# Routes
@app.post("/users/", response_model=User)
def create_user(user: UserCreate):
 db_user = User(**user.dict())
 session.add(db_user)
 session.commit()
 session.refresh(db_user)
 return db_user

@app.get("/users/", response_model=List[User])
def read_users(skip: int = 0, limit: int = 100):
 users = session.query(User).offset(skip).limit(limit).all()
 return users

@app.get("/users/{user_id}", response_model=User)
def read_user(user_id: int):
 user = session.query(User).filter(User.id == user_id).first()
 if user is None:
   raise HTTPException(status_code=404, detail="User not found")
 return user

@app.put("/users/{user_id}", response_model=User)
def update_user(user_id: int, user: UserBase):
 db_user = session.query(User).filter(User.id == user_id).first()
 if db_user is None:
   raise HTTPException(status_code=404, detail="User not found")
 for key, value in user.dict().items():
   setattr(db_user, key, value)
 session.commit()
 session.refresh(db_user)
 return db_user

@app.delete("/users/{user_id}", response_model=User)
def delete_user(user_id: int):
 user = session.query(User).filter(User.id == user_id).first()
 if user is None:
   raise HTTPException(status_code=404, detail="User not found")
 session.delete(user)
 session.commit()
 return user
