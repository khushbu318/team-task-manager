# Session -> used to communicate with the database.
#
# select -> used to build SELECT queries.
from sqlmodel import Session, select


# Import the Task model.
#
# Task represents the `tasks` table in our database.
from backend.app.models.task import Task


# ---------------------------------------------------------
# TASK REPOSITORY
# ---------------------------------------------------------

class TaskRepository:
    """
    Repository responsible for database operations
    related to Task.

    The repository keeps database logic separate from
    our API/service layer.

    Example flow:

        API
         ↓
        Service
         ↓
        TaskRepository
         ↓
        Database
    """

    # -----------------------------------------------------
    # CONSTRUCTOR
    # -----------------------------------------------------

    def __init__(self, session: Session):
        """
        Receive a database session and store it.

        `session` is our connection/session object that
        allows us to query and modify the database.
        """

        # Save the session so all methods in this repository
        # can use the same database session.
        self.session = session


    # -----------------------------------------------------
    # CREATE TASK
    # -----------------------------------------------------

    def create(self, task: Task) -> Task:
        """
        Create/save a new Task in the database.

        Example:

            task = Task(
                title="Learn FastAPI"
            )

            repository.create(task)
        """

        # Add the Task object to the current database session.
        #
        # At this point, we are telling SQLModel:
        #
        #     "I want to insert this task."
        #
        # It has not necessarily been permanently saved yet.
        self.session.add(task)


        # Commit the transaction.
        #
        # This actually saves the changes to the database.
        self.session.commit()


        # Refresh the object from the database.
        #
        # This is useful when the database generates values
        # automatically, such as:
        #
        #     id
        #
        # Example:
        #
        # Before commit:
        #     task.id = None
        #
        # After commit + refresh:
        #     task.id = 1
        self.session.refresh(task)


        # Return the newly created Task.
        return task


    # -----------------------------------------------------
    # GET TASK BY ID
    # -----------------------------------------------------

    def get_by_id(
        self,
        task_id: int,
    ) -> Task | None:
        """
        Find one Task using its primary key.

        Example:

            task_id = 10

        means:

            "Find the task whose ID is 10."

        Returns:
            Task -> if found
            None -> if not found
        """

        # session.get() is designed to retrieve an object
        # using its primary key.
        #
        # Task     -> model/table to search
        # task_id  -> primary key value
        return self.session.get(
            Task,
            task_id,
        )


    # -----------------------------------------------------
    # GET ALL TASKS
    # -----------------------------------------------------

    def get_all(self) -> list[Task]:
        """
        Return all tasks from the database.

        Returns:
            list[Task]

        Example:

            [
                Task(...),
                Task(...),
                Task(...)
            ]
        """

        # Build a SELECT query for the Task table.
        #
        # Conceptually this is:
        #
        #     SELECT * FROM tasks;
        statement = select(Task)


        # Execute the query using our database session.
        #
        # session.exec(statement)
        #     -> executes the query
        #
        # list(...)
        #     -> converts the returned results into a Python list
        return list(
            self.session.exec(statement)
        )


    # -----------------------------------------------------
    # GET TASKS FOR A SPECIFIC USER
    # -----------------------------------------------------

    def get_for_user(
        self,
        user_id: int,
    ) -> list[Task]:
        """
        Return all tasks assigned to a particular user.

        Example:

            get_for_user(5)

        means:

            "Give me all tasks where assignee_id = 5."
        """

        # Build a filtered SELECT query.
        #
        # Conceptually:
        #
        #     SELECT *
        #     FROM tasks
        #     WHERE assignee_id = 5;
        #
        # `Task.assignee_id` refers to the foreign-key column
        # connecting Task to User.
        statement = select(Task).where(
            Task.assignee_id == user_id
        )


        # Execute the query and convert the result
        # into a normal Python list.
        return list(
            self.session.exec(statement)
        )


    # -----------------------------------------------------
    # SAVE / UPDATE TASK
    # -----------------------------------------------------

    def save(self, task: Task) -> Task:
        """
        Save changes made to an existing Task.

        Example:

            task.status = TaskStatus.COMPLETED

            repository.save(task)

        The updated task will then be committed to
        the database.
        """

        # Add the modified Task to the session.
        self.session.add(task)


        # Commit the changes to the database.
        self.session.commit()


        # Refresh the object so it contains the latest
        # values from the database.
        self.session.refresh(task)


        # Return the updated Task.
        return task