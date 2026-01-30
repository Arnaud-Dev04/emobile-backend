from fastapi import APIRouter
from app.api.v1.endpoints import auth, users, login_google, products, orders, chat, lumicash, favorites, notifications, crypto

api_router = APIRouter()
api_router.include_router(auth.router, tags=["login"])
api_router.include_router(login_google.router, tags=["login"])
api_router.include_router(users.router, prefix="/users", tags=["users"])
api_router.include_router(products.router, prefix="/products", tags=["products"])
api_router.include_router(orders.router, prefix="/orders", tags=["orders"])
api_router.include_router(chat.router, prefix="/chat", tags=["chat"])
api_router.include_router(lumicash.router, tags=["lumicash"])
api_router.include_router(favorites.router, prefix="/favorites", tags=["favorites"])
api_router.include_router(notifications.router, prefix="/notifications", tags=["notifications"])
api_router.include_router(crypto.router, prefix="/crypto", tags=["crypto"])
