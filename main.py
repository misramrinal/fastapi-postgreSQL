import jwt
from pydantic import BaseModel
from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from passlib.hash import bcrypt
from tortoise import fields 
from tortoise.contrib.fastapi import register_tortoise
from tortoise.contrib.pydantic import pydantic_model_creator
from tortoise.models import Model
import models
from database import engine, Sessionlocal 
from sqlalchemy.orm import Session

def create_tables():         
	models.Questions.metadata.create_all(bind=engine)
        

def start_application():
    app = FastAPI()
    create_tables()
    return app

app = start_application()

def get_db():
    db = Sessionlocal()
    try:
        yield db
    finally:
        db.close()

JWT_SECRET = 'myjwtsecret'

class ChoiceBase(BaseModel):
    choice_test: str
    is_correct: bool

class QuestionBase(BaseModel):
    question_text: str
    choices: list[ChoiceBase]


class User(Model):
    id = fields.IntField(pk=True)
    username = fields.CharField(50, unique=True)
    password_hash = fields.CharField(128)

    def verify_password(self, password):
        return bcrypt.verify(password, self.password_hash)

User_Pydantic = pydantic_model_creator(User, name='User')
UserIn_Pydantic = pydantic_model_creator(User, name='UserIn', exclude_readonly=True)

oauth2_scheme = OAuth2PasswordBearer(tokenUrl='token')

async def authenticate_user(username: str, password: str):
    user = await User.get(username=username)
    if not user:
        return False 
    if not user.verify_password(password):
        return False
    return user 

@app.post('/token')
async def generate_token(form_data: OAuth2PasswordRequestForm = Depends()):
    user = await authenticate_user(form_data.username, form_data.password)

    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, 
            detail='Invalid username or password'
        )

    user_obj = await User_Pydantic.from_tortoise_orm(user)

    token = jwt.encode(user_obj.dict(), JWT_SECRET)

    return {'access_token' : token, 'token_type' : 'bearer'}

async def get_current_user(token: str = Depends(oauth2_scheme)):
    try:
        payload = jwt.decode(token, JWT_SECRET, algorithms=['HS256'])
        user = await User.get(id=payload.get('id'))
    except:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, 
            detail='Invalid username or password'
        )

    return await User_Pydantic.from_tortoise_orm(user)


@app.post('/users', response_model=User_Pydantic)
async def create_user(user: UserIn_Pydantic):
    user_obj = User(username=user.username, password_hash=bcrypt.hash(user.password_hash))
    await user_obj.save()
    return await User_Pydantic.from_tortoise_orm(user_obj)

@app.get('/users/me', response_model=User_Pydantic)
async def get_user(user: User_Pydantic = Depends(get_current_user)):
    return user    

@app.get("/questions/{question_id}", response_model=User_Pydantic)
async def read_question(question_id: int, db: Session = Depends(get_db), user: User_Pydantic = Depends(get_current_user)):
    result = db.query(models.Questions).filter(models.Questions.id == question_id).first()
    if not result:
        raise HTTPException(status_code=404, detail='question is not found')
    return result

@app.get("/choices/{question_id}", response_model=User_Pydantic)
async def read_choices(question_id: int, db: Session = Depends(get_db), user: User_Pydantic = Depends(get_current_user)):
    result = db.query(models.Choices).filter(models.Choices.question_id == question_id).all()
    if not result:
        raise HTTPException(status_code=404, detail='choice is not found')
    return result

@app.delete("/questions/{question_id}", response_model=User_Pydantic)
async def delete_question(question_id: int, db: Session = Depends(get_db), user: User_Pydantic = Depends(get_current_user)):
    result = db.query(models.Choices).filter(models.Choices.question_id == question_id).all()
    if not result:
        raise HTTPException(status_code=404, detail='no such question exists')
    for item in result:
        db.delete(item)
    # db.delete(result)
    db.commit()
    res = db.query(models.Questions).filter(models.Questions.id == question_id).all()
    for item in res:
        db.delete(item)
    # db.delete(res)
    db.commit()
    

@app.post("/questions/", response_model=User_Pydantic)
async def create_questions(question: QuestionBase, db: Session = Depends(get_db), user: User_Pydantic = Depends(get_current_user)):
    db_question = models.Questions(question_text=question.question_text)
    db.add(db_question)
    db.commit()
    db.refresh(db_question)
    for choice in question.choices:
        db_choice = models.Choices(choice_text=choice.choice_test, is_correct=choice.is_correct, question_id=db_question.id)
        db.add(db_choice)
    db.commit()

register_tortoise(
    app, 
    db_url='sqlite://db.sqlite3',
    modules={'models': ['main']},
    generate_schemas=True,
    add_exception_handlers=True
)