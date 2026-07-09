from fastapi import APIRouter, HTTPException, status

from app.core.user import auth_backend, fastapi_users
from app.schemas.user import UserCreate, UserRead, UserUpdate

router = APIRouter()

router.include_router(
    fastapi_users.get_auth_router(auth_backend),
    prefix="/auth/jwt",
    tags=["auth"],
)
router.include_router(
    fastapi_users.get_register_router(UserRead, UserCreate),
    prefix="/auth",
    tags=["auth"],
)

users_router = fastapi_users.get_users_router(UserRead, UserUpdate)


@users_router.delete(
    "/{id}",
    tags=["users"],
    deprecated=True,
    description="Удаление пользователей запрещено. Деактивируйте их.",
)
def delete_user(id: str):
    raise HTTPException(
        status_code=status.HTTP_405_METHOD_NOT_ALLOWED,
        detail="Удаление пользователей запрещено!",
    )


router.include_router(users_router, prefix="/users", tags=["users"])
