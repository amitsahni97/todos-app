from fastapi import FastAPI
from router.todos import todo_router
from router.user import router
import models
from database import engine

app = FastAPI()

# This will create the database to appropriate location given in SQLALCHEMY_DATABASE_URL
models.Base.metadata.create_all(bind=engine)

app.include_router(router)
app.include_router(todo_router)
