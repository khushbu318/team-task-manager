# Import SQLModel utilities:
# Session -> used to interact with the database
# SQLModel -> used to create database tables from models
# create_engine -> creates a connection/engine to the database
from sqlmodel import Session, SQLModel, create_engine

# Import the database URL from the application configuration
from backend.app.core.config import DATABASE_URL

from backend.app.models import User, Task

# Dictionary used to store database-specific connection arguments
connect_args = {}

# SQLite has a special requirement when the same database connection
# can be accessed from different threads.
if DATABASE_URL.startswith("sqlite"):

    # Allow SQLite connection to be used across multiple threads
    connect_args = {
        "check_same_thread": False
    }


# Create the database engine.
# The engine is responsible for managing connections to the database.
engine = create_engine(
    DATABASE_URL,

    # echo=False means SQL queries will NOT be printed in the console.
    # Set echo=True while debugging if you want to see generated SQL.
    echo=True,

    # Pass database-specific connection arguments.
    connect_args=connect_args
)


def create_db_and_tables():
    """
    Create all database tables defined using SQLModel.

    SQLModel.metadata contains information about all registered
    SQLModel classes/tables.

    create_all() creates the tables if they don't already exist.
    """
    SQLModel.metadata.create_all(engine)


def get_session():
    """
    Provide a database session to the application.

    A session is used to perform database operations such as:
    - SELECT
    - INSERT
    - UPDATE
    - DELETE

    'yield' makes this function useful as a FastAPI dependency.

    The 'with' block automatically closes the session after
    the request is completed.
    """
    with Session(engine) as session:
        yield session