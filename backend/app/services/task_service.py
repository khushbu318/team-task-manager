from fastapi import HTTPException, status

# Task is the SQLAlchemy database model.
# It represents a task stored in the database.
from backend.app.models.task import Task

# User -> represents the logged-in user.
# UserRole -> contains the available roles such as:
#             TEAM_LEAD, EMPLOYEE, etc.
from backend.app.models.user import User, UserRole

# Repository is responsible for database operations.
# TaskService will use it instead of directly writing SQL queries.
from backend.app.repositories.task_repository import (
    TaskRepository,
)

# Schemas are used for validating incoming API data.
#
# TaskCreate -> data required when creating a task.
# TaskUpdate -> data allowed when updating a task.
from backend.app.schemas.task import (
    TaskCreate,
    TaskUpdate,
)


class TaskService:
    """
    Service layer containing the business logic for tasks.

    The Service layer sits between the API/router and repository.

    Router
       ↓
    TaskService  ← Business rules / authorization
       ↓
    TaskRepository  ← Database operations
       ↓
    Database
    """

    def __init__(
        self,
        task_repository: TaskRepository,
    ):
        # Dependency Injection.
        #
        # Instead of creating TaskRepository inside this class,
        # we receive it from outside.
        #
        # This makes the service easier to test and maintain.
        self.task_repository = task_repository

    def create_task(
        self,
        current_user: User,
        data: TaskCreate,
    ) -> Task:
        """
        Create a new task.

        current_user:
            The user who is currently logged in.

        data:
            The validated task data coming from the API request.

        Returns:
            The newly created Task object.
        """

        # ---------------------------------------------------------
        # STEP 1: Check ROLE-BASED authorization
        # ---------------------------------------------------------
        #
        # Only a TEAM_LEAD is allowed to create tasks.
        #
        # This is called RBAC:
        # Role-Based Access Control.
        #
        # Example:
        #
        # TEAM_LEAD  → can create task ✅
        # EMPLOYEE   → cannot create task ❌
        if current_user.role != UserRole.TEAM_LEAD:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Only team leads can create tasks",
            )

        # ---------------------------------------------------------
        # STEP 2: Create the Task database object
        # ---------------------------------------------------------
        #
        # data contains the information received from the API.
        #
        # We convert the Pydantic schema (TaskCreate)
        # into our SQLAlchemy model (Task).
        task = Task(
            title=data.title,
            description=data.description,
            assignee_id=data.assignee_id,
        )

        # ---------------------------------------------------------
        # STEP 3: Save the task in the database
        # ---------------------------------------------------------
        #
        # The Service does not directly interact with the DB.
        #
        # It asks the Repository to save the task.
        return self.task_repository.create(task)

    def get_tasks_for_user(
        self,
        current_user: User,
    ) -> list[Task]:
        """
        Get tasks visible to the current user.

        TEAM_LEAD:
            Can see ALL tasks.

        Normal employee:
            Can see only their own assigned tasks.
        """

        # ---------------------------------------------------------
        # TEAM LEAD → return ALL tasks
        # ---------------------------------------------------------
        #
        # A team lead has permission to see every task.
        if current_user.role == UserRole.TEAM_LEAD:
            return self.task_repository.get_all()

        # ---------------------------------------------------------
        # NORMAL USER → make sure we have their user ID
        # ---------------------------------------------------------
        #
        # We need the user's ID to find their tasks.
        #
        # If the ID is None, we cannot safely query:
        #
        #     "Give me tasks assigned to user ???"
        #
        # So we stop the request.
        if current_user.id is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="User ID is required",
            )

        # ---------------------------------------------------------
        # Get only tasks assigned to this user
        # ---------------------------------------------------------
        #
        # Example:
        #
        # current_user.id = 10
        #
        # Repository might execute something conceptually like:
        #
        # SELECT * FROM tasks
        # WHERE assignee_id = 10;
        #
        # The actual database query belongs inside the Repository.
        return self.task_repository.get_for_user(current_user.id)

    def update_task(
        self,
        current_user: User,
        task_id: int,
        data: TaskUpdate,
    ) -> Task:
        """
        Update an existing task.

        Authorization rules:

        TEAM_LEAD:
            Can update any task.

        Employee:
            Can update only their own assigned task.
        """

        # ---------------------------------------------------------
        # STEP 1: Find the task
        # ---------------------------------------------------------
        #
        # We first need to check whether the requested task exists.
        #
        # task_id comes from the API URL.
        #
        # Example:
        #
        # PUT /tasks/25
        #
        # task_id = 25
        task = self.task_repository.get_by_id(
            task_id
        )

        # ---------------------------------------------------------
        # STEP 2: Handle task not found
        # ---------------------------------------------------------
        #
        # If repository couldn't find the task,
        # it returns None.
        #
        # We then return HTTP 404 to the client.
        if not task:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Task not found",
            )

        # ---------------------------------------------------------
        # STEP 3: OBJECT-LEVEL AUTHORIZATION
        # ---------------------------------------------------------
        #
        # This is different from simply checking the user's role.
        #
        # We are checking:
        #
        # "Is this specific user allowed to modify
        #  THIS specific task?"
        #
        # Rules:
        #
        # TEAM_LEAD
        #     → can update any task
        #
        # EMPLOYEE
        #     → can update only a task assigned to themselves
        #
        # Example:
        #
        # Current user ID = 10
        # Task assignee ID = 20
        #
        # Employee 10 trying to update task belonging to 20
        #     → FORBIDDEN ❌
        #
        # But if user 10 is TEAM_LEAD
        #     → allowed ✅
        if (
            current_user.role != UserRole.TEAM_LEAD
            and task.assignee_id != current_user.id
        ):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You can update only your own tasks",
            )

        # ---------------------------------------------------------
        # STEP 4: Update only the fields that were provided
        # ---------------------------------------------------------
        #
        # TaskUpdate probably contains OPTIONAL fields.
        #
        # For example, the client may send:
        #
        # {
        #     "status": "completed"
        # }
        #
        # In that case we should update only status.
        #
        # We don't want to overwrite the other fields with None.

        if data.status is not None:
            task.status = data.status

        # Update current_state only when the client supplied it.
        if data.current_state is not None:
            task.current_state = data.current_state

        # Update blocker only when the client supplied it.
        if data.blocker is not None:
            task.blocker = data.blocker

        # Update permission_issue only when the client supplied it.
        if data.permission_issue is not None:
            task.permission_issue = data.permission_issue

        # ---------------------------------------------------------
        # STEP 5: Save the modified task
        # ---------------------------------------------------------
        #
        # At this point:
        #
        # 1. Task exists ✅
        # 2. User is authorized ✅
        # 3. Allowed fields have been updated ✅
        #
        # Now Repository persists the changes to the database.
        return self.task_repository.save(task)
