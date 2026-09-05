# Import UserRole and User from the user model.
#
# UserRole -> Enum containing the possible user roles
# User     -> SQLModel representing the User database table
from backend.app.models.user import UserRole, User


# Import TaskStatus and Task from the task model.
#
# TaskStatus -> Enum containing task statuses
# Task       -> SQLModel representing the Task database table
from backend.app.models.task import TaskStatus, Task


# __all__ defines what should be considered the
# "public" members of this module.
#
# In other words, these are the names we want to expose
# when someone imports everything from this file:
#
#     from backend.app.models import *
#
# Python will use this list to know what to import.
__all__ = [
    "User",
    "UserRole",
    "Task",
    "TaskStatus"
]