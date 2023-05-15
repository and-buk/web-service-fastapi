from fastapi import APIRouter, Depends, HTTPException, Security
from fastapi.encoders import jsonable_encoder
from sqlalchemy.ext.asyncio import AsyncSession
from starlette import status

from web.app.crud.user import create_user_info_in_db, get_user_by_email, get_user_by_username, update_user_info
from web.app.database import get_db
from web.app.role import Role
from web.app.schemas import CreateUserRequest, CreateUserResponse, Message, MutableUserDataInDB, StaticUserDataInDB
from web.app.security import get_current_active_user, get_password_hash

router = APIRouter(tags=["Users Management"], prefix="/users")


@router.post(
    "/",
    response_model=CreateUserResponse,
    status_code=status.HTTP_201_CREATED,
    responses={400: {"model": Message}, 409: {"model": Message}},
    summary="Create user",
)
async def create(user: CreateUserRequest, session: AsyncSession = Depends(get_db)):
    username_in_db = await get_user_by_username(session, user.user_name)
    email_in_db = await get_user_by_email(session, user.email)
    if username_in_db is not None:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"UserInfo with username '{user.user_name}' already exists",
        )
    if email_in_db is not None:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"UserInfo with email '{user.email}' already exists",
        )
    hashed_password = await get_password_hash(user.password)
    responce_data = await create_user_info_in_db(
        session,
        user_name=user.user_name,
        first_name=user.first_name,
        second_name=user.second_name,
        email=user.email,
        password=hashed_password,
    )
    return {
        "user_name": responce_data[0],
        "id": responce_data[1],
        "created_at": responce_data[2],
    }


@router.patch(
    "/{user_name}",
    response_model=MutableUserDataInDB,
    status_code=status.HTTP_200_OK,
    responses={
        400: {"model": Message},
        401: {"model": Message, "description": "Not authenticated"},
        403: {"model": Message, "description": "Not enough permissions"},
        404: {"model": Message},
    },
    summary="Update user data",
)
async def update(
    user_name: str,
    user_data: MutableUserDataInDB,
    session: AsyncSession = Depends(get_db),
    current_user: MutableUserDataInDB = Security(get_current_active_user, scopes=[Role.ADMIN["name"]]),
):
    username_in_db = await get_user_by_username(session, user_name)
    if username_in_db is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"UserInfo with username '{user_name}' not found",
        )
    update_data = user_data.dict(exclude_unset=True)
    data_for_db = jsonable_encoder(update_data)
    responce_data = await update_user_info(user_name, session, **data_for_db)
    return responce_data


@router.get(
    "/{user_name}",
    response_model=StaticUserDataInDB,
    status_code=status.HTTP_200_OK,
    responses={
        404: {"model": Message},
        401: {"model": Message, "description": "Not authenticated"},
        403: {"model": Message, "description": "Not enough permissions"},
    },
    summary="Get user data",
)
async def get_data(
    user_name: str,
    session: AsyncSession = Depends(get_db),
    current_user: MutableUserDataInDB = Security(get_current_active_user, scopes=[Role.ADMIN["name"]]),
):
    responce_data = await get_user_by_username(session, user_name)
    if responce_data is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"UserInfo with username '{user_name}' not found",
        )
    return jsonable_encoder(responce_data)
