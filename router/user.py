from datetime import timedelta
from fastapi import APIRouter, status, Depends, Query, Path
from sqlalchemy.exc import NoResultFound, IntegrityError
from exceptions import DuplicateException, UnknownErrorException, NoRecordFound, InvalidCredentialsException
from request_body import UsersDetailsSchema
from sqlalchemy.orm import Session
from models import Users
from utils import get_db, validate_user_name, bcrypt_context, get_jwt_token

router = APIRouter(
    prefix="/auth",
    tags=["Users"]
)


@router.post("/", status_code=status.HTTP_201_CREATED)
def create_user(
        user_details: UsersDetailsSchema,
        db: Session = Depends(get_db)
):
    try:
        validate_user_name(user_details.user_name)
        user_obj = Users(
            user_name=user_details.user_name,
            first_name=user_details.first_name,
            last_name=user_details.last_name,
            email=user_details.email,
            role=user_details.role,
            hashed_password=bcrypt_context.hash(user_details.password)
        )

        db.add(user_obj)
        db.commit()

        return user_obj

    except IntegrityError:
        raise DuplicateException(
            status_code=status.HTTP_406_NOT_ACCEPTABLE,
            detail="same record, change it"
        )

    except InvalidCredentialsException as e:
        raise e

    except Exception:
        raise UnknownErrorException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred while saving user's details"
        )


@router.get("/token", status_code=status.HTTP_200_OK)
def get_token(
        user_name: str = Query(),
        password: str = Query(),
        db: Session = Depends(get_db)
):
    try:
        user_details = db.query(Users).filter(Users.user_name == user_name).one()
        if not bcrypt_context.verify(password, user_details.hashed_password):
            raise InvalidCredentialsException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Could not validate credentials"
            )

        token = get_jwt_token(user_name, user_details.id, timedelta(minutes=20))

        return {"token": token}

    except NoResultFound:
        raise NoRecordFound(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No record found for given user"
        )

    except InvalidCredentialsException as e:
        raise e

    except Exception:
        raise UnknownErrorException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred while matching user_name or password"
        )


@router.get("/", status_code=status.HTTP_200_OK)
def get_all_users(db: Session = Depends(get_db)):
    try:
        details = db.query(Users).all()
        return details

    except Exception:
        raise UnknownErrorException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error occurred while fetching user details"
        )


@router.delete("/{user_id}", status_code=status.HTTP_200_OK)
def delete_user(user_id: int = Path(), db: Session = Depends(get_db)):
    try:
        db.query(Users).filter(Users.id == user_id).one()
        db.query(Users).filter(Users.id == user_id).delete()
        db.commit()
        return {"msg": "deleted"}

    except NoResultFound:
        raise NoRecordFound(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No record found"
        )

    except Exception:
        raise UnknownErrorException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error occurred while fetching user details"
        )
