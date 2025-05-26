from app.api_v1.admins.routers import router as admin_router
from app.api_v1.books.routers import router as books_router
from app.api_v1.users.routers import router as user_router

routers = [admin_router, books_router, user_router]
