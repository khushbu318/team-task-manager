# FastAPI is the framework we use to create our API.
#
# FastAPI gives us things like:
# - API routes
# - Request/response handling
# - Automatic validation
# - Swagger documentation
from fastapi import FastAPI


# Import our database initialization function.
#
# This function is responsible for creating the database
# tables when the application starts.
from backend.app.db.session import create_db_and_tables


# asynccontextmanager helps us define code that should run
# when the application starts and/or shuts down.
#
# Think of it like:
#
#     START application
#          ↓
#     run startup code
#          ↓
#     application is running
#          ↓
#     run shutdown code
#
from contextlib import asynccontextmanager

# ============================================================
# API ROUTERS
# ============================================================
#
# Import routers from individual modules.
#
# Each router contains endpoints for a specific feature:
#
# auth_router  → /auth/*
# task_router  → /tasks/*
#
# Keeping routes separated by feature makes the application
# easier to maintain as the project grows.
#
from backend.app.api.routes.auth import router as auth_router
from backend.app.api.routes.tasks import router as task_router


# ---------------------------------------------------------
# APPLICATION LIFESPAN
# ---------------------------------------------------------

@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Code inside this function controls the application
    startup and shutdown lifecycle.

    Everything BEFORE `yield`
        → runs when FastAPI starts.

    `yield`
        → means "the application can now run".

    Everything AFTER `yield`
        → would run when FastAPI shuts down.
    """

    # Create the database and database tables when
    # the FastAPI application starts.
    #
    # For example:
    #
    #     CREATE TABLE user (...)
    #     CREATE TABLE tasks (...)
    #
    create_db_and_tables()


    # `yield` tells FastAPI:
    #
    # "Startup is finished.
    #  Now allow the application to serve requests."
    yield


# ---------------------------------------------------------
# CREATE FASTAPI APPLICATION
# ---------------------------------------------------------

app = FastAPI(
    # Name displayed in Swagger/OpenAPI documentation.
    title="Team Task Manager API",

    # Version of our API.
    version="1.0.0",

    # IMPORTANT:
    # Your original code defines `lifespan()` but does not
    # connect it to FastAPI.
    #
    # We should pass it here:
    #
    # lifespan=lifespan
    #
    # Otherwise FastAPI will NOT execute the lifespan
    # function automatically.
    lifespan=lifespan
)

# ============================================================
# Register API Routers
# ============================================================
#
# include_router() connects the individual routers to the
# main FastAPI application.
#
# Without include_router(), FastAPI will not know about
# these endpoints.
#
# Authentication routes:
#
#     /auth/login
#
# Task routes:
#
#     /tasks
#     /tasks/{task_id}
#
# The prefix defined inside each router is automatically
# applied to its endpoints.
#
app.include_router(auth_router)
app.include_router(task_router)


# ---------------------------------------------------------
# ROOT API ENDPOINT
# ---------------------------------------------------------

@app.get("/")
def root():
    """
    Handles GET requests to:

        /

    Example:

        GET http://localhost:8000/

    FastAPI calls this function whenever someone visits
    the root URL.
    """

    # FastAPI automatically converts this Python dictionary
    # into a JSON response.
    return {
        "message": "Team Task Manager API is Running"
    }