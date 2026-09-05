# datetime is used to work with dates and times.
#
# timedelta is used to add/subtract a period of time.
#
# timezone is used so that our datetime is timezone-aware.
from datetime import datetime, timedelta, timezone


# JWTError -> exception raised when a JWT is invalid,
# expired, malformed, etc.
#
# jwt -> used to create (encode) and read/verify (decode)
# JSON Web Tokens.
from jose import JWTError, jwt


# PasswordHash is provided by pwdlib.
#
# It handles secure password hashing and verification.
#
# IMPORTANT:
# We NEVER want to store the user's plain-text password
# directly in the database.
from pwdlib import PasswordHash


# Import authentication configuration from our config file.
#
# ACCESS_TOKEN_EXPIRE_MINUTES
#     -> How long the JWT should remain valid.
#
# JWT_ALGORITHM
#     -> Algorithm used to sign the JWT.
#
# JWT_SECRET_KEY
#     -> Secret key used to sign and verify the JWT.
from backend.app.core.config import (
    ACCESS_TOKEN_EXPIRE_MINUTES,
    JWT_ALGORITHM,
    JWT_SECRET_KEY
)


# ---------------------------------------------------------
# PASSWORD HASHING
# ---------------------------------------------------------

# Create a PasswordHash object using pwdlib's recommended
# secure hashing configuration.
#
# We will use this object for:
#
#     password_hash.hash()
#     password_hash.verify()
#
password_hash = PasswordHash.recommended()


def hash_password(password: str) -> str:
    """
    Convert a plain-text password into a secure hash.

    Example:

        password = "mypassword123"

        hash_password(password)

    Result will look something like:

        "$argon2id$..."

    We store the HASH in the database,
    NOT the original password.
    """

    # password_hash.hash() takes the plain password
    # and generates a secure password hash.
    return password_hash.hash(password)


def verify_password(
        plain_password: str,
        hashed_password: str,
        ) -> bool:
    """
    Check whether a plain-text password matches
    the stored password hash.

    Example:

        User enters:
            "mypassword123"

        Database contains:
            "$argon2id$..."

        pwdlib checks whether they match.

    Returns:
        True  -> password is correct
        False -> password is incorrect
    """

    return password_hash.verify(
        # Password entered by the user.
        plain_password,

        # Hash stored in the database.
        hashed_password
    )


# ---------------------------------------------------------
# CREATE JWT ACCESS TOKEN
# ---------------------------------------------------------

def create_access_token(
        user_id: int,
        username: str,
        role: str,
) -> str:
    """
    Create a JWT access token for an authenticated user.

    The token contains information about the user
    and an expiration time.

    Example payload:

        {
            "sub": "10",
            "username": "khushbu",
            "role": "admin",
            "exp": "..."
        }
    """

    # Get the current time in UTC.
    #
    # timezone.utc is important because authentication
    # systems should generally use a consistent timezone.
    #
    # Then add the configured number of minutes.
    #
    # Example:
    #
    # Current time = 10:00
    # Expiration   = 10:30
    #
    # if ACCESS_TOKEN_EXPIRE_MINUTES = 30
    expire = datetime.now(
        timezone.utc
    ) + timedelta(
        minutes=ACCESS_TOKEN_EXPIRE_MINUTES
    )


    # -----------------------------------------------------
    # JWT PAYLOAD
    # -----------------------------------------------------

    # The payload is the data stored inside the JWT.
    #
    # IMPORTANT:
    # JWT payload is NOT encrypted by default.
    # It is encoded and signed.
    #
    # Therefore, don't put sensitive information such as:
    #
    #     password
    #     credit card number
    #     secrets
    #
    # inside the payload.
    payload = {
        # "sub" means "subject".
        #
        # Usually we use it to identify the user.
        #
        # We convert user_id to string because the JWT
        # subject claim is conventionally represented as a string.
        "sub": str(user_id),

        # Store the username in the token.
        "username": username,

        # Store the user's role.
        #
        # This can later be used for authorization/RBAC.
        #
        # Example:
        #
        #     admin
        #     manager
        #     member
        "role": role,

        # Token expiration time.
        #
        # Once this time is reached, the JWT becomes invalid.
        "exp": expire,
    }


    # -----------------------------------------------------
    # ENCODE / SIGN JWT
    # -----------------------------------------------------

    return jwt.encode(
        # Data we want to put inside the token.
        payload,

        # Secret key used to sign the token.
        #
        # This should be kept secret and normally loaded
        # from environment variables/configuration.
        JWT_SECRET_KEY,

        # Algorithm used to create the JWT signature.
        #
        # Example:
        #     HS256
        algorithm=JWT_ALGORITHM,

        # algorithms=[JWT_ALGORITHM] #That makes the expected API explicit and avoids issues depending on the library/version.
    )


# ---------------------------------------------------------
# DECODE / VERIFY JWT
# ---------------------------------------------------------

def decode_access_token(token: str) -> dict:
    """
    Decode and verify a JWT access token.

    This function checks things such as:
    
    1. Is the token correctly signed?
    2. Is the token valid?
    3. Has the token expired?

    If everything is valid, it returns the payload.

    If something is wrong, python-jose can raise JWTError.
    """

    return jwt.decode(
        # JWT received from the client.
        token,

        # Same secret key that was used to create the token.
        JWT_SECRET_KEY,

        # Only allow the configured algorithm.
        algorithms=JWT_ALGORITHM,
    )