# taskhub-python

TaskHub API — FastAPI + SQLAlchemy + Alembic.

## Cấu trúc project

```
app/
  main.py               FastAPI app, include routers
  api/
    routers/            APIRouter: /api/users, /api/projects, /api/tasks, /api/tags
  core/
    config.py           Đọc config từ .env (pydantic-settings)
    database.py         Engine, SessionLocal, Base, get_db dependency
    constants.py         Hằng số dùng chung (độ dài field,...)
    pagination.py        Hằng số phân trang dùng chung (DEFAULT_SKIP, DEFAULT_LIMIT,...)
  models/               SQLAlchemy models: User, Project, Task, Comment, Tag
  schemas/              Pydantic schemas (Create/Update/Read)
  repositories/         Data access thuần (query DB, không chứa business rule)
  services/             Business logic (hash password, ràng buộc xóa,...), gọi xuống repositories
docs/                   Ghi chú/tài liệu project
migrations/             Alembic migration scripts
tests/                  Test tự động (pytest)
```

Luồng gọi: `router` → `service` (business logic) → `repository` (query DB) → `model`.

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
