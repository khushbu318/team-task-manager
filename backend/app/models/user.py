

# Enum is used when a variable should have a fixed set of allowed values.
from enum import Enum

# Field      -> Used to configure database columns.
# Relationship -> Used to define relationships between database tables.
# SQLModel   -> Base class used to create SQLModel models/tables.
from sqlmodel import Field, Relationship, SQLModel

from typing import List, TYPE_CHECKING

if TYPE_CHECKING:
    from backend.app.models.task import Task

# ---------------------------------------------------------
# USER ROLE
# ---------------------------------------------------------

class UserRole(str, Enum):
    """
    Defines the roles that a user can have.

    Instead of allowing any random string such as:
        "admin"
        "abc"
        "hello"

    We restrict the role to the values defined below.
    """

    # "team_lead" is the actual value stored/used by the application.
    TEAM_LEAD = "team_lead"

    # Developer role
    DEVELOPER = "developer"


# ---------------------------------------------------------
# USER TABLE
# ---------------------------------------------------------

class User(SQLModel, table=True):
    """
    Represents a User database table.

    SQLModel combines:
        - Pydantic -> data validation
        - SQLAlchemy -> database ORM functionality

    table=True tells SQLModel:

        "Create a database table for this class."

    Without table=True, this would be a normal SQLModel/Pydantic
    model and would not represent a database table.
    """

    # Explicitly specify the database table name.
    #
    # Without this, SQLModel would generate a table name based
    # on the model name.
    __tablename__ = "users"


    # -----------------------------------------------------
    # PRIMARY KEY
    # -----------------------------------------------------

    id: int | None = Field(
        # None means we don't need to provide the ID when
        # creating a new user.
        #
        # The database will generate the ID automatically.
        default=None,

        # primary_key=True makes this column the PRIMARY KEY.
        #
        # A primary key uniquely identifies each row.
        primary_key=True
    )


    # -----------------------------------------------------
    # USERNAME
    # -----------------------------------------------------

    username: str = Field(
        # index=True creates a database index.
        #
        # This makes searches such as:
        #
        #     WHERE username = 'john'
        #
        # faster, especially when the table becomes large.
        index=True,

        # unique=True means two users cannot have
        # the same username.
        #
        # Example:
        #
        # User 1 -> john
        # User 2 -> john  ❌ Not allowed
        unique=True
    )


    # -----------------------------------------------------
    # FULL NAME
    # -----------------------------------------------------

    # A normal required string column.
    #
    # Example:
    #     "John Smith"
    #
    # Because there is no default value and it is not Optional,
    # a value is expected when creating a User.
    full_name: str


    # -----------------------------------------------------
    # PASSWORD HASH
    # -----------------------------------------------------

    # Stores the HASHED password.
    #
    # IMPORTANT:
    # We should NOT store the user's actual/plain-text password.
    #
    # Example:
    #
    # Plain password:
    #     "mypassword123"
    #
    # Stored in database:
    #     "$2b$12$...."
    #
    # The application should hash the password before storing it.
    password_hash: str


    # -----------------------------------------------------
    # USER ROLE
    # -----------------------------------------------------

    role: UserRole = Field(
        # If a role is not provided when creating a user,
        # the user will automatically become a DEVELOPER.
        #
        # Example:
        #
        # User(
        #     username="john",
        #     full_name="John Smith",
        #     password_hash="..."
        # )
        #
        # role will automatically be:
        #     UserRole.DEVELOPER
        default=UserRole.DEVELOPER
    )


    # -----------------------------------------------------
    # RELATIONSHIP WITH TASK
    # -----------------------------------------------------

    tasks: List["Task"] = Relationship(
        # This connects the User model with the Task model.
        #
        # back_populates="assignee" means:
        #
        # User.tasks  <---------------->  Task.assignee
        #
        # One User can have multiple Tasks.
        #
        # Example:
        #
        # User: John
        #     |
        #     ├── Task 1
        #     ├── Task 2
        #     └── Task 3
        #
        # The "assignee" side will be defined inside
        # the Task model.
        back_populates="assignee"
    )