

# Enum is used to create a fixed set of allowed values.
# For example, a task can only have:
# todo, in_progress, blocked, or completed.
from enum import Enum

# SQLModel is used to define database models using Python classes.
# Field is used to configure individual database columns.
# Relationship is used to define relationships between tables.
from sqlmodel import Field, Relationship, SQLModel

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from backend.app.models.user import User


# ---------------------------------------------------------
# TASK STATUS
# ---------------------------------------------------------

class TaskStatus(str, Enum):
    """
    Enum representing the possible statuses of a Task.

    Why Enum?
    ---------
    Instead of allowing someone to write any random status like:

        status = "hello"

    We restrict the status to a predefined set of values.

    Why (str, Enum)?
    ----------------
    `str` makes the enum values behave like strings.

    So:

        TaskStatus.TODO

    has the value:

        "todo"
    """

    TODO = "todo"

    # Task has been started and is currently being worked on.
    IN_PROGRESS = "in_progress"

    # Task cannot continue because something is preventing it.
    BLOCKED = "blocked"

    # Task has been successfully finished.
    COMPLETED = "completed"


# ---------------------------------------------------------
# TASK DATABASE MODEL
# ---------------------------------------------------------

class Task(SQLModel, table=True):
    """
    Represents a Task table in the database.

    `SQLModel` allows us to use one Python class for:
    
    1. Python data validation
    2. Database table definition

    `table=True` is VERY important.

    It tells SQLModel:

        "This class should become a database table."

    Without `table=True`, this would just be a normal SQLModel
    data model and would not create a database table.
    """

    # Name of the database table.
    #
    # By default SQLModel may generate a table name based on
    # the class name, but here we explicitly say:
    #
    #     CREATE TABLE tasks (...)
    #
    __tablename__ = "tasks"


    # -----------------------------------------------------
    # ID
    # -----------------------------------------------------

    id: int | None = Field(
        # `None` means we don't have to provide the ID when
        # creating a new Task.
        #
        # Example:
        #
        #     Task(title="Learn FastAPI")
        #
        # We don't provide id.
        #
        # The database will generate it automatically.
        default=None,

        # This column is the PRIMARY KEY.
        #
        # A primary key uniquely identifies each row.
        #
        # Example:
        #
        #     1 -> Learn FastAPI
        #     2 -> Learn SQLModel
        #     3 -> Build API
        #
        primary_key=True
    )


    # -----------------------------------------------------
    # TITLE
    # -----------------------------------------------------

    title: str

    # `title` is a required string field.
    #
    # Because there is no default value:
    #
    #     title: str
    #
    # we must provide it when creating a Task.
    #
    # Example:
    #
    #     Task(title="Learn FastAPI")
    #
    # If we try:
    #
    #     Task()
    #
    # validation will fail.


    # -----------------------------------------------------
    # DESCRIPTION
    # -----------------------------------------------------

    description: str | None = None

    # `str | None` means:
    #
    #     This field can contain a string OR None.
    #
    # `= None` means it is optional.
    #
    # Example:
    #
    #     Task(
    #         title="Learn FastAPI",
    #         description="Learn routing and dependency injection"
    #     )
    #
    # OR:
    #
    #     Task(title="Learn FastAPI")
    #
    # Both are valid.


    # -----------------------------------------------------
    # STATUS
    # -----------------------------------------------------

    status: TaskStatus = Field(
        # Every new task will start with TODO
        # unless another status is explicitly provided.
        default=TaskStatus.TODO
    )

    # Notice that the type is NOT:
    #
    #     status: str
    #
    # Instead:
    #
    #     status: TaskStatus
    #
    # This means the status should be one of the values
    # defined inside our TaskStatus Enum.
    #
    # Example:
    #
    #     TaskStatus.TODO
    #     TaskStatus.IN_PROGRESS
    #     TaskStatus.BLOCKED
    #     TaskStatus.COMPLETED


    # -----------------------------------------------------
    # CURRENT STATE
    # -----------------------------------------------------

    current_state: str | None = None

    # Stores information about what is currently happening
    # with the task.
    #
    # Example:
    #
    #     "Waiting for API response"
    #
    #     "Running browser automation"
    #
    #     "Waiting for user approval"
    #
    # It is optional, so it can also be None.


    # -----------------------------------------------------
    # BLOCKER
    # -----------------------------------------------------

    blocker: str | None = None

    # Stores information about something preventing the
    # task from progressing.
    #
    # Example:
    #
    #     blocker = "Payer portal is unavailable"
    #
    # If there is no blocker:
    #
    #     blocker = None


    # -----------------------------------------------------
    # PERMISSION ISSUE
    # -----------------------------------------------------

    permission_issue: str | None = None

    # Stores information about permission/access problems.
    #
    # Example:
    #
    #     "User does not have permission to submit PA request"
    #
    # If there is no permission problem:
    #
    #     permission_issue = None

    # -----------------------------------------
    # FOREIGN KEY
    # -----------------------------------------

    assignee_id: int | None = Field(
        default=None,
        foreign_key="users.id"
    )
    
    # -----------------------------------------------------
    # ASSIGNEE / USER RELATIONSHIP
    # -----------------------------------------------------

    assignee: "User" = Relationship(
        back_populates="tasks"
    )

    # This is NOT a normal database column like `title`.
    #
    # It represents a RELATIONSHIP between Task and User.
    #
    # Meaning:
    #
    #     One Task belongs to a User.
    #
    # Example:
    #
    #     Task 1 -> assigned to Alice
    #     Task 2 -> assigned to Alice
    #     Task 3 -> assigned to Bob
    #
    # `User` is written as a string:
    #
    #     "User"
    #
    # because the User class may be defined somewhere else
    # or later in the code.
    #
    # `back_populates="tasks"` means the User model should
    # have a matching relationship called `tasks`.
    #
    # So we can navigate in both directions:
    #
    #     task.assignee
    #
    # gives us the User assigned to the task.
    #
    # And:
    #
    #     user.tasks
    #
    # gives us all tasks assigned to that User.