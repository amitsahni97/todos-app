from fastapi import APIRouter, status
from typing import Optional
from fastapi import Depends, HTTPException, Path, Query
from sqlalchemy import and_
from sqlalchemy.exc import NoResultFound
from sqlalchemy.orm import Session
from exceptions import ValidateTokenError, NoRecordFound, InvalidCredentialsException
from models import Todos
from request_body import TodoRequestSchema
from utils import get_db, get_todo, validate_user_id_and_token

todo_router = APIRouter(
    tags=["Todos"]
)


@todo_router.post("/{user_id}/todos", status_code=status.HTTP_201_CREATED)
def save_todo(
        details: TodoRequestSchema,
        user_id: int = Path(gt=0),
        token: str = Query(),
        db: Session = Depends(get_db)
):
    try:
        user_details = validate_user_id_and_token(token, user_id)
        todos = Todos(**details.model_dump(), owner_id=user_details.get('user_id'))
        db.add(todos)
        db.commit()

        return {"message": "Todo created!"}

    except InvalidCredentialsException as exc:
        raise exc

    except ValidateTokenError as e:
        raise e

    except Exception:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred while saving details to db"
        )


@todo_router.patch("/{user_id}/todos/{todo_id}", status_code=status.HTTP_202_ACCEPTED)
def update_todo(
        token: str,
        user_id: int = Path(gt=0),
        todo_id: int = Path(gt=0),
        title: Optional[str] = Query(min_length=3),
        description: Optional[str] = Query(min_length=3),
        priority: Optional[int] = Query(default=1),
        complete: Optional[bool] = Query(default=False),
        db: Session = Depends(get_db)
):
    try:
        user_details = validate_user_id_and_token(token, user_id)
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
        if complete:
            result.complete = complete
        db.add(result)
        db.commit()

        return {"message": "Details updated"}

    except InvalidCredentialsException as exc:
        raise exc

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


@todo_router.get("{user_id}/todos/{todo_id}", status_code=status.HTTP_200_OK)
def get_particular_todo(
        token: str,
        user_id: int = Path(gt=0),
        todo_id: int = Path(gt=0),
        db: Session = Depends(get_db)
):
    try:
        user_details = validate_user_id_and_token(token, user_id)
        result = db.query(Todos).filter(
            and_(
                Todos.owner_id == user_details.get("user_id"),
                Todos.id == todo_id
            )
        ).all()
        return result

    except InvalidCredentialsException as exc:
        raise exc

    except ValidateTokenError as e:
        raise e

    except Exception:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail='An error occurred while fetching details'
        )


@todo_router.get("/{user_id}/todos", status_code=status.HTTP_200_OK)
def get_all_todos(
        token: str,
        user_id: int = Path(gt=0),
        db: Session = Depends(get_db)
):
    try:
        user_details = validate_user_id_and_token(token, user_id)
        result = db.query(Todos).filter(
                Todos.owner_id == user_details.get("user_id")
        ).all()
        return result

    except InvalidCredentialsException as exc:
        raise exc

    except ValidateTokenError as e:
        raise e

    except Exception:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail='An error occurred while fetching details'
        )


@todo_router.delete("/{user_id}/todos/{todo_id}", status_code=status.HTTP_200_OK)
def delete_particular_todo(
        token: str,
        user_id: int = Path(gt=0),
        todo_id: int = Path(gt=0),
        db: Session = Depends(get_db)
):
    try:
        user_details = validate_user_id_and_token(token, user_id)
        get_todo(db, Todos, todo_id, user_details.get("user_id"))
        db.query(Todos).filter(
            and_(
                Todos.id == todo_id,
                Todos.owner_id == user_details.get("user_id")
            )
        ).delete()
        db.commit()
        return {"message": "Todo deleted"}

    except InvalidCredentialsException as exc:
        raise exc

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


@todo_router.delete("/{user_id}/todos", status_code=status.HTTP_200_OK)
def delete_all_todo(
        token: str,
        user_id: int = Path(gt=0),
        db: Session = Depends(get_db)
):
    try:
        user_details = validate_user_id_and_token(token, user_id)
        result = db.query(Todos).filter(
                Todos.owner_id == user_details.get("user_id")
            )
        details = result.all()
        if len(details) == 0:
            raise NoRecordFound(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="No todo tasks found to delete"
            )
        result.delete()
        db.commit()
        return {"message": "Successfully deleted all tasks"}

    except InvalidCredentialsException as exc:
        raise exc

    except NoResultFound as exc:
        raise exc

    except ValidateTokenError as e:
        raise e

    except Exception:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error occurred while deleting all todos"
        )
