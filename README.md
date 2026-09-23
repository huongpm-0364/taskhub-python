# taskhub-python

TaskHub API — FastAPI + SQLAlchemy + Alembic.

## Cấu trúc project

```
app/
  main.py          FastAPI app, include routers
  config.py        Đọc config từ .env (pydantic-settings)
  database.py       Engine, SessionLocal, Base, get_db dependency
  models/          SQLAlchemy models: User, Project, Task, Comment, Tag
  schemas/         Pydantic schemas (request/response)
  crud/            Hàm thao tác DB (get/create ...)
  routers/         APIRouter: /api/users, /api/projects, /api/tasks
alembic/           Migration scripts
```

## Setup

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

cp .env.example .env
# sửa DATABASE_URL trỏ tới Postgres/MySQL của bạn
```

Setup Postgres local bằng Homebrew (macOS):

```bash
brew install postgresql@16
brew services start postgresql@16

export PATH="/opt/homebrew/opt/postgresql@16/bin:$PATH"
createuser -s taskhub
createdb -O taskhub taskhub
```

Rồi set `.env`:

```
DATABASE_URL=postgresql+psycopg2://taskhub@localhost:5432/taskhub
```

## Migrate database

```bash
alembic revision --autogenerate -m "create initial tables"
alembic upgrade head
```

## Chạy server

```bash
uvicorn app.main:app --reload
```

Mở http://127.0.0.1:8000/docs để xem Swagger UI và thử các endpoint
`/api/users`, `/api/projects`, `/api/tasks`.

## Chạy test

```bash
pytest
```

Test dùng SQLite in-memory riêng (qua `tests/conftest.py`), không đụng vào database
thật đang cấu hình trong `.env`.
