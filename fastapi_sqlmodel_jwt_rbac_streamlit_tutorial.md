# FastAPI + SQLModel + Relationships + JWT Authentication + RBAC + Streamlit
## Production-Style Tutorial: Development Team Task Management System

> **Goal:** Build one realistic application that teaches FastAPI, SQLModel, database relationships, JWT authentication, role-based access control (RBAC), a 3-layer architecture, and a Streamlit UI that visually explains what is happening behind the scenes.

---

# 1. What We Are Building

We will build a small **Development Team Task Management System**.

There is one **Team Lead** and multiple **Developers**.

The Team Lead creates tasks/todos for developers:

| User | Role | Responsibility |
|---|---|---|
| Alice | `team_lead` | Creates and manages tasks |
| Dev1 | `developer` | Microservice API Server |
| Dev2 | `developer` | Microservice Planner |
| Dev3 | `developer` | Microservice Redis |

Example tasks:

- Dev1 → Build authentication API in `api-server`
- Dev2 → Implement planner workflow in `planner`
- Dev3 → Implement Redis state management

Developers **cannot create tasks**.

They can update their own tasks:

- `todo`
- `in_progress`
- `blocked`
- `completed`

They can also explain the current stage:

> "Implemented repository layer; currently facing PostgreSQL connection issue."

or:

> "Waiting for permission to access Redis namespace."

The Team Lead can:

- Create tasks
- Assign tasks to developers
- View all tasks
- Edit/update tasks
- Change assignments
- Monitor progress

The Streamlit UI will show the user:

```text
LOGIN
  ↓
username + password
  ↓
FastAPI /auth/login
  ↓
password verification
  ↓
JWT generated
  ↓
Streamlit stores JWT
  ↓
JWT sent in Authorization header
  ↓
FastAPI decodes JWT
  ↓
current user identified
  ↓
RBAC checks user's role
  ↓
permission granted / denied
  ↓
database operation
```

This makes the project useful not only as an application, but also as a **teaching tool**.

---

# 2. What You Will Learn

By completing this project, you will understand:

## Backend

- FastAPI
- Pydantic
- SQLModel
- SQLAlchemy concepts
- Relationships
- PostgreSQL/SQLite
- CRUD
- Repository pattern
- Service layer
- API/router layer
- Dependency Injection
- JWT authentication
- Password hashing
- Access tokens
- RBAC
- Authorization
- HTTP status codes
- Production-style project structure

## Frontend / Teaching UI

- Streamlit
- Login UI
- JWT visualization
- HTTP request visualization
- RBAC visualization
- Task dashboard
- Role-based UI
- API response inspection

---

# 3. Authentication vs Authorization

This is one of the most important concepts.

## Authentication

Authentication answers:

> "Who are you?"

Example:

```text
Alice logs in.

Username: alice
Password: ********

FastAPI verifies the credentials.

Result:

Alice is authenticated.
```

## Authorization

Authorization answers:

> "What are you allowed to do?"

Example:

```text
Alice
Role = team_lead

Can create task? YES
Can assign task? YES
Can view all tasks? YES
```

Developer:

```text
Dev1
Role = developer

Can create task? NO
Can update own task? YES
Can update someone else's task? NO
Can view own task? YES
```

Remember:

```text
Authentication = WHO ARE YOU?

Authorization = WHAT CAN YOU DO?
```

---

# 4. Our Application Story

Imagine a real software company.

The development team is working on an **Agentic AI Platform**.

There are three microservices:

```text
api-server
planner
redis
```

The Team Lead divides the work.

```text
                    TEAM LEAD
                        |
          +-------------+-------------+
          |             |             |
         Dev1          Dev2          Dev3
          |             |             |
      api-server      planner       redis
```

The Team Lead creates:

```text
Task 1
Title: Implement authentication API
Assigned to: Dev1
Service: api-server
```

```text
Task 2
Title: Implement planner workflow
Assigned to: Dev2
Service: planner
```

```text
Task 3
Title: Implement Redis state management
Assigned to: Dev3
Service: redis
```

Developers update the progress.

Example:

```text
Status:
IN_PROGRESS

Stage:
Repository layer completed

Notes:
Database connection is failing in Docker.

Blocked:
Yes

Blocked Reason:
Need PostgreSQL credentials.
```

---

# 5. Production-Style Architecture

We will use a **3-layer architecture**.

```text
                    ┌─────────────────────┐
                    │     Streamlit UI    │
                    └──────────┬──────────┘
                               │ HTTP
                               ▼
                    ┌─────────────────────┐
                    │    API / Router     │
                    │      Layer         │
                    └──────────┬──────────┘
                               │
                               ▼
                    ┌─────────────────────┐
                    │    Service Layer    │
                    │  Business Logic     │
                    └──────────┬──────────┘
                               │
                               ▼
                    ┌─────────────────────┐
                    │  Repository Layer   │
                    │   Database Access    │
                    └──────────┬──────────┘
                               │
                               ▼
                    ┌─────────────────────┐
                    │     SQLModel DB     │
                    │ PostgreSQL / SQLite │
                    └─────────────────────┘
```

The responsibility of each layer must remain clear.

---

# 6. Layer Responsibilities

## 6.1 API / Router Layer

Responsible for:

- HTTP endpoints
- Request validation
- Response models
- Authentication dependencies
- Calling services

Example:

```python
@router.post("/tasks")
def create_task(
    task_data: TaskCreate,
    current_user: User = Depends(get_current_user),
):
    return task_service.create_task(task_data, current_user)
```

The router should NOT contain complicated business logic.

---

# 6.2 Service Layer

Responsible for:

- Business rules
- RBAC decisions
- Workflow rules
- Coordinating repositories

Example:

```python
if current_user.role != UserRole.TEAM_LEAD:
    raise HTTPException(
        status_code=403,
        detail="Only team leads can create tasks"
    )
```

---

# 6.3 Repository Layer

Responsible for:

- Database queries
- CRUD operations
- SQLModel session interaction

Example:

```python
def create_task(self, task: Task):
    self.session.add(task)
    self.session.commit()
    self.session.refresh(task)

    return task
```

The repository should not decide whether a user is allowed to create a task.

---

# 7. Why 3 Layers?

Imagine a restaurant.

```text
Customer
   ↓
Waiter
   ↓
Chef
   ↓
Kitchen
```

Customer does not walk directly into the kitchen.

Similarly:

```text
Streamlit
   ↓
Router
   ↓
Service
   ↓
Repository
   ↓
Database
```

Each layer has one job.

This gives us:

- easier testing
- cleaner code
- easier maintenance
- better separation of concerns
- easier scaling
- easier replacement of components

---

# 8. Project Structure

We will intentionally structure this like a production application.

```text
team-task-manager/
│
├── backend/
│   │
│   ├── app/
│   │   ├── __init__.py
│   │   ├── main.py
│   │   │
│   │   ├── core/
│   │   │   ├── __init__.py
│   │   │   ├── config.py
│   │   │   ├── security.py
│   │   │   └── dependencies.py
│   │   │
│   │   ├── db/
│   │   │   ├── __init__.py
│   │   │   ├── session.py
│   │   │   └── init_db.py
│   │   │
│   │   ├── models/
│   │   │   ├── __init__.py
│   │   │   ├── user.py
│   │   │   ├── task.py
│   │   │   └── enums.py
│   │   │
│   │   ├── schemas/
│   │   │   ├── __init__.py
│   │   │   ├── auth.py
│   │   │   └── task.py
│   │   │
│   │   ├── repositories/
│   │   │   ├── __init__.py
│   │   │   ├── user_repository.py
│   │   │   └── task_repository.py
│   │   │
│   │   ├── services/
│   │   │   ├── __init__.py
│   │   │   ├── auth_service.py
│   │   │   └── task_service.py
│   │   │
│   │   └── api/
│   │       ├── __init__.py
│   │       ├── router.py
│   │       │
│   │       └── routes/
│   │           ├── __init__.py
│   │           ├── auth.py
│   │           ├── users.py
│   │           └── tasks.py
│   │
│   ├── requirements.txt
│   └── .env
│
├── frontend/
│   ├── streamlit_app.py
│   ├── api_client.py
│   └── components/
│       ├── jwt_viewer.py
│       ├── rbac_viewer.py
│       └── task_dashboard.py
│
├── tests/
│   ├── test_auth.py
│   ├── test_tasks.py
│   └── test_rbac.py
│
├── .gitignore
├── README.md
└── docker-compose.yml
```

---

# 9. Nomenclature Rules

Use predictable naming.

## Files

```text
user.py
task.py
auth_service.py
task_repository.py
```

## Classes

Use PascalCase:

```python
User
Task
UserRepository
TaskService
```

## Functions

Use snake_case:

```python
get_current_user()
create_task()
get_task_by_id()
```

## Variables

Use snake_case:

```python
current_user
task_data
access_token
```

## Routes

Use plural nouns:

```text
/users
/tasks
```

Authentication:

```text
/auth/login
/auth/me
```

---

# 10. Installing Dependencies

Create a virtual environment:

```bash
python -m venv venv
```

Activate on Windows:

```bash
venv\Scripts\activate
```

Activate on Linux/macOS:

```bash
source venv/bin/activate
```

Install dependencies:

```bash
pip install fastapi uvicorn sqlmodel python-jose[cryptography] passlib[bcrypt] python-dotenv requests streamlit
```

Optional PostgreSQL driver:

```bash
pip install psycopg[binary]
```

---

# 11. Environment Variables

Create:

```text
backend/.env
```

Example:

```env
DATABASE_URL=sqlite:///./team_tasks.db

SECRET_KEY=change-this-to-a-long-random-secret
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
```

For PostgreSQL:

```env
DATABASE_URL=postgresql+psycopg://postgres:postgres@localhost:5432/team_tasks
```

Never commit `.env` to Git.

---

# 12. Database Design

We need two main tables:

```text
users
tasks
```

Relationship:

```text
User 1 ─────────── * Task
```

One user can have many tasks.

A task belongs to one developer.

---

# 13. User Model

Create:

```text
backend/app/models/enums.py
```

```python
from enum import Enum


class UserRole(str, Enum):
    TEAM_LEAD = "team_lead"
    DEVELOPER = "developer"


class TaskStatus(str, Enum):
    TODO = "todo"
    IN_PROGRESS = "in_progress"
    BLOCKED = "blocked"
    COMPLETED = "completed"
```

Now:

```text
backend/app/models/user.py
```

```python
from typing import List, Optional

from sqlmodel import Field, Relationship, SQLModel

from .enums import UserRole


class User(SQLModel, table=True):

    __tablename__ = "users"

    id: Optional[int] = Field(default=None, primary_key=True)

    username: str = Field(index=True, unique=True)
    email: str = Field(unique=True)

    hashed_password: str

    role: UserRole = Field(default=UserRole.DEVELOPER)

    tasks: List["Task"] = Relationship(back_populates="assignee")
```

Notice:

```python
tasks: List["Task"]
```

This represents:

```text
User → many Tasks
```

---

# 14. Task Model

Create:

```text
backend/app/models/task.py
```

```python
from typing import Optional

from sqlmodel import Field, Relationship, SQLModel

from .enums import TaskStatus


class Task(SQLModel, table=True):

    __tablename__ = "tasks"

    id: Optional[int] = Field(default=None, primary_key=True)

    title: str
    description: str

    service_name: str

    status: TaskStatus = Field(default=TaskStatus.TODO)

    current_state: Optional[str] = None

    notes: Optional[str] = None

    blocked: bool = False

    blocked_reason: Optional[str] = None

    assignee_id: int = Field(
        foreign_key="users.id"
    )

    assignee: Optional["User"] = Relationship(
        back_populates="tasks"
    )
```

---

# 15. Understanding the Relationship

The important field is:

```python
assignee_id: int = Field(
    foreign_key="users.id"
)
```

This creates:

```text
tasks.assignee_id
        ↓
users.id
```

For example:

```text
users

id | username
---+---------
1  | alice
2  | dev1
3  | dev2
4  | dev3
```

Tasks:

```text
id | title              | assignee_id
---+--------------------+------------
1  | Auth API            | 2
2  | Planner workflow    | 3
3  | Redis state         | 4
```

Therefore:

```text
Task 1 → Dev1
Task 2 → Dev2
Task 3 → Dev3
```

---

# 16. Why Do We Need Relationships?

Without relationships, we could manually query:

```python
task.assignee_id
```

and then separately:

```python
user = session.get(User, task.assignee_id)
```

Relationships make the domain model easier to work with.

Conceptually:

```python
task.assignee
```

means:

> "Give me the User associated with this Task."

And:

```python
user.tasks
```

means:

> "Give me all tasks assigned to this User."

---

# 17. Database Session

Create:

```text
backend/app/db/session.py
```

```python
from sqlmodel import Session, create_engine

from app.core.config import settings


engine = create_engine(
    settings.database_url,
    echo=True,
)


def get_session():
    with Session(engine) as session:
        yield session
```

`yield` allows FastAPI to provide one session to a request and then clean it up.

---

# 18. Configuration

Create:

```text
backend/app/core/config.py
```

```python
import os

from dotenv import load_dotenv


load_dotenv()


class Settings:

    database_url: str = os.getenv(
        "DATABASE_URL",
        "sqlite:///./team_tasks.db",
    )

    secret_key: str = os.getenv(
        "SECRET_KEY",
        "dev-secret-key",
    )

    algorithm: str = os.getenv(
        "ALGORITHM",
        "HS256",
    )

    access_token_expire_minutes: int = int(
        os.getenv(
            "ACCESS_TOKEN_EXPIRE_MINUTES",
            "30",
        )
    )


settings = Settings()
```

---

# 19. Password Hashing

Never store passwords like:

```text
alice123
```

Never.

Instead:

```text
password
   ↓
hash function
   ↓
hashed password
```

Database contains something like:

```text
$2b$12$...
```

Create:

```text
backend/app/core/security.py
```

```python
from datetime import datetime, timedelta, timezone

from jose import JWTError, jwt
from passlib.context import CryptContext

from app.core.config import settings


pwd_context = CryptContext(
    schemes=["bcrypt"],
    deprecated="auto",
)


def hash_password(password: str) -> str:

    return pwd_context.hash(password)


def verify_password(
    plain_password: str,
    hashed_password: str,
) -> bool:

    return pwd_context.verify(
        plain_password,
        hashed_password,
    )


def create_access_token(
    data: dict,
    expires_minutes: int | None = None,
) -> str:

    payload = data.copy()

    expire = datetime.now(timezone.utc) + timedelta(
        minutes=(
            expires_minutes
            or settings.access_token_expire_minutes
        )
    )

    payload["exp"] = expire

    return jwt.encode(
        payload,
        settings.secret_key,
        algorithm=settings.algorithm,
    )
```

---

# 20. What Is a JWT?

JWT means:

```text
JSON Web Token
```

It is commonly represented as:

```text
xxxxx.yyyyy.zzzzz
```

Three sections:

```text
HEADER.PAYLOAD.SIGNATURE
```

Example conceptual payload:

```json
{
    "sub": "alice",
    "role": "team_lead",
    "exp": 1780000000
}
```

Important:

JWT payload is **encoded, not encrypted**.

Therefore, don't put secrets inside it.

---

# 21. JWT Login Flow

When Alice logs in:

```text
Streamlit
   |
   | username + password
   ↓
POST /auth/login
   |
   ↓
Find Alice in DB
   |
   ↓
Verify password
   |
   ↓
Create JWT
   |
   ↓
Return access_token
   |
   ↓
Streamlit stores token
```

---

# 22. JWT Authentication Flow

After login:

```text
Streamlit
   |
   | Authorization:
   | Bearer eyJ...
   ↓
FastAPI
   |
   ↓
Extract token
   |
   ↓
Decode JWT
   |
   ↓
Read username / subject
   |
   ↓
Find user
   |
   ↓
Current User
```

Then RBAC happens.

```text
Current User
     |
     ↓
What role?
     |
 +---+---+
 |       |
Lead   Developer
```

---

# 23. Authentication Dependency

Create:

```text
backend/app/core/dependencies.py
```

```python
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from sqlmodel import Session, select

from app.core.config import settings
from app.db.session import get_session
from app.models.user import User


oauth2_scheme = OAuth2PasswordBearer(
    tokenUrl="/auth/login"
)


def get_current_user(
    token: str = Depends(oauth2_scheme),
    session: Session = Depends(get_session),
) -> User:

    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Invalid authentication credentials",
        headers={
            "WWW-Authenticate": "Bearer"
        },
    )

    try:

        payload = jwt.decode(
            token,
            settings.secret_key,
            algorithms=[settings.algorithm],
        )

        username = payload.get("sub")

        if not username:
            raise credentials_exception

    except JWTError:
        raise credentials_exception

    statement = select(User).where(
        User.username == username
    )

    user = session.exec(statement).first()

    if not user:
        raise credentials_exception

    return user
```

---

# 24. Understand `Depends()`

This:

```python
current_user: User = Depends(get_current_user)
```

means:

> "Before this endpoint runs, FastAPI should execute `get_current_user()`."

So:

```text
GET /tasks
       |
       ↓
get_current_user()
       |
       ↓
JWT validation
       |
       ↓
User object
       |
       ↓
endpoint
```

This is one of FastAPI's most powerful features.

---

# 25. RBAC

RBAC means:

```text
Role-Based Access Control
```

Our roles:

```python
TEAM_LEAD
DEVELOPER
```

Permissions:

| Action | Team Lead | Developer |
|---|---:|---:|
| Create task | ✅ | ❌ |
| Assign task | ✅ | ❌ |
| View all tasks | ✅ | ❌ |
| View own task | ✅ | ✅ |
| Update own task | ✅ | ✅ |
| Update someone else's task | ✅ | ❌ |
| Mark completed | ✅ | ✅ |
| Mark blocked | ✅ | ✅ |

---

# 26. RBAC Dependency

Create:

```text
backend/app/core/dependencies.py
```

Add:

```python
from typing import Callable

from fastapi import Depends, HTTPException, status

from app.models.enums import UserRole
from app.models.user import User


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

Now we can write:

```python
current_user: User = Depends(
    require_role(UserRole.TEAM_LEAD)
)
```

This means:

```text
JWT valid?
     |
    YES
     ↓
Who is user?
     |
     ↓
What role?
     |
     ↓
team_lead?
   /     \
 YES      NO
 ↓        ↓
ALLOW    403
```

---

# 27. Authentication and RBAC Are Different

This distinction is extremely important.

Suppose Dev1 calls:

```text
POST /tasks
```

with a valid JWT.

Authentication:

```text
JWT valid?
YES
```

But authorization:

```text
Developer allowed to create task?
NO
```

Therefore:

```text
401 = Authentication problem

403 = Authorization problem
```

Think:

```text
401:
"I don't know who you are."

403:
"I know who you are,
but you are not allowed to do this."
```

---

# 28. Request/Response Schemas

We should not expose database models directly everywhere.

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
    token_type: str = "bearer"
```

---

# 29. Task Schemas

Create:

```text
backend/app/schemas/task.py
```

```python
from typing import Optional

from pydantic import BaseModel

from app.models.enums import TaskStatus


class TaskCreate(BaseModel):

    title: str
    description: str
    service_name: str
    assignee_id: int


class TaskUpdate(BaseModel):

    status: Optional[TaskStatus] = None

    current_state: Optional[str] = None

    notes: Optional[str] = None

    blocked: Optional[bool] = None

    blocked_reason: Optional[str] = None
```

---

# 30. Repository Layer

Create:

```text
backend/app/repositories/user_repository.py
```

```python
from sqlmodel import Session, select

from app.models.user import User


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

# 31. Task Repository

Create:

```text
backend/app/repositories/task_repository.py
```

```python
from sqlmodel import Session, select

from app.models.task import Task


class TaskRepository:

    def __init__(
        self,
        session: Session,
    ):

        self.session = session

    def create(
        self,
        task: Task,
    ) -> Task:

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

    def get_by_assignee(
        self,
        user_id: int,
    ) -> list[Task]:

        statement = select(Task).where(
            Task.assignee_id == user_id
        )

        return list(
            self.session.exec(statement)
        )

    def update(
        self,
        task: Task,
    ) -> Task:

        self.session.add(task)
        self.session.commit()
        self.session.refresh(task)

        return task
```

---

# 32. Why Repository?

Instead of putting SQL everywhere:

```python
statement = select(Task).where(...)
```

we centralize database operations.

Then service code can say:

```python
task_repository.get_by_id(task_id)
```

This makes the code easier to understand.

---

# 33. Authentication Service

Create:

```text
backend/app/services/auth_service.py
```

```python
from fastapi import HTTPException, status

from app.core.security import (
    create_access_token,
    verify_password,
)
from app.repositories.user_repository import (
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
    ):

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
            user.hashed_password,
        ):

            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid username or password",
            )

        token = create_access_token(
            {
                "sub": user.username,
                "role": user.role.value,
            }
        )

        return token
```

---

# 34. Task Service

Create:

```text
backend/app/services/task_service.py
```

```python
from fastapi import HTTPException, status

from app.models.enums import UserRole
from app.models.task import Task
from app.models.user import User
from app.repositories.task_repository import (
    TaskRepository,
)
from app.repositories.user_repository import (
    UserRepository,
)
from app.schemas.task import TaskCreate, TaskUpdate


class TaskService:

    def __init__(
        self,
        task_repository: TaskRepository,
        user_repository: UserRepository,
    ):

        self.task_repository = task_repository
        self.user_repository = user_repository

    def create_task(
        self,
        task_data: TaskCreate,
        current_user: User,
    ) -> Task:

        if current_user.role != UserRole.TEAM_LEAD:

            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Only team leads can create tasks",
            )

        developer = self.user_repository.get_by_id(
            task_data.assignee_id
        )

        if not developer:

            raise HTTPException(
                status_code=404,
                detail="Developer not found",
            )

        if developer.role != UserRole.DEVELOPER:

            raise HTTPException(
                status_code=400,
                detail="Tasks can only be assigned to developers",
            )

        task = Task(
            title=task_data.title,
            description=task_data.description,
            service_name=task_data.service_name,
            assignee_id=task_data.assignee_id,
        )

        return self.task_repository.create(task)

    def get_tasks(
        self,
        current_user: User,
    ) -> list[Task]:

        if current_user.role == UserRole.TEAM_LEAD:

            return self.task_repository.get_all()

        return self.task_repository.get_by_assignee(
            current_user.id
        )

    def update_task(
        self,
        task_id: int,
        task_data: TaskUpdate,
        current_user: User,
    ) -> Task:

        task = self.task_repository.get_by_id(
            task_id
        )

        if not task:

            raise HTTPException(
                status_code=404,
                detail="Task not found",
            )

        if (
            current_user.role != UserRole.TEAM_LEAD
            and task.assignee_id != current_user.id
        ):

            raise HTTPException(
                status_code=403,
                detail="You can only update your own tasks",
            )

        update_data = task_data.model_dump(
            exclude_unset=True
        )

        for field, value in update_data.items():

            setattr(task, field, value)

        return self.task_repository.update(task)
```

---

# 35. Important RBAC Rule

Notice this:

```python
if (
    current_user.role != UserRole.TEAM_LEAD
    and task.assignee_id != current_user.id
):
```

This implements:

```text
Team Lead
    ↓
Can update any task

Developer
    ↓
Can update only own task
```

Example:

```text
Dev1 owns Task 1.

Dev1 → update Task 1
       ALLOWED

Dev1 → update Task 2
       FORBIDDEN

Team Lead → update Task 2
            ALLOWED
```

---

# 36. Dependency Factory for Services

Create:

```text
backend/app/core/dependencies.py
```

Add:

```python
from fastapi import Depends
from sqlmodel import Session

from app.db.session import get_session
from app.repositories.task_repository import TaskRepository
from app.repositories.user_repository import UserRepository
from app.services.task_service import TaskService


def get_task_service(
    session: Session = Depends(get_session),
) -> TaskService:

    return TaskService(
        task_repository=TaskRepository(session),
        user_repository=UserRepository(session),
    )
```

This keeps object creation out of the router.

---

# 37. Auth Router

Create:

```text
backend/app/api/routes/auth.py
```

```python
from fastapi import APIRouter, Depends
from sqlmodel import Session

from app.core.dependencies import get_current_user
from app.db.session import get_session
from app.models.user import User
from app.schemas.auth import LoginRequest, TokenResponse
from app.repositories.user_repository import UserRepository
from app.services.auth_service import AuthService


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

    user_repository = UserRepository(session)

    service = AuthService(
        user_repository
    )

    token = service.login(
        data.username,
        data.password,
    )

    return TokenResponse(
        access_token=token
    )


@router.get("/me")
def get_me(
    current_user: User = Depends(
        get_current_user
    ),
):

    return {
        "id": current_user.id,
        "username": current_user.username,
        "role": current_user.role,
    }
```

---

# 38. Task Router

Create:

```text
backend/app/api/routes/tasks.py
```

```python
from fastapi import APIRouter, Depends

from app.core.dependencies import (
    get_current_user,
    get_task_service,
    require_role,
)
from app.models.enums import UserRole
from app.models.user import User
from app.schemas.task import TaskCreate, TaskUpdate
from app.services.task_service import TaskService


router = APIRouter(
    prefix="/tasks",
    tags=["Tasks"],
)


@router.post("/")
def create_task(
    data: TaskCreate,
    current_user: User = Depends(
        require_role(UserRole.TEAM_LEAD)
    ),
    service: TaskService = Depends(
        get_task_service
    ),
):

    return service.create_task(
        data,
        current_user,
    )


@router.get("/")
def get_tasks(
    current_user: User = Depends(
        get_current_user
    ),
    service: TaskService = Depends(
        get_task_service
    ),
):

    return service.get_tasks(
        current_user
    )


@router.patch("/{task_id}")
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
        task_id,
        data,
        current_user,
    )
```

---

# 39. Main Router

Create:

```text
backend/app/api/router.py
```

```python
from fastapi import APIRouter

from app.api.routes import auth, tasks


api_router = APIRouter()

api_router.include_router(
    auth.router
)

api_router.include_router(
    tasks.router
)
```

---

# 40. Application Entry Point

Create:

```text
backend/app/main.py
```

```python
from fastapi import FastAPI

from app.api.router import api_router
from app.db.session import engine
from sqlmodel import SQLModel


app = FastAPI(
    title="Team Task Manager",
    version="1.0.0",
)


@app.on_event("startup")
def startup():

    SQLModel.metadata.create_all(
        engine
    )


app.include_router(
    api_router,
    prefix="/api",
)


@app.get("/health")
def health():

    return {
        "status": "healthy"
    }
```

---

# 41. Run FastAPI

From the `backend` directory:

```bash
uvicorn app.main:app --reload
```

Open:

```text
http://127.0.0.1:8000/docs
```

FastAPI automatically generates Swagger documentation.

---

# 42. Seed Users

We need:

```text
Alice → Team Lead

Dev1 → Developer
Dev2 → Developer
Dev3 → Developer
```

Create:

```text
backend/app/db/init_db.py
```

```python
from sqlmodel import Session

from app.core.security import hash_password
from app.db.session import engine
from app.models.enums import UserRole
from app.models.user import User


def seed_users():

    with Session(engine) as session:

        users = [
            User(
                username="alice",
                email="alice@example.com",
                hashed_password=hash_password(
                    "alice123"
                ),
                role=UserRole.TEAM_LEAD,
            ),

            User(
                username="dev1",
                email="dev1@example.com",
                hashed_password=hash_password(
                    "dev123"
                ),
                role=UserRole.DEVELOPER,
            ),

            User(
                username="dev2",
                email="dev2@example.com",
                hashed_password=hash_password(
                    "dev123"
                ),
                role=UserRole.DEVELOPER,
            ),

            User(
                username="dev3",
                email="dev3@example.com",
                hashed_password=hash_password(
                    "dev123"
                ),
                role=UserRole.DEVELOPER,
            ),
        ]

        session.add_all(users)

        session.commit()


if __name__ == "__main__":

    seed_users()
```

Run:

```bash
python -m app.db.init_db
```

---

# 43. Test Login Manually

Request:

```http
POST /api/auth/login
```

Body:

```json
{
    "username": "alice",
    "password": "alice123"
}
```

Response:

```json
{
    "access_token": "eyJhbGciOiJIUzI1NiIs...",
    "token_type": "bearer"
}
```

That token is the JWT.

---

# 44. What Happens Internally?

Let's slow down.

Alice sends:

```text
alice
alice123
```

FastAPI:

```text
             LOGIN
               |
               ↓
        Find alice in DB
               |
               ↓
        Get password hash
               |
               ↓
       verify_password()
               |
          +----+----+
          |         |
        valid     invalid
          |         |
          ↓         ↓
      create JWT   401
```

JWT contains information like:

```json
{
    "sub": "alice",
    "role": "team_lead",
    "exp": "..."
}
```

---

# 45. Calling a Protected Endpoint

Request:

```http
GET /api/tasks/
Authorization: Bearer eyJ...
```

FastAPI:

```text
Authorization Header
        |
        ↓
Bearer token
        |
        ↓
Decode JWT
        |
        ↓
sub = alice
        |
        ↓
Find alice
        |
        ↓
current_user = Alice
        |
        ↓
RBAC
        |
        ↓
Service
        |
        ↓
Repository
        |
        ↓
Database
```

---

# 46. Team Lead Creates Task

Alice calls:

```http
POST /api/tasks/
```

Body:

```json
{
    "title": "Implement authentication API",
    "description": "Build JWT authentication endpoints",
    "service_name": "api-server",
    "assignee_id": 2
}
```

Flow:

```text
POST /tasks
    |
    ↓
JWT validation
    |
    ↓
Alice identified
    |
    ↓
Role = team_lead
    |
    ↓
RBAC PASS
    |
    ↓
TaskService
    |
    ↓
Validate developer
    |
    ↓
TaskRepository
    |
    ↓
INSERT INTO tasks
```

---

# 47. Developer Attempts to Create Task

Dev1 sends:

```http
POST /api/tasks/
```

with a valid JWT.

Authentication succeeds.

But:

```text
Role = developer

Required:
team_lead
```

Therefore:

```text
403 Forbidden
```

This demonstrates the difference between authentication and authorization.

---

# 48. Developer Updates Task

Dev1 has:

```text
Task 1
assignee_id = dev1
```

Dev1 sends:

```http
PATCH /api/tasks/1
```

Body:

```json
{
    "status": "in_progress",
    "current_state": "Repository layer",
    "notes": "Repository completed. Testing DB connection.",
    "blocked": false
}
```

Flow:

```text
JWT
 ↓
Dev1 identified
 ↓
Task 1 loaded
 ↓
task.assignee_id == current_user.id
 ↓
PASS
 ↓
Update task
```

---

# 49. Developer Tries to Edit Another Developer's Task

Dev1 tries:

```text
PATCH /tasks/2
```

But:

```text
Task 2 → Dev2
```

Check:

```python
task.assignee_id != current_user.id
```

Result:

```text
403 Forbidden
```

This is object-level authorization.

It is extremely important in real applications.

---

# 50. Object-Level Authorization

There are actually two checks:

## Role-level

```text
Can developers create tasks?
NO
```

## Object-level

```text
Can Dev1 edit Dev2's task?
NO
```

So RBAC alone is not enough.

A real system often needs:

```text
Role permissions
+
Resource ownership
```

---

# 51. Task Lifecycle

We will use:

```text
TODO
  |
  ↓
IN_PROGRESS
  |
  +----------+
  |          |
  ↓          ↓
COMPLETED   BLOCKED
               |
               ↓
          IN_PROGRESS
```

Example:

```text
TODO
```

means:

> Task has been assigned but work has not started.

```text
IN_PROGRESS
```

means:

> Developer is actively working.

```text
BLOCKED
```

means:

> Developer cannot continue because of an external problem.

```text
COMPLETED
```

means:

> Work is finished.

---

# 52. Blocked Task Information

When status is:

```text
BLOCKED
```

the UI should show:

```text
Current Stage:
Integration testing

Blocked:
Yes

Blocked Reason:
Waiting for Redis credentials

Notes:
Local implementation is complete.
Cannot test against shared environment.
```

This makes the application more realistic than a simple todo app.

---

# 53. Streamlit UI

Now we create the teaching interface.

Structure:

```text
frontend/
│
├── streamlit_app.py
├── api_client.py
└── components/
    ├── jwt_viewer.py
    ├── rbac_viewer.py
    └── task_dashboard.py
```

---

# 54. API Client

Create:

```text
frontend/api_client.py
```

```python
import requests


BASE_URL = "http://127.0.0.1:8000/api"


def login(
    username: str,
    password: str,
):

    response = requests.post(
        f"{BASE_URL}/auth/login",
        json={
            "username": username,
            "password": password,
        },
    )

    return response


def get_me(token: str):

    response = requests.get(
        f"{BASE_URL}/auth/me",
        headers={
            "Authorization": f"Bearer {token}"
        },
    )

    return response


def get_tasks(token: str):

    response = requests.get(
        f"{BASE_URL}/tasks/",
        headers={
            "Authorization": f"Bearer {token}"
        },
    )

    return response


def create_task(
    token: str,
    task_data: dict,
):

    response = requests.post(
        f"{BASE_URL}/tasks/",
        json=task_data,
        headers={
            "Authorization": f"Bearer {token}"
        },
    )

    return response


def update_task(
    token: str,
    task_id: int,
    task_data: dict,
):

    response = requests.patch(
        f"{BASE_URL}/tasks/{task_id}",
        json=task_data,
        headers={
            "Authorization": f"Bearer {token}"
        },
    )

    return response
```

---

# 55. Streamlit Session State

Streamlit reruns the script frequently.

Therefore, we store login information in:

```python
st.session_state
```

Example:

```python
if "token" not in st.session_state:

    st.session_state.token = None
```

After login:

```python
st.session_state.token = token
```

Now the token survives reruns during the session.

---

# 56. JWT Viewer

Create:

```text
frontend/components/jwt_viewer.py
```

```python
import base64
import json

import streamlit as st


def decode_jwt_without_verification(token: str):

    parts = token.split(".")

    if len(parts) != 3:

        return None

    payload = parts[1]

    padding = "=" * (
        4 - len(payload) % 4
    )

    decoded = base64.urlsafe_b64decode(
        payload + padding
    )

    return json.loads(
        decoded
    )


def show_jwt(token: str):

    st.subheader(
        "🔐 JWT Behind the Scenes"
    )

    st.code(
        token,
        language="text",
    )

    payload = decode_jwt_without_verification(
        token
    )

    if payload:

        st.write("JWT Payload")

        st.json(payload)

        st.info(
            "The payload is decoded here only "
            "for educational visualization. "
            "The backend still verifies the JWT signature."
        )
```

Important:

This decoder does **not verify the signature**.

It is only for visualization.

The backend remains responsible for verification.

---

# 57. RBAC Viewer

Create:

```text
frontend/components/rbac_viewer.py
```

```python
import streamlit as st


def show_rbac(role: str):

    st.subheader(
        "🛡️ RBAC Decision"
    )

    permissions = {
        "team_lead": {
            "Create Task": True,
            "View All Tasks": True,
            "Assign Tasks": True,
            "Update Any Task": True,
        },

        "developer": {
            "Create Task": False,
            "View All Tasks": False,
            "Assign Tasks": False,
            "Update Any Task": False,
        },
    }

    current_permissions = permissions.get(
        role,
        {},
    )

    for permission, allowed in (
        current_permissions.items()
    ):

        if allowed:

            st.success(
                f"✅ {permission}"
            )

        else:

            st.error(
                f"❌ {permission}"
            )
```

---

# 58. Main Streamlit Application

Create:

```text
frontend/streamlit_app.py
```

```python
import streamlit as st

from api_client import (
    create_task,
    get_me,
    get_tasks,
    login,
    update_task,
)

from components.jwt_viewer import show_jwt
from components.rbac_viewer import show_rbac


st.set_page_config(
    page_title="Team Task Manager",
    page_icon="🛡️",
    layout="wide",
)


if "token" not in st.session_state:

    st.session_state.token = None


if "user" not in st.session_state:

    st.session_state.user = None


st.title(
    "🚀 Development Team Task Manager"
)

st.caption(
    "FastAPI + SQLModel + JWT + RBAC + Streamlit"
)


# --------------------------------------------------
# LOGIN
# --------------------------------------------------

if not st.session_state.token:

    st.header("Login")

    username = st.text_input(
        "Username"
    )

    password = st.text_input(
        "Password",
        type="password",
    )

    if st.button("Login"):

        response = login(
            username,
            password,
        )

        if response.status_code == 200:

            data = response.json()

            st.session_state.token = (
                data["access_token"]
            )

            me_response = get_me(
                st.session_state.token
            )

            st.session_state.user = (
                me_response.json()
            )

            st.rerun()

        else:

            st.error(
                response.json().get(
                    "detail",
                    "Login failed",
                )
            )

    st.info(
        "Demo users: "
        "alice/alice123, "
        "dev1/dev123, "
        "dev2/dev123, "
        "dev3/dev123"
    )

    st.stop()


# --------------------------------------------------
# USER INFORMATION
# --------------------------------------------------

user = st.session_state.user
token = st.session_state.token

role = user["role"]


st.sidebar.success(
    f"Logged in as: {user['username']}"
)

st.sidebar.write(
    f"Role: `{role}`"
)


if st.sidebar.button("Logout"):

    st.session_state.token = None
    st.session_state.user = None

    st.rerun()


# --------------------------------------------------
# TABS
# --------------------------------------------------

tab1, tab2, tab3 = st.tabs(
    [
        "📋 Tasks",
        "🔐 JWT",
        "🛡️ RBAC",
    ]
)


# --------------------------------------------------
# TASKS
# --------------------------------------------------

with tab1:

    st.header(
        "Task Dashboard"
    )

    response = get_tasks(token)

    if response.status_code != 200:

        st.error(
            response.text
        )

    else:

        tasks = response.json()

        for task in tasks:

            with st.expander(
                f"{task['title']} "
                f"— {task['status']}"
            ):

                st.write(
                    f"Service: "
                    f"{task['service_name']}"
                )

                st.write(
                    f"Description: "
                    f"{task['description']}"
                )

                st.write(
                    f"Current Stage: "
                    f"{task.get('current_state')}"
                )

                st.write(
                    f"Notes: "
                    f"{task.get('notes')}"
                )

                st.write(
                    f"Blocked: "
                    f"{task.get('blocked')}"
                )

                st.write(
                    f"Blocked Reason: "
                    f"{task.get('blocked_reason')}"
                )

                if role == "developer":

                    new_status = st.selectbox(
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
                        key=f"status_{task['id']}",
                    )

                    stage = st.text_input(
                        "Current Stage",
                        value=(
                            task.get(
                                "current_state"
                            )
                            or ""
                        ),
                        key=f"stage_{task['id']}",
                    )

                    notes = st.text_area(
                        "Notes",
                        value=(
                            task.get(
                                "notes"
                            )
                            or ""
                        ),
                        key=f"notes_{task['id']}",
                    )

                    blocked_reason = st.text_input(
                        "Blocked Reason",
                        value=(
                            task.get(
                                "blocked_reason"
                            )
                            or ""
                        ),
                        key=(
                            f"blocked_reason_"
                            f"{task['id']}"
                        ),
                    )

                    if st.button(
                        "Update",
                        key=f"update_{task['id']}",
                    ):

                        update_data = {
                            "status": new_status,
                            "current_state": stage,
                            "notes": notes,
                            "blocked": (
                                new_status
                                == "blocked"
                            ),
                            "blocked_reason": (
                                blocked_reason
                                if new_status
                                == "blocked"
                                else None
                            ),
                        }

                        update_response = update_task(
                            token,
                            task["id"],
                            update_data,
                        )

                        if (
                            update_response.status_code
                            == 200
                        ):

                            st.success(
                                "Task updated"
                            )

                            st.rerun()

                        else:

                            st.error(
                                update_response.text
                            )


# --------------------------------------------------
# JWT VISUALIZATION
# --------------------------------------------------

with tab2:

    show_jwt(token)

    st.subheader(
        "Request Header"
    )

    st.code(
        "Authorization: Bearer "
        + token,
        language="http",
    )

    st.write(
        "This is how Streamlit sends the "
        "JWT to protected FastAPI endpoints."
    )


# --------------------------------------------------
# RBAC VISUALIZATION
# --------------------------------------------------

with tab3:

    show_rbac(role)

    st.subheader(
        "Authorization Flow"
    )

    st.code(
        """
JWT
 ↓
Identify User
 ↓
Read User Role
 ↓
Check Required Permission
 ↓
Allowed?
 ├── YES → Execute Service
 └── NO  → 403 Forbidden
        """,
        language="text",
    )
```

---

# 59. Run Streamlit

From the `frontend` directory:

```bash
streamlit run streamlit_app.py
```

Open the URL displayed by Streamlit.

Usually:

```text
http://localhost:8501
```

---

# 60. Recommended UI

The Streamlit application should visually communicate:

```text
┌─────────────────────────────────────────────┐
│ Development Team Task Manager               │
├─────────────────────────────────────────────┤
│ Logged in: alice                             │
│ Role: team_lead                              │
├─────────────────────────────────────────────┤
│ Tasks | JWT Behind Scenes | RBAC             │
└─────────────────────────────────────────────┘
```

For developers:

```text
┌─────────────────────────────────────────────┐
│ Dev1                                        │
│ Role: developer                             │
├─────────────────────────────────────────────┤
│ Task: Authentication API                    │
│ Service: api-server                         │
│                                             │
│ Status: IN_PROGRESS                         │
│                                             │
│ Current Stage: Repository Layer             │
│                                             │
│ Notes:                                      │
│ Testing PostgreSQL connection               │
│                                             │
│ [Update]                                    │
└─────────────────────────────────────────────┘
```

---

# 61. Teaching the JWT Flow in Streamlit

The UI should show:

```text
1. Login Credentials
       ↓
2. POST /auth/login
       ↓
3. Password Verification
       ↓
4. JWT Generated
       ↓
5. JWT Stored in Session State
       ↓
6. Authorization Header
       ↓
7. FastAPI JWT Verification
       ↓
8. Current User
```

This is much more educational than simply showing:

```text
Login successful.
```

---

# 62. Add a JWT Timeline

A useful teaching component is:

```python
st.subheader("JWT Request Lifecycle")

steps = [
    "1️⃣ User enters username/password",
    "2️⃣ FastAPI verifies password",
    "3️⃣ FastAPI creates JWT",
    "4️⃣ Streamlit stores JWT",
    "5️⃣ Streamlit sends Bearer token",
    "6️⃣ FastAPI decodes and verifies JWT",
    "7️⃣ FastAPI identifies current user",
    "8️⃣ RBAC checks role",
    "9️⃣ Endpoint executes",
]
```

Display these vertically.

This helps students understand that JWT is not "magic authentication".

---

# 63. Add an RBAC Decision Simulator

Create a Streamlit section:

```text
Current User:
Dev1

Role:
developer

Action:
Create Task

Required Role:
team_lead

Result:
❌ DENIED
```

For Alice:

```text
Current User:
Alice

Role:
team_lead

Action:
Create Task

Required Role:
team_lead

Result:
✅ ALLOWED
```

This is excellent for teaching.

---

# 64. Add Object-Level Authorization Visualization

For Dev1:

```text
User:
Dev1

Trying to update:
Task #2

Task Owner:
Dev2

Check:

Dev1 == Dev2 ?

NO

Result:
❌ 403 Forbidden
```

For Dev1 updating Task #1:

```text
User:
Dev1

Task Owner:
Dev1

Check:

Dev1 == Dev1 ?

YES

Result:
✅ Allowed
```

This makes authorization extremely easy to understand.

---

# 65. The Complete Request Lifecycle

Let's combine everything.

Suppose Dev1 updates his task.

```text
                     STREAMLIT
                         |
                         |
                 PATCH /tasks/1
                         |
                  Authorization:
                  Bearer eyJ...
                         |
                         ▼
                    FASTAPI
                         |
                         ▼
                OAuth2PasswordBearer
                         |
                         ▼
                  JWT validation
                         |
                         ▼
                  get_current_user()
                         |
                         ▼
                       User
                         |
                         ▼
                    Task Router
                         |
                         ▼
                   Task Service
                         |
                         ▼
             Is Dev1 owner of Task 1?
                         |
                    +----+----+
                    |         |
                   YES       NO
                    |         |
                    ▼         ▼
               Repository    403
                    |
                    ▼
                  SQLModel
                    |
                    ▼
                 Database
                    |
                    ▼
                 Response
                    |
                    ▼
                 Streamlit
```

---

# 66. Why SQLModel?

SQLModel combines ideas from:

```text
Pydantic
+
SQLAlchemy
```

This gives us Python models that can also represent database tables.

Example:

```python
class User(SQLModel, table=True):

    id: Optional[int] = Field(
        default=None,
        primary_key=True,
    )

    username: str
```

This is both:

```text
Python model
+
Database table model
```

---

# 67. SQLModel Relationships Mental Model

Think:

```text
User
 |
 +---- Task
 |
 +---- Task
 |
 +---- Task
```

Python:

```python
user.tasks
```

Database:

```text
users.id
      ↑
      |
tasks.assignee_id
```

This is a foreign-key relationship.

---

# 68. Relationship Types

The tutorial uses:

```text
One-to-Many
```

One User:

```text
User 1
```

can have many Tasks:

```text
Task 1
Task 2
Task 3
```

Other relationship types include:

```text
One-to-One
One-to-Many
Many-to-Many
```

---

# 69. Many-to-Many Example

Suppose developers can work on multiple services.

You might eventually have:

```text
Developer
    |
    +---- Service
    |
    +---- Service
```

and:

```text
Service
    |
    +---- Developer
    |
    +---- Developer
```

That would normally require a junction/link table.

Example:

```text
developer_service
------------------
developer_id
service_id
```

We don't need it for this tutorial, but this is the natural next step.

---

# 70. Why Not Put Everything in `main.py`?

A beginner project might look like:

```text
main.py
```

with:

```python
@app.post(...)
def create_task():
    ...
```

plus:

```python
database query
JWT logic
password hashing
RBAC
business rules
```

all inside one function.

It works.

But it becomes difficult to maintain.

Production code should separate:

```text
Routes
Services
Repositories
Models
Schemas
Security
Database
Configuration
```

---

# 71. Router vs Service vs Repository

Remember this interview table.

| Layer | Main Responsibility |
|---|---|
| Router | HTTP/API |
| Service | Business logic |
| Repository | Database access |

Example:

```text
Router:
"POST /tasks"

Service:
"Only team leads can create tasks"

Repository:
"INSERT task into database"
```

---

# 72. A Good Interview Explanation

If asked:

> "Explain your FastAPI architecture."

Say:

```text
I use a layered architecture where the router layer
handles HTTP concerns and request validation, the service
layer contains business rules and authorization decisions,
and the repository layer handles database access through
SQLModel.

Authentication is implemented using JWT and FastAPI
dependencies. The current user is resolved from the token,
and RBAC is applied before protected operations are executed.

This separation keeps the API layer thin and makes the
business logic and database operations independently
testable.
```

---

# 73. JWT Interview Explanation

If asked:

> "How does JWT authentication work?"

Answer:

```text
The user submits credentials to the login endpoint.
The backend verifies the password against the stored
password hash. If valid, it creates a signed JWT containing
claims such as the subject and expiration time.

The client sends that JWT in the Authorization Bearer header
for protected requests. FastAPI uses a dependency to extract
and validate the token, identify the user, and provide the
current user to the endpoint.
```

---

# 74. RBAC Interview Explanation

If asked:

> "How did you implement RBAC?"

Answer:

```text
Each user has a role such as team_lead or developer.
Protected endpoints use FastAPI dependencies to verify
whether the authenticated user's role satisfies the required
permission.

For example, only a team lead can create or assign tasks.
Developers can update their own tasks, but object-level
authorization prevents them from updating another
developer's task.
```

---

# 75. 401 vs 403

Memorize this:

```text
401 Unauthorized
=
Authentication failed.

403 Forbidden
=
Authentication succeeded,
but permission failed.
```

Examples:

```text
No JWT
→ 401

Invalid JWT
→ 401

Valid JWT + developer calling team-lead endpoint
→ 403
```

---

# 76. Security Improvements for a Real Production System

This tutorial intentionally keeps authentication understandable.

A production application should additionally consider:

- HTTPS
- secure secret management
- short-lived access tokens
- refresh tokens
- token revocation strategy
- password policy
- account lockout
- rate limiting
- audit logging
- CSRF considerations depending on client/auth mechanism
- database migrations
- secure cookie strategies where applicable
- centralized identity provider if appropriate
- least-privilege permissions

Never use:

```env
SECRET_KEY=dev-secret-key
```

in production.

---

# 77. Database Migration

For a serious application, don't rely permanently on:

```python
SQLModel.metadata.create_all(engine)
```

Use migrations.

A common production choice is:

```text
Alembic
```

Migration workflow:

```text
Change SQLModel
      ↓
Create migration
      ↓
Review migration
      ↓
Run migration
      ↓
Database updated
```

---

# 78. Docker Architecture

Eventually the project can become:

```text
                  ┌───────────────┐
                  │   Streamlit   │
                  └───────┬───────┘
                          │
                          ▼
                  ┌───────────────┐
                  │    FastAPI    │
                  └───────┬───────┘
                          │
             ┌────────────┴────────────┐
             │                         │
             ▼                         ▼
       ┌─────────────┐          ┌─────────────┐
       │ PostgreSQL  │          │    Redis    │
       └─────────────┘          └─────────────┘
```

This starts looking like a real microservice-supporting environment.

---

# 79. Docker Compose Example

At project root:

```yaml
services:

  api:
    build:
      context: ./backend

    ports:
      - "8000:8000"

    environment:
      DATABASE_URL: postgresql+psycopg://postgres:postgres@db:5432/team_tasks
      SECRET_KEY: change-me
      ALGORITHM: HS256

    depends_on:
      - db


  frontend:
    build:
      context: ./frontend

    ports:
      - "8501:8501"

    depends_on:
      - api


  db:
    image: postgres:16

    environment:
      POSTGRES_USER: postgres
      POSTGRES_PASSWORD: postgres
      POSTGRES_DB: team_tasks

    ports:
      - "5432:5432"

    volumes:
      - postgres_data:/var/lib/postgresql/data


volumes:

  postgres_data:
```

---

# 80. Testing Strategy

Production architecture becomes especially useful when testing.

Test:

```text
Authentication
RBAC
Task creation
Task update
Ownership
```

Example:

```text
test_login_success
test_login_wrong_password
test_developer_cannot_create_task
test_team_lead_can_create_task
test_developer_can_update_own_task
test_developer_cannot_update_other_task
```

---

# 81. RBAC Test Matrix

Use this as your test checklist.

| User | Action | Expected |
|---|---|---|
| Alice | Create task | 200 |
| Dev1 | Create task | 403 |
| Alice | View all tasks | 200 |
| Dev1 | View tasks | Own tasks |
| Dev1 | Update own task | 200 |
| Dev1 | Update Dev2 task | 403 |
| Alice | Update Dev2 task | 200 |

---

# 82. End-to-End Demo

Run:

```text
Terminal 1:
FastAPI

Terminal 2:
Streamlit
```

Then:

## Step 1

Login as:

```text
alice
alice123
```

Show:

```text
Role:
team_lead
```

Open:

```text
JWT
```

Explain:

```text
sub = alice
role = team_lead
exp = ...
```

---

## Step 2

Create:

```text
Task:
Implement API authentication

Developer:
Dev1

Service:
api-server
```

---

## Step 3

Logout.

Login:

```text
dev1
dev123
```

Now the RBAC tab should show:

```text
Create Task ❌
View All Tasks ❌
Assign Tasks ❌
Update Any Task ❌
```

---

## Step 4

Dev1 opens the assigned task.

Update:

```text
Status:
IN_PROGRESS

Current Stage:
Repository Layer

Notes:
Repository implementation completed.
```

---

## Step 5

Change:

```text
Status:
BLOCKED
```

and:

```text
Blocked Reason:
Waiting for PostgreSQL permission.
```

The UI should make this visible.

---

## Step 6

Try to update Dev2's task.

Expected:

```text
403 Forbidden
```

This demonstrates object-level authorization.

---

# 83. Final Architecture

At the end, you should understand this entire chain:

```text
                         USER
                          |
                          ▼
                    STREAMLIT UI
                          |
                          ▼
                 Login Credentials
                          |
                          ▼
                  POST /auth/login
                          |
                          ▼
                 Password Verification
                          |
                          ▼
                      JWT Token
                          |
                          ▼
                Streamlit Session State
                          |
                          ▼
             Authorization: Bearer <JWT>
                          |
                          ▼
                       FASTAPI
                          |
                          ▼
                 JWT Authentication
                          |
                          ▼
                    Current User
                          |
                          ▼
                         RBAC
                          |
                 +--------+--------+
                 |                 |
              Allowed            Denied
                 |                 |
                 ▼                 ▼
             Service              403
                 |
                 ▼
             Repository
                 |
                 ▼
              SQLModel
                 |
                 ▼
              Database
```

---

# 84. The Most Important Mental Model

If you remember only one diagram from this tutorial, remember:

```text
                 AUTHENTICATION
                       |
                       ▼
                "WHO ARE YOU?"
                       |
                       ▼
                    JWT
                       |
                       ▼
                CURRENT USER
                       |
                       ▼
                 AUTHORIZATION
                       |
                       ▼
               "WHAT CAN YOU DO?"
                       |
                       ▼
                     RBAC
                       |
                       ▼
               BUSINESS LOGIC
                       |
                       ▼
                    DATABASE
```

And the application architecture:

```text
        STREAMLIT
            |
            ▼
          ROUTER
            |
            ▼
         SERVICE
            |
            ▼
       REPOSITORY
            |
            ▼
         DATABASE
```

---

# 85. What Students Should Be Able to Explain After This

After completing this project, you should be able to answer:

### FastAPI

- What is FastAPI?
- What is dependency injection?
- What does `Depends()` do?
- How do routers work?
- Why use response models?

### SQLModel

- What is SQLModel?
- What is a primary key?
- What is a foreign key?
- What is a relationship?
- What is one-to-many?
- Why use repositories?

### JWT

- What is JWT?
- What are JWT header, payload and signature?
- How is a JWT generated?
- How is a JWT verified?
- What is Bearer authentication?
- Why shouldn't JWT payload contain secrets?

### Authentication

- How does login work?
- Why hash passwords?
- How does FastAPI identify the current user?

### Authorization

- What is RBAC?
- Authentication vs authorization?
- 401 vs 403?
- What is object-level authorization?

### Architecture

- What is a 3-layer architecture?
- What belongs in a router?
- What belongs in a service?
- What belongs in a repository?
- Why separate these layers?

### Streamlit

- How does Streamlit communicate with FastAPI?
- Where is the JWT stored?
- How is the JWT sent?
- How can we visualize authentication?
- How can we visualize RBAC?

---

# 86. Final Project Challenge

Once the base application works, extend it.

## Challenge 1 — Admin Role

Add:

```text
ADMIN
```

Admin can:

```text
Create users
Delete users
Change roles
View all tasks
```

---

## Challenge 2 — Task Priority

Add:

```text
LOW
MEDIUM
HIGH
CRITICAL
```

---

## Challenge 3 — Task Comments

Create:

```text
Task 1
   |
   +---- Comment 1
   +---- Comment 2
   +---- Comment 3
```

This introduces another relationship.

---

## Challenge 4 — Audit Log

Create:

```text
audit_logs
```

Record:

```text
who
what
when
task_id
old_value
new_value
```

Example:

```text
Dev1
changed
Task #1
status
todo → in_progress
```

---

## Challenge 5 — Permission Model

Instead of hardcoding:

```python
UserRole.TEAM_LEAD
```

create:

```text
roles
permissions
role_permissions
```

Then:

```text
Team Lead
    |
    +---- create_task
    +---- assign_task
    +---- update_any_task

Developer
    |
    +---- update_own_task
```

This moves from simple RBAC toward a more configurable authorization system.

---

# 87. Suggested Learning Order

Do not try to memorize the entire application at once.

Learn in this order:

```text
1. FastAPI basics
       ↓
2. SQLModel models
       ↓
3. Foreign keys
       ↓
4. Relationships
       ↓
5. CRUD
       ↓
6. Repository layer
       ↓
7. Service layer
       ↓
8. Password hashing
       ↓
9. JWT generation
       ↓
10. JWT verification
       ↓
11. Current user dependency
       ↓
12. RBAC
       ↓
13. Object-level authorization
       ↓
14. Streamlit API client
       ↓
15. JWT visualization
       ↓
16. RBAC visualization
       ↓
17. Testing
       ↓
18. Docker
       ↓
19. PostgreSQL
       ↓
20. Alembic
```

---

# 88. One-Sentence Summary

We built a production-style **Development Team Task Manager** where a Team Lead creates and assigns microservice tasks, developers update their own progress and blockers, FastAPI handles the API, SQLModel manages relational data, JWT authenticates users, RBAC authorizes actions, a 3-layer architecture separates responsibilities, and Streamlit visually teaches what happens behind every authentication and authorization request.

---

# 89. Production Mindset Checklist

Before calling the project "production-ready", ask:

```text
[ ] Is authentication separated from authorization?
[ ] Are passwords hashed?
[ ] Is the JWT signed?
[ ] Is JWT expiration configured?
[ ] Is SECRET_KEY stored securely?
[ ] Are protected endpoints using dependencies?
[ ] Are RBAC checks centralized?
[ ] Are object-level permissions enforced?
[ ] Are routers thin?
[ ] Is business logic inside services?
[ ] Is database access inside repositories?
[ ] Are SQLModel relationships understood?
[ ] Are database migrations used?
[ ] Are tests written?
[ ] Are secrets excluded from Git?
[ ] Is HTTPS used in production?
[ ] Is audit logging implemented where needed?
[ ] Are errors handled consistently?
[ ] Is the application containerized?
[ ] Are health checks available?
[ ] Is PostgreSQL used instead of SQLite for production?
```

---

# 90. Final Takeaway

This is not just a Todo application.

The Todo application is the **story** used to teach a collection of real backend engineering concepts.

The real learning is:

```text
                    FASTAPI
                       |
             +---------+---------+
             |                   |
        Authentication        API Design
             |                   |
            JWT                Routers
             |                   |
             +---------+---------+
                       |
                    RBAC
                       |
                Authorization
                       |
                  Services
                       |
                Repositories
                       |
                  SQLModel
                       |
                 Relationships
                       |
                   Database
                       |
                  Streamlit
                       |
               Visual Learning
```

If you can build this application from scratch and explain every arrow in that diagram, you have moved beyond simply knowing FastAPI syntax—you understand how the major pieces of a real backend application fit together.
