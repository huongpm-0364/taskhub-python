from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app import crud
from app.database import get_db
from app.schemas.task import TaskCreate, TaskRead

router = APIRouter(prefix="/api/tasks", tags=["tasks"])


@router.get("/", response_model=list[TaskRead])
def list_tasks(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    return crud.task.get_tasks(db, skip=skip, limit=limit)


@router.post("/", response_model=TaskRead, status_code=201)
def create_task(task: TaskCreate, db: Session = Depends(get_db)):
    return crud.task.create_task(db, task)


@router.get("/{task_id}", response_model=TaskRead)
def get_task(task_id: int, db: Session = Depends(get_db)):
    db_task = crud.task.get_task(db, task_id)
    if db_task is None:
        raise HTTPException(status_code=404, detail="Task not found")
    return db_task
