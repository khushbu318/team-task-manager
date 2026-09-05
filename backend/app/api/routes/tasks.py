# ============================================================
# task.py
# ============================================================
#
# This file contains the API endpoints related to Tasks.
#
# It represents the ROUTER / CONTROLLER layer of our
# 3-layer architecture.
#
#
# 3-LAYER ARCHITECTURE
#
#        HTTP Request
#             │
#             ▼
#        Task Router
#       (this file)
#             │
#             ▼
#        Task Service
#      (business logic)
#             │
#             ▼
#       Task Repository
#       (DB operations)
#             │
#             ▼
#          Database
#
#
# Authentication is handled separately:
#
# HTTP Request
#      │
#      ▼
# get_current_user()
#      │
#      ▼
# Validate JWT
#      │
#      ▼
# Find User
#      │
#      ▼
# current_user
#
# ============================================================


from fastapi import APIRouter, Depends
from sqlmodel import Session


# ------------------------------------------------------------
# Authentication Dependency
# ------------------------------------------------------------
#
# get_current_user() is responsible for:
#
# 1. Extracting JWT from Authorization header
# 2. Validating/decoding the JWT
# 3. Getting user_id from JWT
# 4. Finding the user in the database
#
# If authentication fails:
#
#     401 Unauthorized
#
# If successful:
#
#     current_user = User object
#
from backend.app.api.deps import get_current_user


# Database dependency.
#
# FastAPI will use get_session() to provide a database
# session whenever we need one.
from backend.app.db.session import get_session


# User database model.
#
# current_user will be an instance of this model.
from backend.app.models.user import User


# Repository layer.
#
# TaskRepository is responsible for database operations
# related to tasks.
#
# Example:
#
# - get tasks
# - find task by ID
# - update task
# - create task
#
from backend.app.repositories.task_repository import (
    TaskRepository,
)


# Request/Response schemas.
#
# TaskCreate   → data required to create a task
# TaskUpdate   → data allowed when updating a task
# TaskResponse → structure returned to the client
#
from backend.app.schemas.task import (
    TaskCreate,
    TaskUpdate,
    TaskResponse
)


# Service layer.
#
# TaskService contains task-related business logic.
#
# The router should NOT contain business rules.
from backend.app.services.task_service import (
    TaskService,
)


# ============================================================
# Create Task Router
# ============================================================

router = APIRouter(
    # All endpoints in this router start with /tasks.
    #
    # Example:
    #
    # @router.get("")
    #
    # becomes:
    #
    # GET /tasks
    #
    prefix="/tasks",

    # Swagger/OpenAPI will group these APIs
    # under the "Tasks" section.
    tags=["Tasks"],
)


# ============================================================
# Task Service Dependency
# ============================================================
#
# This function is a dependency factory.
#
# Its job is to create a TaskService with all the
# dependencies it needs.
#
#
# Instead of doing this inside every endpoint:
#
#     session = ...
#     repository = TaskRepository(session)
#     service = TaskService(repository)
#
# we define it once here.
#
# Then endpoints can simply write:
#
#     service: TaskService = Depends(get_task_service)
#
# ============================================================

def get_task_service(
    # FastAPI automatically provides a database session.
    session: Session = Depends(get_session),
) -> TaskService:

    # --------------------------------------------------------
    # Create Repository
    # --------------------------------------------------------
    #
    # Repository receives the database session.
    #
    # TaskRepository is responsible for database access.
    #
    repository = TaskRepository(session)

    # --------------------------------------------------------
    # Create Service
    # --------------------------------------------------------
    #
    # Service receives the repository.
    #
    # Therefore:
    #
    # TaskService
    #      ↓
    # TaskRepository
    #      ↓
    # Database
    #
    return TaskService(repository)


# ============================================================
# GET /tasks
# ============================================================
#
# Get all tasks belonging to the currently logged-in user.
#
# Example:
#
# GET /tasks
#
# Authorization: Bearer <JWT>
#
# ============================================================

@router.get(
    "",

    # Tell FastAPI that the response should be a list
    # containing TaskResponse objects.
    #
    # Example:
    #
    # [
    #     {
    #         "id": 1,
    #         "title": "Learn FastAPI"
    #     },
    #     {
    #         "id": 2,
    #         "title": "Learn JWT"
    #     }
    # ]
    #
    response_model=list[TaskResponse]
)
def get_tasks(

    # --------------------------------------------------------
    # Authentication Dependency
    # --------------------------------------------------------
    #
    # Before this endpoint executes, FastAPI runs:
    #
    #     get_current_user()
    #
    # That function:
    #
    # JWT
    #  ↓
    # Validate JWT
    #  ↓
    # Get user_id
    #  ↓
    # Database
    #  ↓
    # User object
    #
    # The returned User object is injected here.
    #
    current_user: User = Depends(
        get_current_user
    ),

    # --------------------------------------------------------
    # Task Service Dependency
    # --------------------------------------------------------
    #
    # FastAPI runs:
    #
    #     get_task_service()
    #
    # which internally does:
    #
    #     get_session()
    #          ↓
    #     TaskRepository(session)
    #          ↓
    #     TaskService(repository)
    #
    service: TaskService = Depends(
        get_task_service
    ),
):

    # --------------------------------------------------------
    # Call Service Layer
    # --------------------------------------------------------
    #
    # Router does NOT query the database.
    #
    # Router simply passes the authenticated user
    # to the service.
    #
    return service.get_tasks_for_user(
        current_user
    )


# ============================================================
# POST /tasks
# ============================================================
#
# Create a new task for the currently logged-in user.
#
# Request flow:
#
# Client
#   │
#   ▼
# POST /tasks
#   │
#   ├── TaskCreate         → Request body validation
#   │
#   ├── get_current_user() → JWT authentication
#   │
#   └── get_task_service() → Service + Repository + DB
#   │
#   ▼
# TaskService.create_task()
#   │
#   ▼
# TaskRepository
#   │
#   ▼
# Database
#
# ============================================================

@router.post(
    "",

    # Define the structure of the response.
    #
    # FastAPI will convert the returned task object
    # into the TaskResponse schema.
    #
    # Example response:
    #
    # {
    #     "id": 1,
    #     "title": "Learn FastAPI",
    #     "description": "Study dependencies"
    # }
    #
    response_model=TaskResponse
)
def create_task(

    # --------------------------------------------------------
    # Request Body
    # --------------------------------------------------------
    #
    # FastAPI automatically validates the incoming JSON
    # against the TaskCreate schema.
    #
    # Example request:
    #
    # {
    #     "title": "Learn FastAPI",
    #     "description": "Learn Dependency Injection"
    # }
    #
    # JSON → TaskCreate object
    #
    data: TaskCreate,


    # --------------------------------------------------------
    # JWT Authentication
    # --------------------------------------------------------
    #
    # Before this endpoint runs, FastAPI executes:
    #
    #     get_current_user()
    #
    # It:
    #
    # 1. Extracts JWT from Authorization header
    # 2. Validates the JWT
    # 3. Gets user_id from the token
    # 4. Finds the user in the database
    #
    # If authentication fails:
    #
    #     401 Unauthorized
    #
    # If successful:
    #
    #     current_user = logged-in User object
    #
    current_user: User = Depends(
        get_current_user
    ),


    # --------------------------------------------------------
    # Task Service Dependency
    # --------------------------------------------------------
    #
    # FastAPI executes get_task_service().
    #
    # Internally:
    #
    #     get_session()
    #          ↓
    #     TaskRepository(session)
    #          ↓
    #     TaskService(repository)
    #
    # The resulting TaskService object is injected here.
    #
    service: TaskService = Depends(
        get_task_service
    ),
):

    # --------------------------------------------------------
    # Call Service Layer
    # --------------------------------------------------------
    #
    # The router does NOT contain the task creation logic.
    #
    # It simply passes:
    #
    #     current_user → Who is creating the task?
    #     data         → What task should be created?
    #
    # The service is responsible for the business logic
    # and will use the repository to interact with the DB.
    #
    return service.create_task(
        current_user=current_user,
        data=data
    )

# ============================================================
# PATCH /tasks/{task_id}
# ============================================================
#
# Update a task belonging to the current user.
#
# Example:
#
# PATCH /tasks/10
#
# Authorization: Bearer <JWT>
#
# {
#     "title": "Learn Advanced FastAPI"
# }
#
# ============================================================

@router.patch(
    "/{task_id}",

    # Response must follow TaskResponse schema.
    response_model=TaskResponse
)
def updated_task(

    # --------------------------------------------------------
    # Path Parameter
    # --------------------------------------------------------
    #
    # Example:
    #
    # PATCH /tasks/10
    #
    # task_id = 10
    #
    task_id: int,

    # --------------------------------------------------------
    # Request Body
    # --------------------------------------------------------
    #
    # FastAPI converts incoming JSON into TaskUpdate.
    #
    # Example JSON:
    #
    # {
    #     "title": "Learn JWT"
    # }
    #
    data: TaskUpdate,

    # --------------------------------------------------------
    # Authentication
    # --------------------------------------------------------
    #
    # Ensures that only an authenticated user can update
    # a task.
    #
    # If JWT is invalid:
    #
    #     401 Unauthorized
    #
    current_user: User = Depends(
        get_current_user
    ),

    # --------------------------------------------------------
    # Service Dependency
    # --------------------------------------------------------
    #
    # FastAPI creates:
    #
    #     TaskService
    #          ↓
    #     TaskRepository
    #          ↓
    #     Database Session
    #
    service: TaskService = Depends(
        get_task_service
    ),
):

    # --------------------------------------------------------
    # Call Service Layer
    # --------------------------------------------------------
    #
    # The router passes the required information to the
    # service.
    #
    # The actual business logic belongs inside:
    #
    #     TaskService.update_task()
    #
    # For example, the service may check:
    #
    # "Does this task actually belong to this user?"
    #
    # and then ask the repository to update it.
    #
    return service.update_task(
        current_user=current_user,
        task_id=task_id,
        data=data
    )