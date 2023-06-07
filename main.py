import os
import urllib
from typing import List

import databases
import sqlalchemy
from fastapi import FastAPI, status
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

# SQLAlchemy specific code, as with any other app
# DATABASE_URL = "sqlite:///./test.db"

host = os.environ.get('DBHOST', 'localhost')
port_rw = urllib.parse.quote_plus(str(os.environ.get('DBPORTRW', '5000')))
port_ro = urllib.parse.quote_plus(str(os.environ.get('DBPORTRO', '5001')))
dbname = os.environ.get('DBNAME', 'postgres')
username = urllib.parse.quote_plus(str(os.environ.get('DBUSERNAME', 'postgres')))
password = urllib.parse.quote_plus(str(os.environ.get('DBPASSWORD', 'postgres')))
ssl_mode = urllib.parse.quote_plus(str(os.environ.get('SSL_MODE', 'prefer')))
DATABASE_POOL_SIZE = int(os.environ.get('DBPOOL', 10))
DSN_TEMPLATE = 'postgresql://{}:{}@{}:{}/{}?sslmode={}'
DATABASE_URL_RW = DSN_TEMPLATE.format(username, password, host, port_rw, dbname, ssl_mode)
DATABASE_URL_RO = DSN_TEMPLATE.format(username, password, host, port_ro, dbname, ssl_mode)

database_rw = databases.Database(DATABASE_URL_RW)
database_ro = databases.Database(DATABASE_URL_RO)

metadata = sqlalchemy.MetaData()

notes = sqlalchemy.Table(
        "notes",
        metadata,
        sqlalchemy.Column("id", sqlalchemy.Integer, primary_key=True),
        sqlalchemy.Column("cdate", sqlalchemy.DateTime(timezone=True), server_default=sqlalchemy.func.now()),
        sqlalchemy.Column("mdate", sqlalchemy.DateTime(timezone=True), onupdate=sqlalchemy.func.now()),
        sqlalchemy.Column("text", sqlalchemy.String),
        sqlalchemy.Column("completed", sqlalchemy.Boolean),
)

engine_rw = sqlalchemy.create_engine(DATABASE_URL_RW, pool_size=DATABASE_POOL_SIZE, max_overflow=0)
engine_ro = sqlalchemy.create_engine(DATABASE_URL_RO, pool_size=DATABASE_POOL_SIZE, max_overflow=0)

metadata.create_all(engine_rw)


class NoteIn(BaseModel):
    text: str
    completed: bool = False


class NotePatch(BaseModel):
    completed: bool


class Note(BaseModel):
    id: int
    text: str
    completed: bool


app = FastAPI(title="REST API using FastAPI PostgreSQL cluster on patroni Async EndPoints")
app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
)


@app.on_event("startup")
async def startup():
    await database_rw.connect()
    await database_ro.connect()


@app.on_event("shutdown")
async def shutdown():
    await database_rw.disconnect()
    await database_ro.disconnect()


@app.get("/notes/", response_model=List[Note], status_code=status.HTTP_200_OK)
async def read_notes(skip: int = 0, take: int = 20):
    query = notes.select().offset(skip).limit(take)
    return await database_ro.fetch_all(query)


@app.get("/notes/{note_id}/", response_model=Note, status_code=status.HTTP_200_OK)
async def read_notes(note_id: int):
    query = notes.select().where(notes.c.id == note_id)
    return await database_ro.fetch_one(query)


@app.post("/notes/", response_model=Note, status_code=status.HTTP_201_CREATED)
async def create_note(note: NoteIn):
    query = notes.insert().values(text=note.text, completed=note.completed)
    last_record_id = await database_rw.execute(query)
    return {**note.dict(), "id": last_record_id}


@app.put("/notes/{note_id}/", response_model=Note, status_code=status.HTTP_200_OK)
async def update_note(note_id: int, payload: NoteIn):
    query = notes.update().where(notes.c.id == note_id).values(text=payload.text, completed=payload.completed)
    await database_rw.execute(query)
    return {**payload.dict(), "id": note_id}


@app.patch("/notes/{note_id}/", response_model=NotePatch, status_code=status.HTTP_200_OK)
async def update_note(note_id: int, payload: NotePatch):
    query = notes.update().where(notes.c.id == note_id).values(completed=payload.completed)
    await database_rw.execute(query)
    return {**payload.dict(), "id": note_id}


@app.delete("/notes/{note_id}/", status_code=status.HTTP_200_OK)
async def delete_note(note_id: int):
    query = notes.delete().where(notes.c.id == note_id)
    await database_rw.execute(query)
    return {"message": "Note with id: {} deleted successfully!".format(note_id)}
