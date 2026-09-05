# ============================================================
# deps.py
# ============================================================
#
# This file contains FastAPI dependencies related to:
#
# 1. JWT authentication
# 2. Getting the currently logged-in user
# 3. Role-based access control (RBAC)
#
# Think of this file as the "security gate" of the API.
#
# Request
#    ↓
# JWT Token
#    ↓
# get_current_user()
#    ↓
# Validate Token
#    ↓
# Find User in DB
#    ↓
# User object
#    ↓
# require_role()
#    ↓
# Check user's permission
#    ↓
# API endpoint
#
# ============================================================


from typing import Callable

# FastAPI tools used to create dependencies and HTTP errors
from fastapi import Depends, HTTPException, status

# OAuth2PasswordBearer extracts the Bearer token
# from the Authorization header.
#
# Example request:
#
# Authorization: Bearer eyJhbGciOiJIUzI1Ni...
#
from fastapi.security import OAuth2PasswordBearer

# JWTError is raised when a JWT token is invalid,
# malformed, or cannot be decoded.
from jose import JWTError

# SQLModel Session is used to communicate with the database.
from sqlmodel import Session


# ------------------------------------------------------------
# Application-specific imports
# ------------------------------------------------------------

# Function responsible for decoding and validating
# the JWT access token.
#
# This function should typically:
# - Verify the JWT signature
# - Check token expiration
# - Decode the payload
#
from backend.app.core.security import decode_access_token


# FastAPI database dependency.
#
# get_session() creates/provides a database session
# and FastAPI automatically injects it into our function.
from backend.app.db.session import get_session


# User model represents the user stored in the database.
#
# UserRole is an Enum containing roles such as:
#
# ADMIN
# USER
# MANAGER
#
from backend.app.models.user import User, UserRole


# Repository responsible for database operations
# related to User.
#
# Instead of writing SQL/database queries directly
# inside this dependency, we use the repository layer.
from backend.app.repositories.user_repository import (
    UserRepository,
)


# ============================================================
# OAuth2 / JWT Configuration
# ============================================================

# OAuth2PasswordBearer tells FastAPI:
#
# "This API expects a Bearer token in the Authorization header."
#
# Example:
#
# Authorization: Bearer <access_token>
#
# oauth2_scheme() will extract ONLY the token from the header.
#
# IMPORTANT:
# oauth2_scheme does NOT validate the JWT.
#
# It only extracts the token.
#
# JWT validation is performed later by:
#
#     decode_access_token(token)
#
oauth2_scheme = OAuth2PasswordBearer(
    tokenUrl="/auth/login"
)

# tokenUrl tells Swagger/OpenAPI where the user can obtain
# the access token.
#
# In Swagger UI, this allows FastAPI to understand that:
#
#     /auth/login
#
# is the endpoint used to authenticate the user.


# ============================================================
# Get Current Logged-In User
# ============================================================

def get_current_user(
    # --------------------------------------------------------
    # Step 1: Extract JWT token from Authorization header
    # --------------------------------------------------------
    #
    # Depends(oauth2_scheme) tells FastAPI:
    #
    # "Before executing get_current_user(),
    #  run oauth2_scheme()."
    #
    # oauth2_scheme extracts:
    #
    # Authorization: Bearer abc123
    #
    # and gives us:
    #
    # token = "abc123"
    #
    token: str = Depends(oauth2_scheme),

    # --------------------------------------------------------
    # Step 2: Get database session
    # --------------------------------------------------------
    #
    # Depends(get_session) tells FastAPI to create/provide
    # a database session for this request.
    #
    session: Session = Depends(get_session)

) -> User:

    # --------------------------------------------------------
    # Common error returned when authentication fails.
    # --------------------------------------------------------
    #
    # We intentionally use the same error for:
    #
    # - Missing/invalid JWT
    # - Expired JWT
    # - Invalid user ID
    # - User does not exist
    #
    # This prevents unnecessarily exposing authentication
    # details to the client.
    #
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Invalid or expired token",
        headers={
            # Tells the client that Bearer authentication
            # is required.
            "WWW-Authenticate": "Bearer"
        },
    )

    try:

        # ----------------------------------------------------
        # Step 3: Decode and validate JWT
        # ----------------------------------------------------
        #
        # decode_access_token() should verify the JWT.
        #
        # If the token is:
        #
        # - expired
        # - incorrectly signed
        # - malformed
        #
        # JWTError may be raised.
        #
        # Example decoded payload:
        #
        # {
        #     "sub": "123",
        #     "exp": 1780000000
        # }
        #
        payload = decode_access_token(token)

        # ----------------------------------------------------
        # Step 4: Get user ID from JWT payload
        # ----------------------------------------------------
        #
        # "sub" means "subject".
        #
        # In our application, we are using "sub" to store
        # the user's ID.
        #
        # Example:
        #
        # payload = {
        #     "sub": "123"
        # }
        #
        # Therefore:
        #
        # user_id = "123"
        #
        user_id = payload.get("sub")

        # If JWT does not contain "sub",
        # we cannot identify the user.
        if user_id is None:
            raise credentials_exception

        # JWT payload values may come back as strings.
        #
        # Convert:
        #
        #     "123"
        #
        # into:
        #
        #     123
        #
        # so that it can be used to query the database.
        user_id = int(user_id)

    except (
        # Invalid JWT
        JWTError,

        # int("abc") causes ValueError
        ValueError,

        # int(None) / unexpected type can cause TypeError
        TypeError

    ):
        # Any JWT parsing/conversion problem means that
        # authentication failed.
        raise credentials_exception

    # ========================================================
    # 3-LAYER ARCHITECTURE
    # ========================================================
    #
    # We are currently in the DEPENDENCY / API layer.
    #
    # Instead of directly writing:
    #
    #     session.get(User, user_id)
    #
    # we use the repository layer.
    #
    # Architecture:
    #
    # API / Dependency Layer
    #          ↓
    # Repository Layer
    #          ↓
    # Database
    #
    # UserRepository hides database access logic from
    # this authentication dependency.
    #
    repository = UserRepository(session)

    # --------------------------------------------------------
    # Step 5: Find user in database
    # --------------------------------------------------------
    #
    # JWT only tells us WHO the user claims to be.
    #
    # We still check the database to make sure that user
    # actually exists.
    #
    user = repository.get_by_id(user_id)

    # If JWT is valid but the user no longer exists
    # in the database, authentication should fail.
    #
    # Example:
    #
    # User was deleted from DB
    # but their old JWT is still being used.
    #
    if not user:
        raise credentials_exception

    # --------------------------------------------------------
    # Step 6: Return the User object
    # --------------------------------------------------------
    #
    # FastAPI can now inject this User object into another
    # endpoint using:
    #
    # current_user: User = Depends(get_current_user)
    #
    return user


# ============================================================
# Role-Based Access Control (RBAC)
# ============================================================

def require_role(
        # The role required to access an endpoint.
        #
        # Example:
        #
        # require_role(UserRole.ADMIN)
        #
        # means:
        #
        # "Only ADMIN users can access this endpoint."
        required_role: UserRole,
) -> Callable:

    # --------------------------------------------------------
    # This is a function that creates another function.
    #
    # This pattern is called a "closure" / "factory".
    #
    # Example:
    #
    # admin_required = require_role(UserRole.ADMIN)
    #
    # require_role() creates and returns role_checker().
    # --------------------------------------------------------

    def role_checker(

            # ------------------------------------------------
            # FastAPI first executes get_current_user().
            #
            # If JWT is invalid:
            #
            #     get_current_user()
            #              ↓
            #         401 Unauthorized
            #
            # If JWT is valid:
            #
            #     get_current_user()
            #              ↓
            #         User object
            #
            current_user: User = Depends(
                get_current_user
            ),

    ) -> User:

        # ----------------------------------------------------
        # Check whether the logged-in user's role matches
        # the role required by the endpoint.
        #
        # Example:
        #
        # current_user.role = UserRole.USER
        #
        # required_role = UserRole.ADMIN
        #
        # USER != ADMIN
        #
        # Therefore access is denied.
        # ----------------------------------------------------

        if current_user.role != required_role:

            # ------------------------------------------------
            # 401 vs 403
            # ------------------------------------------------
            #
            # 401 = "Who are you?"
            #
            # Used when authentication fails.
            #
            # 403 = "I know who you are,
            #        but you are not allowed."
            #
            # Therefore role failure should return 403.
            #
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Insufficient Permission"
            )

        # User has the required role.
        #
        # Return the user so the endpoint can also use:
        #
        # current_user.id
        # current_user.email
        # current_user.role
        #
        return current_user

    # Return the dependency function.
    #
    # This allows us to write:
    #
    # Depends(require_role(UserRole.ADMIN))
    #
    return role_checker