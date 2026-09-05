# ============================================================
# seed.py
# ============================================================
#
# This script is used to INSERT initial/test data into the
# database.
#
# It is commonly called a "database seeding" script.
#
# Why do we need it?
#
# When developing an application, we need some users to test:
#
#     Login
#     ↓
#     JWT generation
#     ↓
#     Authentication
#     ↓
#     Role-based access control (RBAC)
#     ↓
#     Task APIs
#
# Instead of manually creating users every time, we can run:
#
#     python seed.py
#
# and the required users will be created automatically.
#
# ============================================================


# Session  → Database session used to execute DB operations
# select   → Used to build SELECT queries
from sqlmodel import Session, select


# hash_password() converts a plain-text password into a
# secure password hash before storing it in the database.
#
# IMPORTANT:
# We should NEVER store plain-text passwords in the database.
#
# Example:
#
# "dev123"
#     ↓
# hash_password()
#     ↓
# "$2b$12$...."
#
from backend.app.core.security import hash_password


# create_db_and_tables()
#     → Creates database/tables if they don't exist.
#
# engine
#     → Database connection configuration used by SQLModel.
#
from backend.app.db.session import (
    create_db_and_tables,
    engine
)


# User     → Database model representing a user
# UserRole → Enum containing allowed user roles
#
# Example roles:
#
#     TEAM_LEAD
#     DEVELOPER
#
from backend.app.models.user import User, UserRole


# ============================================================
# Initial Users
# ============================================================
#
# These are the users that we want to create in the database.
#
# Keeping seed data in a list makes it easy to add/remove
# test users.
#
# NOTE:
# Passwords are plain text HERE only because this is seed
# input. They are hashed before being stored in the database.
#
# Database will NEVER receive these plain-text passwords.
#
USERS = [
    {
        "username": "alice",
        "full_name": "Alice Team Lead",
        "password": "lead123",
        "role": UserRole.TEAM_LEAD,
    },
    {
        "username": "dev1",
        "full_name": "Developer One",
        "password": "dev123",
        "role": UserRole.DEVELOPER,
    },
    {
        "username": "dev2",
        "full_name": "Developer Two",
        "password": "dev123",
        "role": UserRole.DEVELOPER,
    },
    {
        "username": "dev3",
        "full_name": "Developer Three",
        "password": "dev123",
        "role": UserRole.DEVELOPER,
    },
]


# ============================================================
# Seed Database
# ============================================================

def seed():

    # --------------------------------------------------------
    # Step 1: Create Database and Tables
    # --------------------------------------------------------
    #
    # If the database/tables don't exist, create them.
    #
    # This makes the seed script easier to run on a fresh
    # development environment.
    #
    create_db_and_tables()


    # --------------------------------------------------------
    # Step 2: Open Database Session
    # --------------------------------------------------------
    #
    # Session(engine) creates a database session.
    #
    # "with" automatically closes the session when we are done.
    #
    # Think:
    #
    #     Open DB connection
    #          ↓
    #       Do work
    #          ↓
    #     Close connection
    #
    with Session(engine) as session:

        # ----------------------------------------------------
        # Step 3: Process Each User
        # ----------------------------------------------------
        #
        # Go through every user defined in USERS.
        #
        for item in USERS:

            # ------------------------------------------------
            # Step 4: Check if User Already Exists
            # ------------------------------------------------
            #
            # Build a query equivalent to:
            #
            # SELECT *
            # FROM user
            # WHERE username = 'alice';
            #
            # select(User)
            #     → SELECT from User table
            #
            # where(...)
            #     → Add WHERE condition
            #
            # first()
            #     → Get the first matching record
            #
            existing = session.exec(
                select(User).where(
                    User.username == item["username"]
                )
            ).first()


            # ------------------------------------------------
            # Step 5: Skip Existing User
            # ------------------------------------------------
            #
            # If the username already exists, don't create
            # another user.
            #
            # This makes the seed script IDEMPOTENT.
            #
            # Idempotent means:
            #
            #     Run once  → creates users
            #     Run again → skips existing users
            #
            # It prevents duplicate users.
            #
            if existing:
                print(
                    f"skipping {item['username']} "
                    f"(already Exists)"
                )

                # Move to the next user.
                continue


            # ------------------------------------------------
            # Step 6: Create User Object
            # ------------------------------------------------
            #
            # Convert the seed dictionary into a User model.
            #
            # Notice that the plain-text password is NOT stored.
            #
            # Instead:
            #
            # item["password"]
            #       ↓
            # hash_password()
            #       ↓
            # password_hash
            #
            user = User(
                username=item["username"],
                full_name=item["full_name"],

                # NEVER store the plain-text password.
                # Store only its hash.
                password_hash=hash_password(
                    item["password"]
                ),

                role=item["role"],
            )


            # ------------------------------------------------
            # Step 7: Add User to Session
            # ------------------------------------------------
            #
            # session.add() tells SQLModel:
            #
            # "I want to INSERT this object into the DB."
            #
            # The actual INSERT may not happen immediately.
            # It will be persisted when session.commit()
            # is called.
            #
            session.add(user)


        # ----------------------------------------------------
        # Step 8: Commit Changes
        # ----------------------------------------------------
        #
        # commit() permanently saves all newly added users
        # to the database.
        #
        # Without commit():
        #
        #     session.add(user)
        #
        # does not permanently save the data.
        #
        session.commit()


    # Database session is automatically closed here because
    # we used:
    #
    #     with Session(engine) as session:
    #
    print("Seed Completed.")


# ============================================================
# Python Entry Point
# ============================================================
#
# This condition means:
#
# "Only execute seed() when this file is run directly."
#
# Example:
#
#     python seed.py
#
#     ↓
#
# __name__ == "__main__"
#
#     ↓
#
# seed()
#
#
# But if another file imports this module:
#
#     import seed
#
# seed() will NOT automatically execute.
#
# ============================================================

if __name__ == "__main__":
    seed()