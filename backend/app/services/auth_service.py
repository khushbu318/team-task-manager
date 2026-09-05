from fastapi import HTTPException, status

# create_access_token -> creates the JWT token after successful login
# verify_password -> checks whether the entered password matches
#                  the hashed password stored in the database
from backend.app.core.security import (
    create_access_token,
    verify_password,
)

# Repository is responsible for talking to the database.
# AuthService does NOT directly write SQL/database queries.
from backend.app.repositories.user_repository import (
    UserRepository,
)


class AuthService:
    """
    Service layer for authentication-related business logic.

    Think of AuthService as the "brain" of the login process.

    It:
    1. Finds the user
    2. Checks whether the user exists
    3. Verifies the password
    4. Creates and returns an access token
    """

    def __init__(
        self,
        user_repository: UserRepository,
    ):
        # Dependency Injection:
        # We receive UserRepository from outside instead of
        # creating it ourselves.
        #
        # This makes the service easier to test and maintain.
        self.user_repository = user_repository

    def login(
        self,
        username: str,
        password: str,
    ) -> str:
        """
        Authenticate a user and return a JWT access token.

        username -> username entered by the user
        password -> plain-text password entered by the user

        Returns:
            str: JWT access token
        """

        # STEP 1:
        # Ask the repository to find the user in the database
        # using the username.
        #
        # Repository handles DATABASE work.
        user = self.user_repository.get_by_username(
            username
        )

        # STEP 2:
        # If no user was found, stop the login process.
        #
        # We intentionally use the same error message for:
        # - username does not exist
        # - password is incorrect
        #
        # This prevents attackers from discovering which
        # usernames actually exist in the system.
        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid username or password",
            )

        # STEP 3:
        # Compare the password entered by the user
        # with the HASHED password stored in the database.
        #
        # verify_password() should internally hash/verify
        # the plain password against the stored hash.
        if not verify_password(
            password,
            user.password_hash,
        ):
            # Password is incorrect.
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid username or password",
            )

        if user.id is None:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="User has no valid ID",
            )

        # STEP 4:
        # Username + password are correct.
        #
        # Now create a JWT access token.
        #
        # We put some user information inside the token:
        # - user_id -> identifies the user
        # - username -> identifies the username
        # - role -> useful for RBAC/authorization
        #
        # The frontend/client can then send this token
        # with future API requests.
        return create_access_token(
            user_id=user.id,
            username=user.username,
            role=user.role.value,
        )
