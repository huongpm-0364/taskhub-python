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
    security.py         Hash password (bcrypt), tạo/giải mã JWT access token
    constants.py         Hằng số dùng chung (độ dài field,...)
    pagination.py        Hằng số phân trang dùng chung (DEFAULT_SKIP, DEFAULT_LIMIT,...)
  models/               SQLAlchemy models: User, Project, Task, Comment, Tag
  schemas/              Pydantic schemas (Create/Update/Read)
  repositories/         Data access thuần (query DB, không chứa business rule)
  services/             Business logic (hash password, JWT, ràng buộc xóa,...), gọi xuống repositories
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

## Xác thực (JWT)

```bash
# Đăng ký
curl -X POST http://127.0.0.1:8000/api/users/register \
  -H "Content-Type: application/json" \
  -d '{"email":"a@a.com","username":"alice","password":"secret123"}'

# Đăng nhập — lưu ý: form data (application/x-www-form-urlencoded), không phải JSON
curl -X POST http://127.0.0.1:8000/api/users/login \
  -d "username=alice&password=secret123"

# Gọi endpoint cần xác thực
curl http://127.0.0.1:8000/api/users/me -H "Authorization: Bearer <access_token>"
```

Trong Swagger UI (`/docs`): bấm nút **Authorize** ở góc trên, đăng nhập bằng
username/password — Swagger tự lấy token và gắn vào các request tiếp theo, không cần
copy token thủ công.

`SECRET_KEY` trong `.env.example` chỉ dùng để dev local — nhớ đổi giá trị thật khi
deploy (`python -c "import secrets; print(secrets.token_hex(32))"`).

## Phân quyền

- `GET /api/users/` — chỉ role `admin` gọi được.
- `DELETE /api/projects/{id}` — chỉ chủ sở hữu project (hoặc admin) mới xóa được.
- `POST /api/tasks/{id}/bookmark` — cần đăng nhập (bất kỳ user nào).

Chưa có endpoint "promote user thành admin" (ngoài phạm vi các bài hiện tại). Muốn test
cục bộ, tự sửa trực tiếp trong DB:

```sql
UPDATE users SET role = 'admin' WHERE username = 'your_username';
```

## Chạy test

```bash
pytest
```

Test dùng SQLite in-memory riêng (qua `tests/conftest.py`), không đụng vào database
thật đang cấu hình trong `.env`.
