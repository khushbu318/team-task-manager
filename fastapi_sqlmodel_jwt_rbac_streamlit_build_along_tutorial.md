# Build-Along Tutorial: Team Task Manager

> **Goal:** Build one complete project from an empty folder to a working application while learning FastAPI, SQLModel, relationships, JWT authentication, RBAC, Streamlit, and a production-style 3-layer backend.
>
> **Important:** This version is intentionally written as a **build-along tutorial**. It does not repeat the conceptual material from the earlier tutorial. Instead, every phase follows:
>
> **Create → Paste → Run → Verify → Understand → Continue**

---

# 0. What We Are Building

We will build:

```text
                 ┌──────────────────────┐
                 │      Streamlit UI    │
                 │  Login + Dashboard   │
                 └──────────┬───────────┘
                            │ HTTP
                            ▼
                 ┌──────────────────────┐
                 │      FastAPI         │
                 │       Routes         │
                 └──────────┬───────────┘
                            ▼
                 ┌──────────────────────┐
                 │       Services       │
                 │ Business Rules       │
                 └──────────┬───────────┘
                            ▼
                 ┌──────────────────────┐
                 │     Repositories     │
                 │      SQLModel        │
                 └──────────┬───────────┘
                            ▼
                 ┌──────────────────────┐
                 │       SQLite         │
                 │       Database       │
                 └──────────────────────┘
```

The application has:

- `team_lead`
- `developer`

A team lead can:

- create tasks
- assign tasks to developers
- see all tasks
- update tasks

A developer can:

- see their own assigned tasks
- update their own task
- change status
- update current stage
- add blockers/errors
- report permission issues

A developer cannot:

- create a task
- edit another developer's task

---

# 1. Prerequisites

Install:

- Python 3.11+
- VS Code or another editor
- A terminal

Check Python:

```bash
python --version
```

Expected:

```text
Python 3.11.x
```

---

# 2. Create the Project

Create a folder:

```bash
mkdir team-task-manager
cd team-task-manager
```

Create this structure:

```text
team-task-manager/
│
├── backend/
│   └── app/
│       ├── __init__.py
│       ├── main.py
│       │
│       ├── core/
│       │   ├── __init__.py
│       │   ├── config.py
│       │   └── security.py
│       │
│       ├── db/
│       │   ├── __init__.py
│       │   └── session.py
│       │
│       ├── models/
│       │   ├── __init__.py
│       │   ├── user.py
│       │   └── task.py
│       │
│       ├── schemas/
│       │   ├── __init__.py
│       │   ├── auth.py
│       │   └── task.py
│       │
│       ├── repositories/
│       │   ├── __init__.py
│       │   ├── user_repository.py
│       │   └── task_repository.py
│       │
│       ├── services/
│       │   ├── __init__.py
│       │   ├── auth_service.py
│       │   └── task_service.py
│       │
│       └── api/
│           ├── __init__.py
│           ├── deps.py
│           └── routes/
│               ├── __init__.py
│               ├── auth.py
│               └── tasks.py
│
├── frontend/
│   ├── api_client.py
│   └── streamlit_app.py
│
├── scripts/
│   └── seed.py
│
├── requirements.txt
└── .env
```

Create empty `__init__.py` files wherever shown.

---

# 3. Create the Virtual Environment

From the project root:

```bash
python -m venv venv
```

Activate it.

### Windows

```bash
venv\Scripts\activate
```

### macOS/Linux

```bash
source venv/bin/activate
```

You should see something similar to:

```text
(venv)
```

---

# 4. Install Dependencies

Create:

```text
requirements.txt
```

Add:

```text
fastapi
uvicorn[standard]
sqlmodel
python-jose[cryptography]
pwdlib[argon2]
python-multipart
python-dotenv
streamlit
requests
```

Install:

```bash
pip install -r requirements.txt
```

Verify:

```bash
pip list
```

---

# 5. Configuration

Create:

```text
backend/app/core/config.py
```

```python
import os

from dotenv import load_dotenv

load_dotenv()


DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "sqlite:///./team_tasks.db",
)

JWT_SECRET_KEY = os.getenv(
    "JWT_SECRET_KEY",
    "dev-only-change-this-secret",
)

JWT_ALGORITHM = "HS256"

ACCESS_TOKEN_EXPIRE_MINUTES = int(
    os.getenv(
        "ACCESS_TOKEN_EXPIRE_MINUTES",
        "60",
    )
)
```

Create `.env`:

```env
DATABASE_URL=sqlite:///./team_tasks.db
JWT_SECRET_KEY=replace-this-with-a-long-random-secret
ACCESS_TOKEN_EXPIRE_MINUTES=60
```

> For learning, this is enough. In production, secrets should come from a proper secret-management system and should never be committed to Git.

---

# 6. First FastAPI Application

Before adding the database, make sure FastAPI works.

Create:

```text
backend/app/main.py
```

```python
from fastapi import FastAPI


app = FastAPI(
    title="Team Task Manager API",
)


@app.get("/")
def root():
    return {
        "message": "Team Task Manager API is running"
    }
```

Start the server from the project root:

```bash
uvicorn backend.app.main:app --reload
```

Open:

```text
http://127.0.0.1:8000
```

Expected:

```json
{
  "message": "Team Task Manager API is running"
}
```

Open Swagger:

```text
http://127.0.0.1:8000/docs
```

### Checkpoint

At this point:

```text
Browser
   ↓
FastAPI
   ↓
GET /
   ↓
JSON response
```

Do not continue until this works.

---

# 7. Create the Database Session

Now add SQLModel.

Create:

```text
backend/app/db/session.py
```

```python
from sqlmodel import Session, SQLModel, create_engine

from backend.app.core.config import DATABASE_URL


connect_args = {}

if DATABASE_URL.startswith("sqlite"):
    connect_args = {
        "check_same_thread": False
    }


engine = create_engine(
    DATABASE_URL,
    echo=False,
    connect_args=connect_args,
)


def create_db_and_tables():
    SQLModel.metadata.create_all(engine)


def get_session():
    with Session(engine) as session:
        yield session
```

### What did we just create?

```text
engine
   ↓
Database connection

Session
   ↓
Conversation with database

SQLModel.metadata
   ↓
Knows about our database tables
```

---

# 8. Create the User Model

Create:

```text
backend/app/models/user.py
```

```python
from __future__ import annotations

from enum import Enum

from sqlmodel import Field, Relationship, SQLModel


class UserRole(str, Enum):
    TEAM_LEAD = "team_lead"
    DEVELOPER = "developer"


class User(SQLModel, table=True):
    __tablename__ = "users"

    id: int | None = Field(
        default=None,
        primary_key=True,
    )

    username: str = Field(
        index=True,
        unique=True,
    )

    full_name: str

    password_hash: str

    role: UserRole = Field(
        default=UserRole.DEVELOPER
    )

    tasks: list["Task"] = Relationship(
        back_populates="assignee"
    )
```

Notice:

```python
tasks: list["Task"]
```

This says:

> One user can have many tasks.

---

# 9. Create the Task Model

Create:

```text
backend/app/models/task.py
```

```python
from __future__ import annotations

from enum import Enum

from sqlmodel import Field, Relationship, SQLModel


class TaskStatus(str, Enum):
    TODO = "todo"
    IN_PROGRESS = "in_progress"
    BLOCKED = "blocked"
    COMPLETED = "completed"


class Task(SQLModel, table=True):
    __tablename__ = "tasks"

    id: int | None = Field(
        default=None,
        primary_key=True,
    )

    title: str

    description: str | None = None

    status: TaskStatus = Field(
        default=TaskStatus.TODO
    )

    current_state: str | None = None

    blocker: str | None = None

    permission_issue: str | None = None

    assignee_id: int = Field(
        foreign_key="users.id"
    )

    assignee: "User" = Relationship(
        back_populates="tasks"
    )
```

We now have:

```text
User
  │
  │ one-to-many
  ▼
Task
```

One developer can have many tasks.

---

# 10. Make SQLModel Know Both Models

Update:

```text
backend/app/models/__init__.py
```

```python
from backend.app.models.user import User, UserRole
from backend.app.models.task import Task, TaskStatus

__all__ = [
    "User",
    "UserRole",
    "Task",
    "TaskStatus",
]
```

The important part is that both models are imported before table creation.

---

# 11. Add Database Dependency to FastAPI

Update:

```text
backend/app/main.py
```

```python
from fastapi import FastAPI
from backend.app.db.session import create_db_and_tables
from contextlib import asynccontextmanager

@asynccontextmanager
async def lifespan(app: FastAPI):
    create_db_and_tables()
    yield


app = FastAPI(
    title="Team Task Manager API",
    version="1.0.0"
)


@app.get("/")
def root():
    return {
        'message':'Team Task Manager API is Running'
    }

```

Restart the server.

You should now see a new file:

```text
team_tasks.db
```

---

# 12. Verify the Tables

Install a SQLite viewer if desired, or use Python.

Run:

```bash
python
```

Then:

```python
from sqlmodel import Session, select

from backend.app.db.session import engine
from backend.app.models import User, Task

with Session(engine) as session:
    print(session.exec(select(User)).all())
    print(session.exec(select(Task)).all())
```

Expected:

```text
[]
[]
```

The tables exist, but there are no records yet.

Exit:

```python
exit()
```

---

# 13. Password Security

Never store:

```text
password = "dev123"
```

in the database.

Store a password hash instead.

Create:

```text
backend/app/core/security.py
```

```python
from datetime import datetime, timedelta, timezone

from jose import JWTError, jwt
from pwdlib import PasswordHash

from backend.app.core.config import (
    ACCESS_TOKEN_EXPIRE_MINUTES,
    JWT_ALGORITHM,
    JWT_SECRET_KEY,
)


password_hash = PasswordHash.recommended()


def hash_password(password: str) -> str:
    return password_hash.hash(password)


def verify_password(
    plain_password: str,
    hashed_password: str,
) -> bool:
    return password_hash.verify(
        plain_password,
        hashed_password,
    )


def create_access_token(
    user_id: int,
    username: str,
    role: str,
) -> str:

    expire = datetime.now(
        timezone.utc
    ) + timedelta(
        minutes=ACCESS_TOKEN_EXPIRE_MINUTES
    )

    payload = {
        "sub": str(user_id),
        "username": username,
        "role": role,
        "exp": expire,
    }

    return jwt.encode(
        payload,
        JWT_SECRET_KEY,
        algorithm=JWT_ALGORITHM,
    )


def decode_access_token(token: str) -> dict:
    return jwt.decode(
        token,
        JWT_SECRET_KEY,
        algorithms=[JWT_ALGORITHM],
    )
```

---

# 14. Understand the Password Flow

When a user registers:

```text
"dev123"
   ↓
hash_password()
   ↓
"$argon2id$..."
   ↓
database
```

During login:

```text
user enters "dev123"
          ↓
verify_password()
          ↓
database hash
          ↓
True / False
```

The original password is not stored.

---

# 15. Authentication Schemas

Create:

```text
backend/app/schemas/auth.py
```

```python
from pydantic import BaseModel


class LoginRequest(BaseModel):
    username: str
    password: str


class TokenResponse(BaseModel):
    access_token: str
    token_type: str
```

---

# 16. Task Schemas

Create:

```text
backend/app/schemas/task.py
```

```python
from pydantic import BaseModel

from backend.app.models.task import TaskStatus


class TaskCreate(BaseModel):
    title: str
    description: str | None = None
    assignee_id: int


class TaskUpdate(BaseModel):
    status: TaskStatus | None = None
    current_state: str | None = None
    blocker: str | None = None
    permission_issue: str | None = None


class TaskResponse(BaseModel):
    id: int
    title: str
    description: str | None
    status: TaskStatus
    current_state: str | None
    blocker: str | None
    permission_issue: str | None
    assignee_id: int
```

---

# 17. Repository Layer

The repository talks to the database.

It should not contain JWT rules.

It should not decide whether the user is a team lead.

It should focus on database operations.

Create:

```text
backend/app/repositories/user_repository.py
```

```python
from sqlmodel import Session, select

from backend.app.models.user import User


class UserRepository:

    def __init__(self, session: Session):
        self.session = session

    def get_by_username(
        self,
        username: str,
    ) -> User | None:

        statement = select(User).where(
            User.username == username
        )

        return self.session.exec(
            statement
        ).first()

    def get_by_id(
        self,
        user_id: int,
    ) -> User | None:

        return self.session.get(
            User,
            user_id,
        )

    def create(
        self,
        user: User,
    ) -> User:

        self.session.add(user)
        self.session.commit()
        self.session.refresh(user)

        return user
```

---

# 18. Task Repository

Create:

```text
backend/app/repositories/task_repository.py
```

```python
from sqlmodel import Session, select

from backend.app.models.task import Task


class TaskRepository:

    def __init__(self, session: Session):
        self.session = session

    def create(self, task: Task) -> Task:

        self.session.add(task)
        self.session.commit()
        self.session.refresh(task)

        return task

    def get_by_id(
        self,
        task_id: int,
    ) -> Task | None:

        return self.session.get(
            Task,
            task_id,
        )

    def get_all(self) -> list[Task]:

        statement = select(Task)

        return list(
            self.session.exec(statement)
        )

    def get_for_user(
        self,
        user_id: int,
    ) -> list[Task]:

        statement = select(Task).where(
            Task.assignee_id == user_id
        )

        return list(
            self.session.exec(statement)
        )

    def save(self, task: Task) -> Task:

        self.session.add(task)
        self.session.commit()
        self.session.refresh(task)

        return task
```

---

# 19. Why Do We Need Repositories?

Without repositories:

```text
Router
  ↓
SQL queries everywhere
  ↓
Messy code
```

With repositories:

```text
Router
   ↓
Service
   ↓
Repository
   ↓
Database
```

Now database logic has one home.

---

# 20. Authentication Service

Create:

```text
backend/app/services/auth_service.py
```

```python
from fastapi import HTTPException, status

from backend.app.core.security import (
    create_access_token,
    verify_password,
)
from backend.app.repositories.user_repository import (
    UserRepository,
)


class AuthService:

    def __init__(
        self,
        user_repository: UserRepository,
    ):
        self.user_repository = user_repository

    def login(
        self,
        username: str,
        password: str,
    ) -> str:

        user = self.user_repository.get_by_username(
            username
        )

        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid username or password",
            )

        if not verify_password(
            password,
            user.password_hash,
        ):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid username or password",
            )

        return create_access_token(
            user_id=user.id,
            username=user.username,
            role=user.role.value,
        )
```

---

# 21. Task Service

This is where business rules belong.

Create:

```text
backend/app/services/task_service.py
```

```python
from fastapi import HTTPException, status

from backend.app.models.task import Task
from backend.app.models.user import User, UserRole
from backend.app.repositories.task_repository import (
    TaskRepository,
)
from backend.app.schemas.task import (
    TaskCreate,
    TaskUpdate,
)


class TaskService:

    def __init__(
        self,
        task_repository: TaskRepository,
    ):
        self.task_repository = task_repository

    def create_task(
        self,
        current_user: User,
        data: TaskCreate,
    ) -> Task:

        if current_user.role != UserRole.TEAM_LEAD:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Only team leads can create tasks",
            )

        task = Task(
            title=data.title,
            description=data.description,
            assignee_id=data.assignee_id,
        )

        return self.task_repository.create(task)

    def get_tasks_for_user(
        self,
        current_user: User,
    ) -> list[Task]:

        if current_user.role == UserRole.TEAM_LEAD:
            return self.task_repository.get_all()

        return self.task_repository.get_for_user(
            current_user.id
        )

    def update_task(
        self,
        current_user: User,
        task_id: int,
        data: TaskUpdate,
    ) -> Task:

        task = self.task_repository.get_by_id(
            task_id
        )

        if not task:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Task not found",
            )

        # Object-level authorization.
        if (
            current_user.role != UserRole.TEAM_LEAD
            and task.assignee_id != current_user.id
        ):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You can update only your own tasks",
            )

        if data.status is not None:
            task.status = data.status

        if data.current_state is not None:
            task.current_state = data.current_state

        if data.blocker is not None:
            task.blocker = data.blocker

        if data.permission_issue is not None:
            task.permission_issue = data.permission_issue

        return self.task_repository.save(task)
```

---

# 22. The Most Important Authorization Rule

This line is extremely important:

```python
task.assignee_id != current_user.id
```

Why?

Imagine:

```text
Dev1
  ↓
Task #10
  ↓
assignee_id = 2
```

Dev2 has:

```text
current_user.id = 2
```

So Dev2 can edit it.

Dev1 has:

```text
current_user.id = 1
```

Therefore:

```text
1 != 2
```

Access denied.

This is **object-level authorization**.

---

# 23. Authentication Dependency

Create:

```text
backend/app/api/deps.py
```

```python
from typing import Callable

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError
from sqlmodel import Session

from backend.app.core.security import decode_access_token
from backend.app.db.session import get_session
from backend.app.models.user import User, UserRole
from backend.app.repositories.user_repository import (
    UserRepository,
)


oauth2_scheme = OAuth2PasswordBearer(
    tokenUrl="/auth/login"
)


def get_current_user(
    token: str = Depends(oauth2_scheme),
    session: Session = Depends(get_session),
) -> User:

    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Invalid or expired token",
        headers={
            "WWW-Authenticate": "Bearer"
        },
    )

    try:
        payload = decode_access_token(token)

        user_id = payload.get("sub")

        if user_id is None:
            raise credentials_exception

        user_id = int(user_id)

    except (
        JWTError,
        ValueError,
        TypeError,
    ):
        raise credentials_exception

    repository = UserRepository(session)

    user = repository.get_by_id(user_id)

    if not user:
        raise credentials_exception

    return user


def require_role(
    required_role: UserRole,
) -> Callable:

    def role_checker(
        current_user: User = Depends(
            get_current_user
        ),
    ) -> User:

        if current_user.role != required_role:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Insufficient permissions",
            )

        return current_user

    return role_checker
```

---

# 24. Understand the Dependency Chain

When an endpoint says:

```python
current_user: User = Depends(get_current_user)
```

FastAPI performs:

```text
Request
  ↓
Read Authorization header
  ↓
Extract Bearer token
  ↓
Decode JWT
  ↓
Read user ID
  ↓
Find user in DB
  ↓
Return User object
  ↓
Endpoint receives current_user
```

This means the endpoint does not need to manually repeat authentication code.

---

# 25. Authentication Router

Create:

```text
backend/app/api/routes/auth.py
```

```python
from fastapi import APIRouter, Depends
from sqlmodel import Session

from backend.app.db.session import get_session
from backend.app.repositories.user_repository import (
    UserRepository,
)
from backend.app.schemas.auth import (
    LoginRequest,
    TokenResponse,
)
from backend.app.services.auth_service import (
    AuthService,
)


router = APIRouter(
    prefix="/auth",
    tags=["Authentication"],
)


@router.post(
    "/login",
    response_model=TokenResponse,
)
def login(
    data: LoginRequest,
    session: Session = Depends(get_session),
):

    repository = UserRepository(session)

    service = AuthService(repository)

    token = service.login(
        username=data.username,
        password=data.password,
    )

    return TokenResponse(
        access_token=token,
        token_type="bearer",
    )
```

---

# 26. Task Router

Create:

```text
backend/app/api/routes/tasks.py
```

```python
from fastapi import APIRouter, Depends
from sqlmodel import Session

from backend.app.api.deps import get_current_user
from backend.app.db.session import get_session
from backend.app.models.user import User
from backend.app.repositories.task_repository import (
    TaskRepository,
)
from backend.app.schemas.task import (
    TaskCreate,
    TaskResponse,
    TaskUpdate,
)
from backend.app.services.task_service import (
    TaskService,
)


router = APIRouter(
    prefix="/tasks",
    tags=["Tasks"],
)


def get_task_service(
    session: Session = Depends(get_session),
) -> TaskService:

    repository = TaskRepository(session)

    return TaskService(repository)


@router.get(
    "",
    response_model=list[TaskResponse],
)
def get_tasks(
    current_user: User = Depends(
        get_current_user
    ),
    service: TaskService = Depends(
        get_task_service
    ),
):

    return service.get_tasks_for_user(
        current_user
    )


@router.post(
    "",
    response_model=TaskResponse,
)
def create_task(
    data: TaskCreate,
    current_user: User = Depends(
        get_current_user
    ),
    service: TaskService = Depends(
        get_task_service
    ),
):

    return service.create_task(
        current_user=current_user,
        data=data,
    )


@router.patch(
    "/{task_id}",
    response_model=TaskResponse,
)
def update_task(
    task_id: int,
    data: TaskUpdate,
    current_user: User = Depends(
        get_current_user
    ),
    service: TaskService = Depends(
        get_task_service
    ),
):

    return service.update_task(
        current_user=current_user,
        task_id=task_id,
        data=data,
    )
```

---

# 27. Connect the Routers

Replace `backend/app/main.py` with:

```python
from fastapi import FastAPI

from backend.app.api.routes.auth import router as auth_router
from backend.app.api.routes.tasks import router as task_router
from backend.app.db.session import create_db_and_tables


app = FastAPI(
    title="Team Task Manager API",
)


@app.on_event("startup")
def on_startup():
    create_db_and_tables()


app.include_router(auth_router)
app.include_router(task_router)


@app.get("/")
def root():
    return {
        "message": "Team Task Manager API is running"
    }
```

Restart:

```bash
uvicorn backend.app.main:app --reload
```

Go to:

```text
http://127.0.0.1:8000/docs
```

You should now see:

```text
Authentication
    POST /auth/login

Tasks
    GET  /tasks
    POST /tasks
    PATCH /tasks/{task_id}
```

---

# 28. Seed the Users

Create:

```text
scripts/seed.py
```

```python
from sqlmodel import Session, select

from backend.app.core.security import hash_password
from backend.app.db.session import (
    create_db_and_tables,
    engine,
)
from backend.app.models.user import User, UserRole


USERS = [
    {
        "username": "alice",
        "full_name": "Alice Team Lead",
        "password": "lead123",
        "role": UserRole.TEAM_LEAD,
    },
    {
        "username": "dev1",
        "full_name": "Developer One",
        "password": "dev123",
        "role": UserRole.DEVELOPER,
    },
    {
        "username": "dev2",
        "full_name": "Developer Two",
        "password": "dev123",
        "role": UserRole.DEVELOPER,
    },
    {
        "username": "dev3",
        "full_name": "Developer Three",
        "password": "dev123",
        "role": UserRole.DEVELOPER,
    },
]


def seed():

    create_db_and_tables()

    with Session(engine) as session:

        for item in USERS:

            existing = session.exec(
                select(User).where(
                    User.username == item["username"]
                )
            ).first()

            if existing:
                print(
                    f"Skipping {item['username']} "
                    f"(already exists)"
                )
                continue

            user = User(
                username=item["username"],
                full_name=item["full_name"],
                password_hash=hash_password(
                    item["password"]
                ),
                role=item["role"],
            )

            session.add(user)

        session.commit()

    print("Seed completed.")


if __name__ == "__main__":
    seed()
```

Run:

```bash
python scripts/seed.py
```

Expected:

```text
Seed completed.
```

Run again:

```bash
python scripts/seed.py
```

Expected:

```text
Skipping alice (already exists)
Skipping dev1 (already exists)
Skipping dev2 (already exists)
Skipping dev3 (already exists)
Seed completed.
```

---

# 29. Test Login

Open Swagger:

```text
http://127.0.0.1:8000/docs
```

Open:

```text
POST /auth/login
```

Send:

```json
{
  "username": "alice",
  "password": "lead123"
}
```

You should receive:

```json
{
  "access_token": "eyJ...",
  "token_type": "bearer"
}
```

Copy the token.

---

# 30. Understand the JWT

The token looks like:

```text
xxxxx.yyyyy.zzzzz
```

Conceptually:

```text
HEADER
   .
PAYLOAD
   .
SIGNATURE
```

The payload contains information such as:

```json
{
  "sub": "1",
  "username": "alice",
  "role": "team_lead",
  "exp": "..."
}
```

The client sends:

```http
Authorization: Bearer <token>
```

The server validates it.

---

# 31. Test Authentication in Swagger

Click:

```text
Authorize
```

Paste:

```text
Bearer YOUR_TOKEN
```

Then call:

```text
GET /tasks
```

Expected:

```json
[]
```

Why?

Alice is authenticated, but no tasks exist yet.

---

# 32. Test RBAC: Developer Cannot Create

Login as:

```text
username: dev1
password: dev123
```

Copy the token.

Authorize Swagger with the developer token.

Call:

```text
POST /tasks
```

Try:

```json
{
  "title": "Build planner API",
  "description": "Implement planner microservice endpoints",
  "assignee_id": 2
}
```

Expected:

```text
403 Forbidden
```

Response:

```json
{
  "detail": "Only team leads can create tasks"
}
```

This is the first important RBAC checkpoint.

---

# 33. Create a Task as Team Lead

Login as:

```text
alice
lead123
```

Find developer IDs if needed.

You can use:

```text
GET /docs
```

or inspect the database.

Assume:

```text
alice = 1
dev1  = 2
dev2  = 3
dev3  = 4
```

Create:

```json
{
  "title": "Build planner API",
  "description": "Implement planner microservice endpoints",
  "assignee_id": 2
}
```

Expected:

```json
{
  "id": 1,
  "title": "Build planner API",
  "description": "Implement planner microservice endpoints",
  "status": "todo",
  "current_state": null,
  "blocker": null,
  "permission_issue": null,
  "assignee_id": 2
}
```

---

# 34. Developer Sees Their Task

Login as:

```text
dev1
dev123
```

Call:

```text
GET /tasks
```

Expected:

```json
[
  {
    "id": 1,
    "title": "Build planner API",
    "status": "todo",
    "assignee_id": 2
  }
]
```

Now login as:

```text
dev2
dev123
```

Call:

```text
GET /tasks
```

Expected:

```json
[]
```

Why?

The service applies:

```python
get_for_user(current_user.id)
```

Developers only see their own tasks.

---

# 35. Developer Updates Their Task

Login as `dev1`.

Call:

```text
PATCH /tasks/1
```

Send:

```json
{
  "status": "in_progress",
  "current_state": "Implementing API endpoints"
}
```

Expected:

```json
{
  "id": 1,
  "status": "in_progress",
  "current_state": "Implementing API endpoints"
}
```

Now add a blocker:

```json
{
  "status": "blocked",
  "current_state": "Waiting for Redis configuration",
  "blocker": "Redis connection details are not available"
}
```

---

# 36. Test Object-Level Authorization

Login as `dev2`.

Try:

```text
PATCH /tasks/1
```

Send:

```json
{
  "status": "completed"
}
```

Expected:

```text
403 Forbidden
```

Because:

```text
Task #1
assignee_id = dev1

Current user
id = dev2
```

Therefore:

```text
dev2 != dev1
```

Access denied.

---

# 37. Now Add the Streamlit Frontend

Create:

```text
frontend/api_client.py
```

```python
import requests


API_URL = "http://127.0.0.1:8000"


class APIClient:

    def __init__(self, token: str | None = None):
        self.token = token

    @property
    def headers(self):

        if not self.token:
            return {}

        return {
            "Authorization": (
                f"Bearer {self.token}"
            )
        }

    def login(
        self,
        username: str,
        password: str,
    ):

        response = requests.post(
            f"{API_URL}/auth/login",
            json={
                "username": username,
                "password": password,
            },
            timeout=10,
        )

        response.raise_for_status()

        return response.json()

    def get_tasks(self):

        response = requests.get(
            f"{API_URL}/tasks",
            headers=self.headers,
            timeout=10,
        )

        response.raise_for_status()

        return response.json()

    def create_task(
        self,
        title: str,
        description: str,
        assignee_id: int,
    ):

        response = requests.post(
            f"{API_URL}/tasks",
            headers=self.headers,
            json={
                "title": title,
                "description": description,
                "assignee_id": assignee_id,
            },
            timeout=10,
        )

        return response

    def update_task(
        self,
        task_id: int,
        payload: dict,
    ):

        response = requests.patch(
            f"{API_URL}/tasks/{task_id}",
            headers=self.headers,
            json=payload,
            timeout=10,
        )

        return response
```

---

# 38. Build the Streamlit Login

Create:

```text
frontend/streamlit_app.py
```

```python
import base64
import json

import streamlit as st

from frontend.api_client import APIClient


st.set_page_config(
    page_title="Team Task Manager",
    layout="wide",
)


if "token" not in st.session_state:
    st.session_state.token = None

if "username" not in st.session_state:
    st.session_state.username = None


def decode_jwt_payload(token: str):

    try:
        payload = token.split(".")[1]

        padding = "=" * (
            4 - len(payload) % 4
        )

        decoded = base64.urlsafe_b64decode(
            payload + padding
        )

        return json.loads(
            decoded.decode("utf-8")
        )

    except Exception:
        return {}


st.title("Team Task Manager")

st.caption(
    "FastAPI + SQLModel + JWT + RBAC + Streamlit"
)


if not st.session_state.token:

    st.subheader("Login")

    username = st.text_input(
        "Username"
    )

    password = st.text_input(
        "Password",
        type="password",
    )

    if st.button("Login"):

        client = APIClient()

        try:

            result = client.login(
                username,
                password,
            )

            st.session_state.token = (
                result["access_token"]
            )

            st.session_state.username = (
                username
            )

            st.rerun()

        except Exception as exc:

            st.error(
                f"Login failed: {exc}"
            )

else:

    token = st.session_state.token

    payload = decode_jwt_payload(token)

    role = payload.get(
        "role",
        "unknown",
    )

    user_id = payload.get(
        "sub",
        "unknown",
    )

    st.sidebar.success(
        f"Logged in as: {st.session_state.username}"
    )

    st.sidebar.write(
        f"User ID: {user_id}"
    )

    st.sidebar.write(
        f"Role: {role}"
    )

    if st.sidebar.button("Logout"):

        st.session_state.token = None
        st.session_state.username = None

        st.rerun()

    client = APIClient(token)

    st.header("JWT + RBAC Dashboard")

    # -------------------------------------------------
    # JWT SECTION
    # -------------------------------------------------

    st.subheader("1. What is inside the JWT?")

    st.json(payload)

    # -------------------------------------------------
    # AUTHORIZATION FLOW
    # -------------------------------------------------

    st.subheader("2. Request Pipeline")

    steps = [
        "Streamlit sends HTTP request",
        "Authorization: Bearer <JWT>",
        "FastAPI extracts token",
        "JWT signature is verified",
        "JWT payload is decoded",
        "User is loaded from database",
        "RBAC / ownership rules are checked",
        "Service executes business logic",
        "Repository talks to SQLModel",
        "Database returns data",
    ]

    for index, step in enumerate(
        steps,
        start=1,
    ):

        st.write(
            f"**{index}.** {step}"
        )

    # -------------------------------------------------
    # TASKS
    # -------------------------------------------------

    st.subheader("3. My Tasks")

    try:

        tasks = client.get_tasks()

        if not tasks:

            st.info(
                "No tasks available."
            )

        for task in tasks:

            with st.container(
                border=True
            ):

                st.write(
                    f"### #{task['id']} "
                    f"{task['title']}"
                )

                st.write(
                    f"Status: "
                    f"**{task['status']}**"
                )

                if task["description"]:
                    st.write(
                        task["description"]
                    )

                if task["current_state"]:
                    st.write(
                        "Stage: "
                        f"{task['current_state']}"
                    )

                if task["blocker"]:
                    st.warning(
                        "Blocker: "
                        f"{task['blocker']}"
                    )

                if task["permission_issue"]:
                    st.error(
                        "Permission issue: "
                        f"{task['permission_issue']}"
                    )

                # Developers can update their own tasks.
                # Team leads can update any task.
                with st.form(
                    f"update_{task['id']}"
                ):

                    status = st.selectbox(
                        "Status",
                        [
                            "todo",
                            "in_progress",
                            "blocked",
                            "completed",
                        ],
                        index=[
                            "todo",
                            "in_progress",
                            "blocked",
                            "completed",
                        ].index(
                            task["status"]
                        ),
                    )

                    stage = st.text_input(
                        "Current stage",
                        value=(
                            task["current_state"]
                            or ""
                        ),
                    )

                    blocker = st.text_input(
                        "Blocker",
                        value=(
                            task["blocker"]
                            or ""
                        ),
                    )

                    permission_issue = (
                        st.text_input(
                            "Permission issue",
                            value=(
                                task[
                                    "permission_issue"
                                ]
                                or ""
                            ),
                        )
                    )

                    submitted = st.form_submit_button(
                        "Update Task"
                    )

                    if submitted:

                        response = (
                            client.update_task(
                                task["id"],
                                {
                                    "status": status,
                                    "current_state": (
                                        stage or None
                                    ),
                                    "blocker": (
                                        blocker or None
                                    ),
                                    "permission_issue": (
                                        permission_issue
                                        or None
                                    ),
                                },
                            )
                        )

                        if response.ok:

                            st.success(
                                "Task updated"
                            )

                            st.rerun()

                        else:

                            st.error(
                                response.text
                            )

    except Exception as exc:

        st.error(
            f"Could not load tasks: {exc}"
        )

    # -------------------------------------------------
    # TEAM LEAD AREA
    # -------------------------------------------------

    if role == "team_lead":

        st.divider()

        st.subheader(
            "4. Team Lead: Create Task"
        )

        with st.form("create_task"):

            title = st.text_input(
                "Task title"
            )

            description = st.text_area(
                "Description"
            )

            assignee_id = st.number_input(
                "Developer User ID",
                min_value=1,
                step=1,
            )

            submitted = st.form_submit_button(
                "Create Task"
            )

            if submitted:

                response = (
                    client.create_task(
                        title=title,
                        description=description,
                        assignee_id=int(
                            assignee_id
                        ),
                    )
                )

                if response.ok:

                    st.success(
                        "Task created"
                    )

                    st.rerun()

                else:

                    st.error(
                        response.text
                    )

    else:

        st.divider()

        st.info(
            "Developer role: task creation "
            "is disabled."
        )
```

---

# 39. Important Streamlit Detail

Run Streamlit from the project root:

```bash
streamlit run frontend/streamlit_app.py
```

Do not run it from inside `frontend/` if you want imports to work exactly as written.

Open the URL Streamlit displays, normally:

```text
http://localhost:8501
```

---

# 40. Test the Complete UI

Login:

```text
alice
lead123
```

You should see:

```text
JWT payload
Request Pipeline
My Tasks
Team Lead: Create Task
```

Login as:

```text
dev1
dev123
```

You should see:

```text
JWT payload
Request Pipeline
My Tasks
Developer role: task creation is disabled
```

This demonstrates that the UI changes based on the authenticated role.

---

# 41. Important: UI Security vs Backend Security

The Streamlit UI hides:

```text
Create Task
```

for developers.

But this is **not the actual security boundary**.

A malicious user could still manually send:

```http
POST /tasks
```

Therefore the backend must still enforce:

```python
if current_user.role != UserRole.TEAM_LEAD:
    raise HTTPException(403)
```

The correct mental model is:

```text
Frontend restriction
       +
Backend authorization
       =
Good application
```

Never trust the frontend alone.

---

# 42. Make the JWT Flow Visible

The Streamlit dashboard already displays:

```text
JWT payload
```

and:

```text
1. Streamlit sends HTTP request
2. Authorization: Bearer <JWT>
3. FastAPI extracts token
4. JWT signature is verified
5. JWT payload is decoded
6. User is loaded from database
7. RBAC / ownership rules are checked
8. Service executes business logic
9. Repository talks to SQLModel
10. Database returns data
```

When teaching this project, explain one box at a time.

---

# 43. Build the Full Mental Execution Flow

Suppose `dev1` clicks:

```text
Update Task
```

The real flow is:

```text
┌───────────────────────┐
│ Streamlit             │
│ Update Task button    │
└──────────┬────────────┘
           │
           │ PATCH /tasks/1
           │ Authorization: Bearer JWT
           ▼
┌───────────────────────┐
│ FastAPI Router        │
│ update_task()         │
└──────────┬────────────┘
           │
           ▼
┌───────────────────────┐
│ get_current_user()    │
│                       │
│ Verify JWT            │
│ Find user             │
└──────────┬────────────┘
           │
           ▼
┌───────────────────────┐
│ TaskService           │
│                       │
│ Is this user's task?  │
└──────────┬────────────┘
           │
           ▼
┌───────────────────────┐
│ TaskRepository        │
│                       │
│ Load + save Task      │
└──────────┬────────────┘
           │
           ▼
┌───────────────────────┐
│ SQLite                │
└───────────────────────┘
```

---

# 44. Why Three Layers?

The backend is:

```text
Router
Service
Repository
```

### Router

Answers:

> What HTTP request came in?

Example:

```python
@router.patch("/{task_id}")
```

### Service

Answers:

> What business rule should happen?

Example:

```python
if task.assignee_id != current_user.id:
    raise HTTPException(403)
```

### Repository

Answers:

> How do I read/write the database?

Example:

```python
self.session.get(Task, task_id)
```

The separation is:

```text
HTTP
 ↓
Business logic
 ↓
Database
```

---

# 45. What Happens If We Put Everything in the Router?

Bad example:

```python
@router.patch("/{task_id}")
def update_task(...):

    # decode JWT

    # find user

    # check role

    # check ownership

    # SQL query

    # update database

    # commit

    # return response
```

The router becomes huge.

Better:

```python
@router.patch("/{task_id}")
def update_task(...):

    return service.update_task(
        current_user,
        task_id,
        data,
    )
```

The router stays focused on HTTP.

---

# 46. Add a `/me` Endpoint

This is useful for teaching authentication.

Update:

```text
backend/app/api/routes/auth.py
```

Add:

```python
from backend.app.api.deps import get_current_user
from backend.app.models.user import User
```

Then add:

```python
@router.get("/me")
def me(
    current_user: User = Depends(
        get_current_user
    ),
):
    return {
        "id": current_user.id,
        "username": current_user.username,
        "full_name": current_user.full_name,
        "role": current_user.role,
    }
```

Now:

```text
GET /auth/me
```

returns the currently authenticated user.

This is an excellent endpoint for understanding:

```text
JWT
 ↓
current user
 ↓
database user
```

---

# 47. RBAC vs Ownership

There are two different checks.

## RBAC

Question:

> Is this user allowed to perform this type of operation?

Example:

```text
POST /tasks
```

Only:

```text
team_lead
```

is allowed.

---

## Ownership

Question:

> Does this particular resource belong to this user?

Example:

```text
PATCH /tasks/1
```

A developer may update it only if:

```python
task.assignee_id == current_user.id
```

So:

```text
RBAC
+
Object-level authorization
```

are different concepts.

---

# 48. Add a Simple Authorization Matrix

Keep this table beside the project while testing.

| Action | Team Lead | Developer |
|---|---:|---:|
| Login | Yes | Yes |
| View own tasks | Yes | Yes |
| View all tasks | Yes | No |
| Create task | Yes | No |
| Assign task | Yes | No |
| Update own task | Yes | Yes |
| Update another developer's task | Yes | No |
| Change status | Yes | Yes |
| Add blocker | Yes | Yes |
| Add permission issue | Yes | Yes |

---

# 49. Test Matrix Manually

Perform these tests.

## Test 1

```text
Alice → login
```

Expected:

```text
200
```

## Test 2

```text
Dev1 → login
```

Expected:

```text
200
```

## Test 3

```text
Dev1 → POST /tasks
```

Expected:

```text
403
```

## Test 4

```text
Alice → POST /tasks
```

Expected:

```text
200
```

## Test 5

```text
Dev1 → GET /tasks
```

Expected:

```text
Only Dev1's tasks
```

## Test 6

```text
Dev2 → GET /tasks
```

Expected:

```text
Only Dev2's tasks
```

## Test 7

```text
Dev1 → PATCH Dev1's task
```

Expected:

```text
200
```

## Test 8

```text
Dev2 → PATCH Dev1's task
```

Expected:

```text
403
```

---

# 50. Common Errors

## Error: ModuleNotFoundError

If you see:

```text
ModuleNotFoundError: No module named 'backend'
```

Run commands from:

```text
team-task-manager/
```

Example:

```bash
uvicorn backend.app.main:app --reload
```

not:

```bash
cd backend/app
uvicorn main:app
```

---

## Error: Database Has No Tables

Run:

```bash
python scripts/seed.py
```

This calls:

```python
create_db_and_tables()
```

---

## Error: 401 Unauthorized

Check:

```text
Authorization: Bearer <JWT>
```

Make sure:

- token is not expired
- token is copied correctly
- username/password are correct
- server secret has not changed

---

## Error: 403 Forbidden

This usually means authentication worked but authorization failed.

Example:

```text
Authenticated: YES
Authorized: NO
```

That is different from:

```text
401
```

which generally means:

```text
Authentication failed
```

---

## Error: Streamlit Cannot Reach API

Make sure FastAPI is running:

```bash
uvicorn backend.app.main:app --reload
```

Then start Streamlit separately:

```bash
streamlit run frontend/streamlit_app.py
```

You need two terminals.

---

# 51. Run the Project Every Day

Terminal 1:

```bash
cd team-task-manager

venv\Scripts\activate

uvicorn backend.app.main:app --reload
```

Terminal 2:

```bash
cd team-task-manager

venv\Scripts\activate

streamlit run frontend/streamlit_app.py
```

If users are not seeded yet:

```bash
python scripts/seed.py
```

---

# 52. Final Project Structure

After completing this tutorial:

```text
team-task-manager/
│
├── backend/
│   └── app/
│       ├── __init__.py
│       ├── main.py
│       │
│       ├── core/
│       │   ├── __init__.py
│       │   ├── config.py
│       │   └── security.py
│       │
│       ├── db/
│       │   ├── __init__.py
│       │   └── session.py
│       │
│       ├── models/
│       │   ├── __init__.py
│       │   ├── user.py
│       │   └── task.py
│       │
│       ├── schemas/
│       │   ├── __init__.py
│       │   ├── auth.py
│       │   └── task.py
│       │
│       ├── repositories/
│       │   ├── __init__.py
│       │   ├── user_repository.py
│       │   └── task_repository.py
│       │
│       ├── services/
│       │   ├── __init__.py
│       │   ├── auth_service.py
│       │   └── task_service.py
│       │
│       └── api/
│           ├── __init__.py
│           ├── deps.py
│           └── routes/
│               ├── __init__.py
│               ├── auth.py
│               └── tasks.py
│
├── frontend/
│   ├── api_client.py
│   └── streamlit_app.py
│
├── scripts/
│   └── seed.py
│
├── requirements.txt
├── .env
└── team_tasks.db
```

---

# 53. What You Have Learned

By actually building this project, you have implemented:

```text
Python
   ↓
FastAPI
   ↓
API routes
   ↓
Dependency Injection
   ↓
SQLModel
   ↓
SQL database
   ↓
Relationships
   ↓
Repository pattern
   ↓
Service layer
   ↓
Password hashing
   ↓
JWT authentication
   ↓
Current-user dependency
   ↓
RBAC
   ↓
Object-level authorization
   ↓
Streamlit
   ↓
HTTP API client
   ↓
End-to-end application
```

---

# 54. Interview Explanation

If an interviewer asks:

> How did you structure this FastAPI application?

Answer:

```text
I separated the application into three main backend layers.

The router layer handles HTTP requests and responses.

The service layer contains business rules such as checking whether
a user has the required role or whether a developer owns the task.

The repository layer handles database operations through SQLModel.

Authentication is implemented using JWT. A FastAPI dependency extracts
and validates the JWT and loads the current user. RBAC is then applied
to protect operations such as task creation.

For developers, I also added object-level authorization so that a
developer can update only tasks assigned to them.
```

---

# 55. Interview Question: Why JWT?

A simple answer:

```text
JWT allows the server to verify the identity represented by a token
without requiring the client to send the username and password on
every request.
```

Request:

```text
Login
 ↓
JWT
 ↓
Every protected request:
Authorization: Bearer JWT
```

---

# 56. Interview Question: Authentication vs Authorization

Use this:

```text
Authentication:
"Who are you?"

Authorization:
"What are you allowed to do?"
```

In our project:

```text
JWT
 ↓
Authentication

Role + ownership checks
 ↓
Authorization
```

---

# 57. Interview Question: Why Service Layer?

Answer:

```text
I don't want business rules mixed with HTTP or database code.

For example, the rule that only a team lead can create tasks belongs
in the service layer. This makes the logic easier to test and reuse.
```

---

# 58. Interview Question: Why Repository Layer?

Answer:

```text
The repository isolates database access from business logic.

If I change how data is stored or how a query is implemented, the
service layer does not need to know those database details.
```

---

# 59. Interview Question: Why SQLModel Relationship?

Our model says:

```python
tasks: list["Task"] = Relationship(
    back_populates="assignee"
)
```

and:

```python
assignee: "User" = Relationship(
    back_populates="tasks"
)
```

This represents:

```text
User 1 ─────────── * Task
```

One user can have multiple tasks.

The database also stores:

```text
tasks.assignee_id
```

as the foreign key.

---

# 60. Next Upgrade: PostgreSQL

Once the SQLite version works, move to PostgreSQL.

Change:

```env
DATABASE_URL=postgresql+psycopg://user:password@localhost/team_tasks
```

Install:

```bash
pip install psycopg[binary]
```

The application architecture stays almost the same.

This is an important lesson:

```text
Application code
      ↓
Repository
      ↓
SQLModel
      ↓
Database
```

The repository boundary makes database changes easier.

---

# 61. Next Upgrade: Alembic

The current project uses:

```python
SQLModel.metadata.create_all(engine)
```

This is acceptable for learning.

For production, use migrations.

Typical production flow:

```text
Developer changes model
        ↓
Alembic migration
        ↓
Review migration
        ↓
Apply migration
        ↓
Database schema updated
```

Do not rely on `create_all()` as your production migration strategy.

---

# 62. Next Upgrade: Automated Tests

Add tests for:

```text
Authentication
RBAC
Ownership
CRUD
Invalid JWT
Expired JWT
Missing JWT
```

The most important authorization tests are:

```text
team lead creates task        → 200
developer creates task       → 403
developer updates own task   → 200
developer updates other's    → 403
```

---

# 63. Final Challenge: Build It Again Without Looking

After finishing once, delete your implementation code but keep the project structure.

Try rebuilding from memory.

You should be able to explain:

```text
1. How FastAPI receives a request
2. How dependency injection works
3. How SQLModel maps Python classes to tables
4. How User → Task relationship works
5. How password hashing works
6. How JWT is generated
7. How JWT is validated
8. How current_user is created
9. How RBAC works
10. How ownership authorization works
11. Why Router → Service → Repository exists
12. How Streamlit calls FastAPI
```

If you can rebuild it, you understand the concepts rather than just recognizing the code.

---

# 64. Final Architecture to Remember

```text
                    STREAMLIT
                        │
                        │ HTTP
                        ▼
              ┌───────────────────┐
              │      ROUTER       │
              │                   │
              │ HTTP concerns     │
              └─────────┬─────────┘
                        │
                        ▼
              ┌───────────────────┐
              │     SECURITY      │
              │                   │
              │ JWT               │
              │ Current User      │
              │ RBAC              │
              └─────────┬─────────┘
                        │
                        ▼
              ┌───────────────────┐
              │      SERVICE      │
              │                   │
              │ Business Rules    │
              │ Ownership         │
              │ Task Logic        │
              └─────────┬─────────┘
                        │
                        ▼
              ┌───────────────────┐
              │    REPOSITORY     │
              │                   │
              │ Database Queries  │
              └─────────┬─────────┘
                        │
                        ▼
              ┌───────────────────┐
              │     SQLMODEL      │
              │                   │
              │ Models + ORM      │
              └─────────┬─────────┘
                        │
                        ▼
                    DATABASE
```

The most important rule is:

```text
Router
  → Service
    → Repository
      → Database
```

And for security:

```text
Request
  → JWT
    → Current User
      → Role
        → Ownership
          → Business Logic
            → Database
```

---

# 65. Project Completion Checklist

Mark these only after you have actually tested them.

```text
[ ] Created Python virtual environment
[ ] Installed dependencies
[ ] Started FastAPI
[ ] Opened Swagger
[ ] Created SQLModel User
[ ] Created SQLModel Task
[ ] Created User → Task relationship
[ ] Created SQLite database
[ ] Seeded users
[ ] Implemented password hashing
[ ] Implemented login
[ ] Generated JWT
[ ] Validated JWT
[ ] Implemented get_current_user
[ ] Implemented team_lead role
[ ] Implemented developer role
[ ] Implemented RBAC
[ ] Implemented object-level authorization
[ ] Implemented repository layer
[ ] Implemented service layer
[ ] Implemented task CRUD
[ ] Started Streamlit
[ ] Displayed JWT payload
[ ] Displayed authentication flow
[ ] Displayed role
[ ] Implemented team-lead task creation
[ ] Implemented developer task updates
[ ] Tested developer → own task
[ ] Tested developer → another developer's task
[ ] Tested developer → create task
[ ] Tested team lead → create task
[ ] Understood 401 vs 403
[ ] Can explain Router → Service → Repository
[ ] Can explain JWT
[ ] Can explain RBAC
[ ] Can explain SQLModel relationships
```

---

# 66. The One-Sentence Mental Model

If you remember only one thing from this project, remember:

```text
FastAPI receives the request,
JWT identifies the user,
RBAC decides what role can do,
ownership decides which resource they can touch,
the service applies business rules,
the repository talks to the database,
and Streamlit gives us a visual way to use and understand the system.
```
