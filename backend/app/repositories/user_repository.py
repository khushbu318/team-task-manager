# Session -> represents a connection/session with the database.
#
# select -> used to build SQL SELECT queries using SQLModel.
from sqlmodel import Session, select


# Import the User model.
#
# User represents our `users` database table.
from backend.app.models.user import User


# ---------------------------------------------------------
# USER REPOSITORY
# ---------------------------------------------------------

class UserRepository:
    """
    Repository responsible for database operations related
    to the User model.

    Instead of writing database queries directly inside our
    API routes, we put them here.

    For example:

        API route
            ↓
        UserRepository
            ↓
        Database

    This keeps our code clean and separates responsibilities.
    """

    # -----------------------------------------------------
    # CONSTRUCTOR
    # -----------------------------------------------------

    def __init__(self, session: Session):
        """
        Receive a database session and store it inside
        the repository.

        `session` is the object we use to communicate
        with the database.

        Example:

            repository = UserRepository(session)

        After that, the repository can use:

            self.session
        """

        # Store the database session so all repository
        # methods can use the same session.
        self.session = session


    # -----------------------------------------------------
    # GET USER BY USERNAME
    # -----------------------------------------------------

    def get_by_username(
        self,
        username: str,
    ) -> User | None:
        """
        Find a user using their username.

        Returns:
            User -> if a matching user is found
            None -> if no user exists with that username
        """

        # Build a SELECT query.
        #
        # This is conceptually similar to SQL:
        #
        #     SELECT *
        #     FROM users
        #     WHERE username = 'john';
        #
        # `select(User)` means:
        #     Select records from the User table.
        #
        # `.where(...)` means:
        #     Apply a condition/filter.
        statement = select(User).where(
            User.username == username
        )


        # Execute the SQL statement using our database session.
        #
        # `.first()` returns the first matching record.
        #
        # If there is no matching user:
        #
        #     None
        #
        # is returned.
        return self.session.exec(
            statement
        ).first()


    # -----------------------------------------------------
    # GET USER BY ID
    # -----------------------------------------------------

    def get_by_id(
        self,
        user_id: int,
    ) -> User | None:
        """
        Find a user using their primary key (ID).

        Example:

            user_id = 5

        This asks the database:

            "Give me the User whose ID is 5."
        """

        # Session.get() is a convenient way to retrieve
        # an object using its primary key.
        #
        # User -> table/model we are searching
        #
        # user_id -> primary key value we want
        #
        # Conceptually:
        #
        #     SELECT *
        #     FROM users
        #     WHERE id = 5;
        #
        # Returns:
        #     User object if found
        #     None if not found
        return self.session.get(
            User,
            user_id,
        )


    # -----------------------------------------------------
    # CREATE USER
    # -----------------------------------------------------

    def create(
        self,
        user: User,
    ) -> User:
        """
        Add a new User to the database.

        `user` is a User object that we want to save.

        Example:

            user = User(
                username="john",
                password_hash="..."
            )

            repository.create(user)
        """

        # Add the User object to the current database session.
        #
        # IMPORTANT:
        # `add()` does NOT immediately save it permanently
        # to the database.
        #
        # It basically tells SQLAlchemy/SQLModel:
        #
        #     "I want to insert this object."
        self.session.add(user)


        # Commit the transaction.
        #
        # This actually saves the new user to the database.
        #
        # Conceptually:
        #
        #     INSERT INTO users (...)
        #
        # Without commit(), the changes may not be persisted.
        self.session.commit()


        # Refresh the User object with the values generated
        # by the database.
        #
        # This is particularly useful for automatically
        # generated fields such as:
        #
        #     id
        #
        # Before refresh:
        #
        #     user.id → None
        #
        # After database insert + refresh:
        #
        #     user.id → 1
        #
        self.session.refresh(user)


        # Return the newly created User object.
        #
        # The returned object now contains the database-
        # generated values such as its ID.
        return user