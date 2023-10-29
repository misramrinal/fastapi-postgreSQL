from fastapi import FastAPI, HTTPException, Depends
from pydantic import BaseModel
from typing import List, Annotated
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

app = FastAPI()
class ChoiceBase(BaseModel):
    choice_test: str
    is_correct: bool

class QuestionBase(BaseModel):
    question_text: str
    choices: list[ChoiceBase]

def get_db():
    db = Sessionlocal()
    try:
        yield db
    finally:
        db.close()

# db_dependancy = Annotated(Session, Depends(get_db))
@app.get("/questions/{question_id}")
async def read_question(question_id: int, db: Session = Depends(get_db)):
    result = db.query(models.Questions).filter(models.Questions.id == question_id).first()
    if not result:
        raise HTTPException(status_code=404, detail='question is not found')
    return result

@app.get("/choices/{question_id}")
async def read_choices(question_id: int, db: Session = Depends(get_db)):
    result = db.query(models.Choices).filter(models.Choices.question_id == question_id).all()
    if not result:
        raise HTTPException(status_code=404, detail='choice is not found')
    return result

@app.delete("/questions/{question_id}")
async def delete_question(question_id: int, db: Session = Depends(get_db)):
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
    

@app.post("/questions/")
async def create_questions(question: QuestionBase, db: Session = Depends(get_db)):
    db_question = models.Questions(question_text=question.question_text)
    db.add(db_question)
    db.commit()
    db.refresh(db_question)
    for choice in question.choices:
        db_choice = models.Choices(choice_text=choice.choice_test, is_correct=choice.is_correct, question_id=db_question.id)
        db.add(db_choice)
    db.commit()
