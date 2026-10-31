from fastapi import FastAPI, Depends, HTTPException
from pydantic import BaseModel
import os
import psycopg2
from psycopg2.extras import RealDictCursor

app = FastAPI(title="Library Management API", version="1.0.0")

DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://postgres:postgres@db:5432/students_db")

def get_db_connection():
    conn = psycopg2.connect(DATABASE_URL, cursor_factory=RealDictCursor)
    return conn

class ReaderCreate(BaseModel):
    full_name: str

class ReaderUpdate(BaseModel):
    full_name: str | None = None
    has_book: bool | None = None
    ticket_active: bool | None = None

@app.post("/readers/", summary="Добавить читателя")
def add_reader(reader: ReaderCreate):
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute(
        "INSERT INTO readers (full_name, has_book, ticket_active) VALUES (%s, FALSE, TRUE) RETURNING id, full_name, has_book, ticket_active;",
        (reader.full_name,)
    )
    new_reader = cur.fetchone()
    conn.commit()
    cur.close()
    conn.close()
    return new_reader

@app.get("/readers/", summary="Получить список всех читателей")
def get_readers():
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("SELECT * FROM readers;")
    readers = cur.fetchall()
    cur.close()
    conn.close()
    return readers

@app.put("/readers/{reader_id}", summary="Отредактировать данные читателя или выдать книгу")
def update_reader(reader_id: int, data: ReaderUpdate):
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("SELECT * FROM readers WHERE id = %s;", (reader_id,))
    if not cur.fetchone():
        cur.close()
        conn.close()
        raise HTTPException(status_code=404, detail="Читатель не найден")
    
    cur.execute(
        "UPDATE readers SET full_name = COALESCE(%s, full_name), has_book = COALESCE(%s, has_book), ticket_active = COALESCE(%s, ticket_active) WHERE id = %s RETURNING *;",
        (data.full_name, data.has_book, data.ticket_active, reader_id)
    )
    updated = cur.fetchone()
    conn.commit()
    cur.close()
    conn.close()
    return updated

@app.delete("/readers/{reader_id}/ticket", summary="Изъять читательский билет")
def revoke_ticket(reader_id: int):
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("UPDATE readers SET ticket_active = FALSE WHERE id = %s RETURNING *;", (reader_id,))
    res = cur.fetchone()
    conn.commit()
    cur.close()
    conn.close()
    if not res:
        raise HTTPException(status_code=404, detail="Читатель не найден")
    return {"message": "Читательский билет изъят", "reader": res}

@app.get("/reports/summary", summary="Отчет: всего читателей и сколько из них имеют книги на руках")
def get_report():
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("SELECT COUNT(*) as total_readers FROM readers;")
    total = cur.fetchone()["total_readers"]
    
    cur.execute("SELECT COUNT(*) as readers_with_books FROM readers WHERE has_book = TRUE;")
    with_books = cur.fetchone()["readers_with_books"]
    
    cur.close()
    conn.close()
    return {
        "total_readers": total,
        "readers_with_books": with_books,
        "readers_without_books": total - with_books
    }
