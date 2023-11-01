from fastapi import FastAPI, HTTPException, Body
from pydantic import BaseModel
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, String, Float

app = FastAPI()


DATABASE_URL = 'mysql://mateus:123456@localhost/mateus'
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

class Aluno(Base):
    __tablename__ = 'aluno'
    id = Column(Integer, primary_key=True, index=True)
    nome = Column(String(100))
    idade = Column(Integer)
    nota_primeiro_semestre = Column(Float)
    nota_segundo_semestre = Column(Float)
    nome_professor = Column(String(100))
    numero_sala = Column(String(10))

class AlunoPydanticResponse(BaseModel):
    id: int
    nome: str
    idade: int
    nota_primeiro_semestre: float
    nota_segundo_semestre: float
    nome_professor: str
    numero_sala: str
class AlunoPydantic(BaseModel):
    nome: str
    idade: int
    nota_primeiro_semestre: float
    nota_segundo_semestre: float
    nome_professor: str
    numero_sala: str


@app.post('/alunos', response_model=AlunoPydanticResponse)
def criar_aluno(aluno: AlunoPydantic):
    if None in aluno.dict().values():
        raise HTTPException(status_code=422)

    db_aluno = Aluno(**aluno.dict())
    db = SessionLocal()
    db.add(db_aluno)
    db.commit()
    db.refresh(db_aluno)
    db.close()
    return AlunoPydanticResponse(**db_aluno.__dict__)

@app.get('/alunos/{aluno_id}', response_model=AlunoPydanticResponse)
def obter_aluno(aluno_id: int):
    db = SessionLocal()
    aluno = db.query(Aluno).filter(Aluno.id == aluno_id).first()
    db.close()
    if aluno is None:
        raise HTTPException(status_code=404, detail='Aluno não encontrado')
    return AlunoPydanticResponse(**aluno.__dict__)

@app.get('/alunos', response_model=list[AlunoPydanticResponse])
def listar_alunos():
    db = SessionLocal()
    alunos = db.query(Aluno).all()
    db.close()
    return [AlunoPydanticResponse(**aluno.__dict__) for aluno in alunos]

@app.put('/alunos/{aluno_id}', response_model=AlunoPydanticResponse)
def atualizar_aluno(aluno_id: int, aluno: AlunoPydantic = Body(...)):
    db = SessionLocal()
    db_aluno = db.query(Aluno).filter(Aluno.id == aluno_id).first()
    if db_aluno is None:
        db.close()
        raise HTTPException(status_code=404, detail='Aluno não encontrado')
    for key, value in aluno.dict().items():
        setattr(db_aluno, key, value)
    db.commit()
    db.refresh(db_aluno)
    db.close()
    return AlunoPydanticResponse(**db_aluno.__dict__)

@app.delete('/alunos/{aluno_id}', response_model=dict)
def deletar_aluno(aluno_id: int):
    db = SessionLocal()
    db_aluno = db.query(Aluno).filter(Aluno.id == aluno_id).first()
    if db_aluno is None:
        db.close()
        raise HTTPException(status_code=404, detail='Aluno não encontrado')
    db.delete(db_aluno)
    db.commit()
    db.close()
    return {'message': 'Aluno excluído com sucesso'}

if __name__ == '__main__':
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
