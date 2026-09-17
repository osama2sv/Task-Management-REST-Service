from fastapi import FastAPI, HTTPException

from api.database import get_connection
from api.models import Task, TaskCreate

app = FastAPI(title="Task Management REST Service")


@app.get("/")
def root():
    return {"message": "Task Management REST Service is running"}


@app.get("/api/tasks", response_model=list[Task])
def get_tasks():
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(
                """
                SELECT id, title, description, status, due_date
                FROM tasks
                ORDER BY id;
                """
            )
            rows = cur.fetchall()

    return [
        {
            "id": row[0],
            "title": row[1],
            "description": row[2],
            "status": row[3],
            "due_date": row[4],
        }
        for row in rows
    ]


@app.get("/api/tasks/{task_id}", response_model=Task)
def get_task(task_id: int):
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(
                """
                SELECT id, title, description, status, due_date
                FROM tasks
                WHERE id = %s;
                """,
                (task_id,),
            )
            row = cur.fetchone()

    if row is None:
        raise HTTPException(status_code=404, detail="Task not found")

    return {
        "id": row[0],
        "title": row[1],
        "description": row[2],
        "status": row[3],
        "due_date": row[4],
    }


@app.post("/api/tasks", response_model=Task, status_code=201)
def create_task(task: TaskCreate):
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(
                """
                INSERT INTO tasks (title, description, status, due_date)
                VALUES (%s, %s, %s, %s)
                RETURNING id, title, description, status, due_date;
                """,
                (
                    task.title,
                    task.description,
                    task.status,
                    task.due_date,
                ),
            )
            row = cur.fetchone()
            conn.commit()

    return {
        "id": row[0],
        "title": row[1],
        "description": row[2],
        "status": row[3],
        "due_date": row[4],
    }


@app.put("/api/tasks/{task_id}", response_model=Task)
def update_task(task_id: int, task: TaskCreate):
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(
                """
                UPDATE tasks
                SET title = %s,
                    description = %s,
                    status = %s,
                    due_date = %s
                WHERE id = %s
                RETURNING id, title, description, status, due_date;
                """,
                (
                    task.title,
                    task.description,
                    task.status,
                    task.due_date,
                    task_id,
                ),
            )
            row = cur.fetchone()

            if row is None:
                conn.rollback()
                raise HTTPException(
                    status_code=404,
                    detail="Task not found"
                )

            conn.commit()

    return {
        "id": row[0],
        "title": row[1],
        "description": row[2],
        "status": row[3],
        "due_date": row[4],
    }


@app.delete("/api/tasks/{task_id}", status_code=204)
def delete_task(task_id: int):
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(
                """
                DELETE FROM tasks
                WHERE id = %s
                RETURNING id;
                """,
                (task_id,),
            )
            row = cur.fetchone()

            if row is None:
                conn.rollback()
                raise HTTPException(
                    status_code=404,
                    detail="Task not found"
                )

            conn.commit()

    return None