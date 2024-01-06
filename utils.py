from sqlalchemy import and_
from database import SessionLocal
from datetime import timedelta, datetime
from fastapi import status
from passlib.context import CryptContext
from exceptions import InvalidCredentialsException, ValidateTokenError
from jose import jwt, JWTError


bcrypt_context = CryptContext(schemes=['bcrypt'], deprecated='auto')
SECRET_KEY = "TODOS_@2023"
algorithm = "HS256"


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def validate_user_name(user_name):
    if len(user_name) == 0 or len(user_name) >= 15:
        raise InvalidCredentialsException(
            status_code=status.HTTP_406_NOT_ACCEPTABLE,
            detail="user_name should be greater than 0 & less than 16"
        )


def get_jwt_token(user_name: str, user_id: int, expire_time: timedelta):
    encode = {'sub': user_name, 'id': user_id}
    expiry = datetime.utcnow() + expire_time
    encode.update({'exp': expiry})
    return jwt.encode(encode, SECRET_KEY, algorithm)


def validate_token(token: str):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[algorithm])
        user_name = payload.get('sub')
        user_id = payload.get('id')

        if user_id is None or user_name is None:
            raise ValidateTokenError(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token"
            )
        return {'user_name': user_name, 'user_id': user_id}

    except JWTError:
        raise ValidateTokenError(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred while validating token"
        )


def get_todo(db, model, todo_id, user_id):
    try:
        details = db.query(model).filter(
            and_(
                model.id == todo_id,
                model.owner_id == user_id
            )
        ).one()
        return details
    except Exception as e:
        raise e