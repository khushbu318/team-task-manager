# ============================================================
# auth.py
# ============================================================
#
# This file contains the Authentication API endpoints.
#
# This is the ROUTER / CONTROLLER layer of our
# 3-layer architecture.
#
# The responsibility of this layer is mainly:
#
# 1. Receive HTTP request
# 2. Validate request data using Pydantic schema
# 3. Get database session
# 4. Create repository
# 5. Call service
# 6. Return API response
#
# Business logic should NOT be written here.
#
#
# 3-LAYER ARCHITECTURE
#
#        Client
#          │
#          ▼
#     Router / API
#       (this file)
#          │
#          ▼
#       Service
#     (business logic)
#          │
#          ▼
#     Repository
#    (DB operations)
#          │
#          ▼
#       Database
#
# ============================================================


# APIRouter is used to create a group of related API endpoints.
#
# Depends is FastAPI's Dependency Injection mechanism.
#
# Example:
#
# session: Session = Depends(get_session)
#
# means FastAPI will automatically provide a database session.
#
from fastapi import APIRouter, Depends


# Session represents a SQLModel database session.
#
# It is used to communicate with the database.
from sqlmodel import Session


# Database dependency.
#
# get_session() is responsible for creating/providing
# a database session for the current request.
#
# The router does not need to manually create a DB connection.
# FastAPI's dependency injection handles it.
from backend.app.db.session import get_session


# Repository layer.
#
# UserRepository contains database-related operations
# for the User model.
#
# For example:
#
#     get_by_id()
#     get_by_username()
#     create_user()
#
# The router should NOT directly write SQL queries.
from backend.app.repositories.user_repository import (
    UserRepository,
)


# Pydantic request/response schemas.
#
# LoginRequest:
#     Defines what data the client must send.
#
# TokenResponse:
#     Defines what the API will return.
#
from backend.app.schemas.auth import (
    LoginRequest,
    TokenResponse
)


# Service layer.
#
# AuthService contains the actual authentication
# business logic.
#
# For example:
#
# - Find user
# - Verify password
# - Generate JWT
#
# The router simply calls the service.
from backend.app.services.auth_service import (
    AuthService,
)

from fastapi import APIRouter, Depends
from fastapi.security import OAuth2PasswordRequestForm
from sqlmodel import Session

# ============================================================
# Create Authentication Router
# ============================================================

router = APIRouter(
    # Every endpoint inside this router will start with /auth.
    #
    # Therefore:
    #
    # "/login"
    #
    # becomes:
    #
    # "/auth/login"
    #
    prefix="/auth",

    # Used by Swagger/OpenAPI to group these endpoints
    # under the "Authentication" section.
    tags=["Authentication"],
)


# ============================================================
# Login Endpoint
# ============================================================

@router.post(
    "/login",

    # The final response must follow TokenResponse schema.
    #
    # Example response:
    #
    # {
    #     "access_token": "eyJhbGciOi...",
    #     "token_type": "bearer"
    # }
    #
    # FastAPI will validate/serialize the returned data
    # according to TokenResponse.
    response_model=TokenResponse
)
@router.post("/login", response_model=TokenResponse)
def login(
    # Swagger OAuth2 sends username/password
    # as FORM DATA, not JSON.
    #
    # OAuth2PasswordRequestForm reads:
    #
    # username
    # password
    #
    # from the incoming form request.
    form_data: OAuth2PasswordRequestForm = Depends(),

    # Get database session.
    session: Session = Depends(get_session)
):
    # Create repository.
    repository = UserRepository(session)

    # Create service.
    service = AuthService(repository)

    # Authenticate user.
    token = service.login(
        username=form_data.username,
        password=form_data.password,
    )

    # Return JWT token.
    return TokenResponse(
        access_token=token,
        token_type="bearer",
    )

