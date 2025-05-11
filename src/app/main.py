from fastapi import FastAPI

from app.api_v1.users.endpoints import router as users_router
from app.api_v1.books.endpoints import router as books_router
from app.api_v1.admin.endpoints import router as admin_router

app = FastAPI()

app.include_router(users_router)
app.include_router(books_router)
app.include_router(admin_router)