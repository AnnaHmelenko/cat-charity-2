from fastapi import FastAPI

from app.api.routes import charity_project, donation, user, yandex_api
from app.core.config import settings
from app.core.init_db import create_first_superuser

app = FastAPI(
    title=settings.app_title,
    description=settings.app_description,
)

app.include_router(
    user.router,
)
app.include_router(
    charity_project.router,
    prefix="/charity_project",
    tags=["Проекты"],
)
app.include_router(
    donation.router,
    prefix="/donation",
    tags=["Пожертвования"],
)
app.include_router(
    yandex_api.router,
    prefix="/yandex",
    tags=["Yandex Disk"],
)


@app.on_event("startup")
async def startup():
    await create_first_superuser()
