from fastapi import FastAPI, HTTPException, Depends
from pydantic import BaseModel
from typing import List, Annotated
import models
from sqlalchemy.orm import Session
import uvicorn
from dotenv import load_dotenv
from sqlalchemy import create_engine
import os
from fastapi_sqlalchemy import DBSessionMiddleware, db

load_dotenv(".env")
app = FastAPI()
app.add_middleware(DBSessionMiddleware, db_url=os.environ["DATABASE_URL"])
engine = create_engine(os.environ["DATABASE_URL"])
models.Questions.metadata.create_all(bind=engine)


# app = FastAPI()




# app = start_application()

app = FastAPI()
class ChoiceBase(BaseModel):
    choice_test: str
    is_correct: bool

class QuestionBase(BaseModel):
    question_text: str
    choices: list[ChoiceBase]

# def get_db():
#     db = Sessionlocal()
#     try:
#         yield db
#     finally:
#         db.close()

# db_dependancy = Annotated(Session, Depends(get_db))
@app.get("/")
async def home():
    return{"message":"Welcome to our app"}

@app.get("/questions/{question_id}")
async def read_question(question_id: int):
    with db():
        result = db.session.query(models.Questions).filter(models.Questions.id == question_id).first()
    if not result:
        raise HTTPException(status_code=404, detail='question is not found')
    return result

@app.get("/choices/{question_id}")
async def read_choices(question_id: int):
    with db():
        result = db.session.query(models.Choices).filter(models.Choices.question_id == question_id).all()
    if not result:
        raise HTTPException(status_code=404, detail='choice is not found')
    return result

@app.delete("/questions/{question_id}")
async def delete_question(question_id: int):
    with db():
        result = db.session.query(models.Choices).filter(models.Choices.question_id == question_id).all()
        if not result:
            raise HTTPException(status_code=404, detail='no such question exists')
        for item in result:
            db.session.delete(item)
        # db.delete(result)
        db.session.commit()
        res = db.session.query(models.Questions).filter(models.Questions.id == question_id).all()
        for item in res:
            db.session.delete(item)
        # db.delete(res)
        db.session.commit()
    

@app.post("/questions/")
async def create_questions(question: QuestionBase):
    # with db():
    #     db.session.query(models.Questions).all()
    #     db.session.query(models.Choices).all()
    db_question = models.Questions(question_text=question.question_text)
    with db():
        db.session.add(db_question)
        db.session.commit()
        # db.refresh(db_question)
        for choice in question.choices:
            db_choice = models.Choices(choice_text=choice.choice_test, is_correct=choice.is_correct, question_id=db_question.id)
            # with db():
            db.session.add(db_choice)
        db.session.commit()


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)