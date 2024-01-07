from datetime import timedelta
from fastapi import APIRouter, status, Depends, Query, Path
from sqlalchemy.exc import NoResultFound, IntegrityError
from exceptions import DuplicateException, UnknownErrorException, NoRecordFound, InvalidCredentialsException, \
    NotAdminError, ValidateTokenError
from request_body import UsersDetailsSchema, UpdateUserDetails
from sqlalchemy.orm import Session
from models import Users
from utils import get_db, bcrypt_context, get_jwt_token, validate_token

router = APIRouter(
    prefix="/auth",
    tags=["Users"]
)


@router.post("/", status_code=status.HTTP_201_CREATED)
def create_user_account(
        user_details: UsersDetailsSchema,
        db: Session = Depends(get_db)
):
    try:
        user_obj = Users(
            user_name=user_details.user_name,
            email=user_details.email,
            hashed_password=bcrypt_context.hash(user_details.password)
        )

        db.add(user_obj)
        db.commit()

        response = {
            "user_id": user_obj.id,
            "message": "Account created. Please generate token to use other features"
        }

        return response

    except IntegrityError:
        raise DuplicateException(
            status_code=status.HTTP_406_NOT_ACCEPTABLE,
            detail="Same user name already exists"
        )

    except Exception:
        raise UnknownErrorException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred while saving user's details"
        )


@router.patch("/{user_id}", status_code=status.HTTP_201_CREATED)
def update_user_account(
        user_id: int,
        user_details: UpdateUserDetails,
        token: str = Query(),
        db: Session = Depends(get_db)
):
    try:
        details = validate_token(token)
        saved_user_id = details.get("user_id")
        if user_id != saved_user_id:
            raise InvalidCredentialsException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="user_id is incorrect"
            )
        result = db.query(Users).get(user_id)
        if user_details.user_name:
            result.user_name = user_details.user_name
        if user_details.email:
            result.email = user_details.email
        if user_details.password:
            result.password = user_details.password

        db.add(result)
        db.commit()

        return {"Successfully updated details"}

    except InvalidCredentialsException as exc:
        raise exc

    except ValidateTokenError as exc:
        raise exc

    except Exception as exc:
        raise UnknownErrorException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred while updating user's details"
        )


@router.get("/token", status_code=status.HTTP_200_OK)
def get_user_token(
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
def get_all_users(
        token: str = Query(),
        db: Session = Depends(get_db)):
    try:
        user_details = validate_token(token)
        user_name = user_details.get("user_name")
        if user_name != "amit_sahni":
            raise NotAdminError(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Only admin has rights to see the user details"
            )
        details = db.query(Users).all()
        return details

    except NotAdminError as exc:
        raise exc

    except Exception:
        raise UnknownErrorException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error occurred while fetching user details"
        )


@router.delete("/{user_id}", status_code=status.HTTP_200_OK)
def delete_user_account(
        user_id: int = Path(gt=0),
        token: str = Query(),
        db: Session = Depends(get_db)
):
    try:
        user_details = validate_token(token)
        saved_id = user_details.get("user_id")
        if user_id != saved_id:
            raise InvalidCredentialsException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="user_id is incorrect"
            )
        db.query(Users).filter(Users.id == user_id).one()
        db.query(Users).filter(Users.id == user_id).delete()
        db.commit()
        return {"User account is deleted."}

    except InvalidCredentialsException as exc:
        raise exc

    except NoResultFound:
        raise NoRecordFound(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No record found"
        )

    except NoRecordFound as exc:
        raise exc

    except Exception:
        raise UnknownErrorException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error occurred while fetching user details"
        )


@router.get("/{user_id}", status_code=status.HTTP_200_OK)
def get_user_details(
        user_id: int = Path(gt=0),
        token: str = Query(),
        db: Session = Depends(get_db)):
    try:
        user_details = validate_token(token)
        saved_id = user_details.get("user_id")
        if user_id != saved_id:
            raise InvalidCredentialsException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="user_id is incorrect"
            )
        details = db.query(Users).filter(Users.id == user_id).one()
        return details.__dict__

    except InvalidCredentialsException as exc:
        raise exc

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
