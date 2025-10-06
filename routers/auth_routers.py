from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import OAuth2PasswordRequestForm
from models import User
from dependencies import get_session, verify_token
from main import argon2_context, SECRET_KEY, ALGORITHM, ACCESS_TOKEN_EXPIRE_MINUTES
from schemas import UserSchema, LoginSchema
from sqlalchemy.orm import Session
from jose import jwt, JWTError
from datetime import datetime, timedelta, timezone

auth_router = APIRouter(prefix="/auth", tags=["Auth"])

def get_token(user_id, token_time=timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)):
    expiration_date = datetime.now(timezone.utc) + token_time
    expiration_date_timestamp = int(expiration_date.timestamp())
    dict_info = {"sub": str(user_id), "exp": expiration_date_timestamp}
    encoded_jwt = jwt.encode(dict_info, SECRET_KEY, ALGORITHM)
    return encoded_jwt


def authenticate_user(email, password, session):
    user = session.query(User).filter(User.email == email).first()
    if not user:
        return False
    elif not argon2_context.verify(password, user.password):
        return False
    return user


@auth_router.get("/")
async def home():
    """
    Default authentication route.

    This endpoint serves as the base authentication route of the system.
    It can be used to verify that the authentication module is active
    and reachable. The response includes a simple confirmation message
    and an authentication flag.

    Returns:
        dict: A JSON object containing a response message and the
        authentication status (always False for this route).
    """
    return {"response": "You have accessed the default authentication route", "auth": False}

@auth_router.post("/signup")
async def signup(
    user_schema: UserSchema,
    session: Session = Depends(get_session),
    current_user: User = Depends(verify_token) 
):
    """
    Register a new user account.

    This endpoint handles user registration in the authentication system.
    It verifies whether a user with the given email already exists and
    enforces admin creation rules:
    - If at least one admin exists, only an existing admin can create another admin user.
    - If no admin exists yet, the first registered user can be an admin.

    The password is securely hashed using Argon2 before storing the new user
    in the database.

    Args:
        user_schema (UserSchema): The user data payload containing name, email,
            password, activation status, and admin flag.
        session (Session): SQLAlchemy database session dependency.
        current_user (User): The currently authenticated user (used to verify
            admin privileges).

    Raises:
        HTTPException: If the email is already registered.
        HTTPException: If a non-admin user attempts to create an admin account.

    Returns:
        dict: A confirmation message indicating successful user registration.
    """
    existing_user = session.query(User).filter(User.email == user_schema.email).first()
    if existing_user:
        raise HTTPException(status_code=400, detail="This user already exists with this email.")
    
    admin_user = session.query(User).filter(User.admin == True).first()
    if admin_user and user_schema.admin:
        if not current_user or not current_user.admin:
            raise HTTPException(status_code=403, detail="Only admins can create new admin users.")

    hash_password = argon2_context.hash(user_schema.password)
    new_user = User(user_schema.name, user_schema.email, hash_password, user_schema.activated, user_schema.admin)
    session.add(new_user)
    session.commit()
    return {"response": f"User {user_schema.email} registered successfully."}
    
@auth_router.post("/signup_admin")
async def signup(
    user_schema: UserSchema,
    session: Session = Depends(get_session), 
):

    existing_user = session.query(User).filter(User.email == user_schema.email).first()
    if existing_user:
        raise HTTPException(status_code=400, detail="This user already exists with this email.")
    else:
        hash_password = argon2_context.hash(user_schema.password[:72])
        new_user = User(user_schema.name, user_schema.email, hash_password, user_schema.activated, user_schema.admin)
        session.add(new_user)
        session.commit()
        return {"response": f"User {user_schema.email} registered successfully."}
    
@auth_router.post("/login")
async def login(
    login_schema: LoginSchema,
    session: Session = Depends(get_session)
    ):
    """Authenticate a user and issue access tokens.

    This endpoint validates the provided user credentials (email and password)
    against the database. If authentication is successful, it generates both
    an access token and a refresh token for the user session.

    The access token is used for short-term authentication in API requests,
    while the refresh token allows the client to request a new access token
    without re-entering credentials.

    Args:
        login_schema (LoginSchema): The login credentials, including email and password.
        session (Session): SQLAlchemy database session dependency.

    Raises:
        HTTPException: If the user is not found or the password is invalid (status code 400).

    Returns:
        dict: A JSON object containing:
            - `access_token` (str): The short-term JWT access token.
            - `refresh_token` (str): The long-term JWT refresh token (valid for 7 days).
            - `token_type` (str): The type of token, always `"Bearer"`.
    """
    user = authenticate_user(login_schema.email, login_schema.password, session)
    if not user:
        raise HTTPException(status_code=400, detail="User not found or invalid password.")
    else:
        access_token = get_token(user.id)
        refresh_token = get_token(user.id, timedelta(days=7))
        return {
            "access_token": access_token,
            "refresh_token": refresh_token,
            "token_type": "Bearer"
            }

@auth_router.post("/login_form")
async def login_form(
    form_data: OAuth2PasswordRequestForm = Depends(),
    session: Session = Depends(get_session)
    ):
    """
    Authenticate a user using form-based credentials and return an access token.

    This endpoint performs user authentication using data submitted through
    the OAuth2 password grant flow (typically via a login form). It verifies
    the provided username (email) and password against stored credentials.
    Upon successful authentication, it issues a short-term access token.

    This route is commonly used for browser-based or OAuth2-compliant clients
    that submit login information via `application/x-www-form-urlencoded`.

    Args:
        form_data (OAuth2PasswordRequestForm): The form data containing the
            username (email) and password fields.
        session (Session): SQLAlchemy database session dependency.

    Raises:
        HTTPException: If the user is not found or the password is invalid (status code 400).

    Returns:
        dict: A JSON object containing:
            - `access_token` (str): The JWT access token for authenticated requests.
            - `token_type` (str): The type of token, always `"Bearer"`.
    """
    user = authenticate_user(form_data.username, form_data.password, session)
    if not user:
        raise HTTPException(status_code=400, detail="User not found or invalid password.")
    else:
        access_token = get_token(user.id)
        return {
            "access_token": access_token,
            "token_type": "Bearer"
            }
        
@auth_router.get("/refresh")
async def user_refresh_token(user: User = Depends(verify_token)):
    """
    Refresh the user's access token.

    This endpoint generates a new short-term access token for an authenticated user.
    It requires a valid refresh token or an existing authentication token to be
    provided via dependency injection (`verify_token`).

    The refreshed access token allows the user to maintain an active session
    without re-entering login credentials.

    Args:
        user (User): The authenticated user extracted from the current valid token.

    Returns:
        dict: A JSON object containing:
            - `access_token` (str): A newly issued JWT access token.
            - `token_type` (str): The type of token, always `"Bearer"`.
    """
    access_token = get_token(user.id)
    return {
            "access_token": access_token,
            "token_type": "Bearer"
            }