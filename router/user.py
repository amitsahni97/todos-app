from datetime import timedelta
from fastapi import APIRouter, status, Depends, HTTPException, Query, Path
from sqlalchemy.exc import NoResultFound, IntegrityError
from exceptions import invalid_credentials_exception
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

    except Exception as error:
        if type(error) == IntegrityError:
            raise HTTPException(
                        status_code=status.HTTP_406_NOT_ACCEPTABLE,
                        detail="Same user name exists"
                    )
        raise HTTPException(
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
            return invalid_credentials_exception()

        token = get_jwt_token(user_name, user_details.id, timedelta(minutes=20))

        return {"token": token}
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred while matching user_name or password"
        )


@router.get("/", status_code=status.HTTP_200_OK)
def get_all_users(db: Session = Depends(get_db)):
    try:
        details = db.query(Users).all()
        return details

    except Exception as e:
        print("errro------>", str(e))
        import traceback
        traceback.print_exc()
        raise HTTPException(
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
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No record found"
        )

    except Exception:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error occurred while fetching user details"
        )
