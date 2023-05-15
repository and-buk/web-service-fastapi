from datetime import timedelta

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession

from web.app.database import get_db
from web.app.schemas import Token, UserPass
from web.app.security import authenticate_user, create_access_token
from web.app.settings import ACCESS_TOKEN_EXPIRE_MINUTES

router = APIRouter(tags=["Authentication"])


@router.post("/token", response_model=Token, summary="Authenticate and get access token")
async def login_for_access_token(
    form_data: OAuth2PasswordRequestForm = Depends(),
    session: AsyncSession = Depends(get_db),
):
    # Аутентификация пользователя
    user: UserPass | bool = await authenticate_user(form_data.username, form_data.password, session)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect user_name or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(minutes=int(ACCESS_TOKEN_EXPIRE_MINUTES))
    access_token = await create_access_token(
        data={"sub": user.user_name, "role": user.user_role},
        expires_delta=access_token_expires,
    )
    return {"access_token": access_token, "token_type": "bearer"}
