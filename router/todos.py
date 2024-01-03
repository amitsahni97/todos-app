from fastapi import APIRouter, status
from typing import Optional
from fastapi import Depends, HTTPException, Path, Query
from sqlalchemy import and_
from sqlalchemy.exc import NoResultFound
from sqlalchemy.orm import Session
from exceptions import ValidateTokenError
from models import Todos
from request_body import TodoRequestSchema
from utils import get_db, get_todo
from utils import validate_token

todo_router = APIRouter(
    prefix="/todos",
    tags=["Todos"]
)


@todo_router.post("/", status_code=status.HTTP_201_CREATED)
def save_todo(
        details: TodoRequestSchema,
        token: str = Query(),
        db: Session = Depends(get_db)
):
    try:
        user_details = validate_token(token)
        todos = Todos(**details.model_dump(), owner_id=user_details.get('user_id'))
        db.add(todos)
        db.commit()

    except ValidateTokenError as e:
        raise e

    except Exception:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred while saving details to db"
        )


@todo_router.patch("/{todo_id}", status_code=status.HTTP_202_ACCEPTED)
def update_todo(
        token: str,
        todo_id: int = Path(gt=0),
        title: Optional[str] = Query(min_length=3),
        description: Optional[str] = Query(min_length=3),
        priority: Optional[int] = Query(default=1),
        db: Session = Depends(get_db)
):
    try:
        user_details = validate_token(token)
        result = db.query(Todos).filter(
            and_(
                Todos.id == todo_id,
                Todos.owner_id == user_details.get("user_id")
            )
        ).one()
        if title:
            result.title = title
        if description:
            result.description = description
        if priority:
            result.priority = priority
        db.add(result)
        db.commit()

    except ValidateTokenError as e:
        raise e

    except NoResultFound:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No Todo found"
        )

    except Exception:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error occurred while updating details"
        )


@todo_router.get("/{todo_id}", status_code=status.HTTP_200_OK)
def get_particular_todo(
        token: str,
        todo_id: int = Path(gt=0),
        db: Session = Depends(get_db)
):
    try:
        user_details = validate_token(token)
        result = db.query(Todos).filter(
            and_(
                Todos.owner_id == user_details.get("user_id"),
                Todos.id == todo_id
            )
        ).all()
        return result

    except ValidateTokenError as e:
        raise e

    except Exception:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail='An error occurred while fetching details'
        )


@todo_router.get("/", status_code=status.HTTP_200_OK)
def get_all_todos(
        token: str,
        db: Session = Depends(get_db)
):
    try:
        user_details = validate_token(token)
        result = db.query(Todos).filter(
                Todos.owner_id == user_details.get("user_id")
        ).all()
        return result

    # except invalid_token_exception as e:
    #     raise e

    except ValidateTokenError as e:
        raise e

    except Exception:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail='An error occurred while fetching details'
        )


@todo_router.delete("/{todo_id}", status_code=status.HTTP_200_OK)
def delete_particular_todo(
        token: str,
        todo_id: int = Path(gt=0),
        db: Session = Depends(get_db)
):
    try:
        user_details = validate_token(token)
        get_todo(db, Todos, todo_id, user_details.get("user_id"))
        db.query(Todos).filter(
            and_(
                Todos.id == todo_id,
                Todos.owner_id == user_details.get("user_id")
            )
        ).delete()
        db.commit()
        return {"msg": "deleted"}

    except NoResultFound:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No record found"
        )

    except ValidateTokenError as e:
        raise e

    except Exception:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error occurred while deleting a todo"
        )
