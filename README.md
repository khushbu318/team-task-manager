# Team Task Manager

A small learning project for understanding how a FastAPI backend, JWT login, role-based access control (RBAC), a three-layer architecture, and a Streamlit UI fit together.

The application models a development team. A team lead creates and assigns tasks, while developers view and update the tasks assigned to them. The Streamlit interface makes the authentication and authorization flow visible instead of hiding it behind a conventional frontend.

## What You Will Learn

- Building REST APIs with FastAPI
- Request and response validation with Pydantic
- SQLModel models, sessions, relationships, and SQLite persistence
- Secure password hashing with `pwdlib`
- JWT access-token authentication
- The difference between authentication and authorization
- RBAC and object-level ownership checks
- FastAPI dependency injection
- A router, service, and repository architecture
- Calling an API from Streamlit with `requests`
- Inspecting JWT claims and the request pipeline in a UI

## Application Flow

```text
Streamlit UI
    |
    | login credentials / Bearer token
    v
FastAPI routers
    |
    v
Services          business rules, RBAC, ownership checks
    |
    v
Repositories      database operations
    |
    v
SQLModel + SQLite
```

During login:

```text
username + password
        -> POST /auth/login
        -> password verification
        -> JWT access token
        -> Streamlit stores the token
        -> token is sent as Authorization: Bearer <token>
```

Authentication answers **who are you?** Authorization answers **what are you allowed to do?**

## Roles and Permissions

| Role | Permissions |
| --- | --- |
| `team_lead` | View all tasks, create tasks, assign tasks, update any task |
| `developer` | View assigned tasks and update only owned tasks |

Developers cannot create tasks or update another developer's task. These rules are enforced in the backend service layer, not only by hiding buttons in Streamlit.

## Project Structure

```text
team-task-manager/
├── backend/
│   └── app/
│       ├── api/             # Dependencies and HTTP routers
│       ├── core/            # Configuration and password/JWT security
│       ├── db/              # SQLModel engine and sessions
│       ├── models/          # Database models
│       ├── repositories/    # Database access
│       ├── schemas/         # Request and response schemas
│       ├── services/        # Business rules and authorization
│       └── main.py          # FastAPI application
├── frontend/
│   ├── api_client.py        # HTTP client for the backend
│   └── streamlit_app.py     # Login and teaching dashboard
├── scripts/
│   └── seed.py              # Sample users
├── requirements.txt
├── fastapi_sqlmodel_jwt_rbac_streamlit_tutorial.md
└── fastapi_sqlmodel_jwt_rbac_streamlit_build_along_tutorial.md
```

## Prerequisites

- Python 3.11 or newer
- A terminal and an editor such as VS Code

## Setup

From the project root:

```bash
python -m venv venv
```

Activate the virtual environment.

### Windows PowerShell

```powershell
venv\Scripts\Activate.ps1
```

### macOS/Linux

```bash
source venv/bin/activate
```

Install dependencies:

```bash
python -m pip install -r requirements.txt
```

Optional: create a `.env` file for local configuration:

```env
DATABASE_URL=sqlite:///./team_tasks.db
JWT_SECRET_KEY=replace-this-with-a-long-random-secret
ACCESS_TOKEN_EXPIRE_MINUTES=60
```

The default database is `team_tasks.db` in the project root. The application creates the database tables when FastAPI starts or when the seed script runs.

## Run the Project

Open two terminals in the project root and activate the virtual environment in each one.

### 1. Seed sample users

```bash
python scripts/seed.py
```

The seed script is safe to run again because it skips users that already exist.

### 2. Start the FastAPI backend

```bash
uvicorn backend.app.main:app --reload
```

The API is available at <http://127.0.0.1:8000>.

- Swagger UI: <http://127.0.0.1:8000/docs>
- OpenAPI schema: <http://127.0.0.1:8000/openapi.json>

### 3. Start the Streamlit UI

In the second terminal:

```bash
streamlit run frontend/streamlit_app.py
```

Streamlit will print the local URL, normally <http://localhost:8501>.

## Sample Login Accounts

| Username | Password | Role |
| --- | --- | --- |
| `alice` | `lead123` | `team_lead` |
| `dev1` | `dev123` | `developer` |
| `dev2` | `dev123` | `developer` |
| `dev3` | `dev123` | `developer` |

These credentials are for local learning only. Change them and use a strong secret before deploying anything.

## API Endpoints

| Method | Path | Purpose |
| --- | --- | --- |
| `GET` | `/` | Check that the API is running |
| `POST` | `/auth/login` | Verify credentials and return a JWT |
| `GET` | `/tasks` | Return all tasks for a team lead or assigned tasks for a developer |
| `POST` | `/tasks` | Create a task; team leads only |
| `PATCH` | `/tasks/{task_id}` | Update a task; team leads or the assigned developer |

`/auth/login` uses form data because it is implemented with FastAPI's `OAuth2PasswordRequestForm`:

```bash
curl -X POST http://127.0.0.1:8000/auth/login \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=alice&password=lead123"
```

Use the returned token in subsequent requests:

```bash
curl http://127.0.0.1:8000/tasks \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"
```

## How the Three Layers Work

1. **Router/API layer** receives HTTP requests, validates input, injects dependencies, and returns responses.
2. **Service layer** implements business rules such as role checks, task visibility, and ownership checks.
3. **Repository layer** performs database operations through SQLModel.

For example, a task request follows this path:

```text
tasks.py router
    -> get_current_user() validates the JWT
    -> TaskService applies RBAC and ownership rules
    -> TaskRepository reads or writes SQLModel data
    -> SQLite
```

Keeping these responsibilities separate makes each layer easier to read, test, and replace.

## Learning Path

1. Run the API and open Swagger UI.
2. Run the seed script and log in as `alice`.
3. Create a task assigned to `dev1`.
4. Log in as `dev1` and update the task status or current state.
5. Try to create a task as `dev1` and observe the `403 Forbidden` response.
6. Try to update a task assigned to another developer and observe the ownership check.
7. Inspect the JWT payload and request pipeline in the Streamlit dashboard.
8. Read the build-along tutorial and recreate the project file by file.

## Tutorials

- [Conceptual tutorial](fastapi_sqlmodel_jwt_rbac_streamlit_tutorial.md): explains the application story, authentication, authorization, RBAC, architecture, and learning concepts.
- [Build-along tutorial](fastapi_sqlmodel_jwt_rbac_streamlit_build_along_tutorial.md): walks from an empty folder through setup, implementation, verification, and running the application.

## Security and Production Notes

This project is designed for learning. Before production use, you should at least:

- provide `JWT_SECRET_KEY` through a secret manager or deployment environment
- use strong, unique passwords and never commit real credentials
- use HTTPS
- replace or migrate the SQLite database for the expected workload
- add database migrations, automated tests, token revocation/refresh strategy, and tighter error/logging policies
- avoid displaying decoded token contents in a production UI

## License

This repository does not currently specify a license. Add one before distributing the project for reuse.