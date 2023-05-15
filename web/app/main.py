import uvicorn as uvicorn
from fastapi import FastAPI
from sqlalchemy import insert

from web.app.database import Base, engine
from web.app.models import UserInfo
from web.app.routers import auth, frames, users
from web.app.settings import APP_HOST, APP_PORT

app = FastAPI(title="FramesManagementApp")
app.include_router(auth.router)
app.include_router(frames.router)
app.include_router(users.router)

# password -> secret
admin_data = {
    "user_name": "johndoe",
    "first_name": "John",
    "second_name": "Doe",
    "email": "john_doe@example.com",
    # secret
    "hashed_password": "$2b$12$EixZaYVK1fsbw1ZfbX3OXePaWxn96p36WQoeG6Lruj3vjPGga31lW",  # noqa
    "disabled": False,
    "user_role": "admin",
}

# password -> user
test_user = {
    "user_name": "user",
    "first_name": "user",
    "second_name": "user",
    "email": "user@example.com",
    "hashed_password": "$2b$12$SMd9FB7BLW63FBI9vyQ7Cu9uhvrfJ2DkFWvrN9M1ZFFPfpCq5TswC",  # noqa
    "disabled": False,
    "user_role": "user",
}


@app.on_event("startup")
async def startup():
    # create db tables
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)
        await conn.run_sync(UserInfo.metadata.drop_all)
        await conn.run_sync(UserInfo.metadata.create_all)
        await conn.execute(insert(UserInfo).values(admin_data))
        await conn.execute(insert(UserInfo).values(test_user))


if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host=APP_HOST,
        port=int(APP_PORT),
        log_level="info",
        reload=True,
    )
