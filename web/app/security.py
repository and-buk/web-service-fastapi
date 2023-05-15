from datetime import datetime, timedelta

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, SecurityScopes
from jose import JWTError, jwt
from passlib.context import CryptContext
from pydantic import ValidationError
from sqlalchemy.ext.asyncio import AsyncSession

from web.app.crud.user import get_user_by_username
from web.app.database import get_db
from web.app.role import Role
from web.app.schemas import TokenData, UserPass
from web.app.settings import ALGORITHM, AUTH_SECRET_KEY

pwd_context = CryptContext(
    schemes=["bcrypt"],
    deprecated="auto",
    # bcrypt__salt_size=16
)
oauth2_scheme = OAuth2PasswordBearer(
    tokenUrl="token",
    scopes={
        Role.APP_USER["name"]: Role.APP_USER["description"],
        Role.ADMIN["name"]: Role.ADMIN["description"],
    },
)


async def verify_password(plain_password, hashed_password):
    """Сравниваем хэш-коды объектов (паролей)."""
    return pwd_context.verify(plain_password, hashed_password)


async def get_password_hash(password) -> str:
    """Преобразуем пароль в битовую строку фиксированной длины."""
    return pwd_context.hash(password)


async def authenticate_user(user_name: str, password: str, session) -> UserPass | bool:
    """Аутентификация пользователя."""
    user = await get_user_by_username(session, user_name=user_name)
    if not user:
        return False
    if not await verify_password(password, user.hashed_password):
        return False
    return user


async def create_access_token(data: dict, expires_delta: timedelta | None = None) -> str:
    """Создаём JSON Web Token."""
    to_encode: dict = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, AUTH_SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


async def get_current_user(
    security_scopes: SecurityScopes,
    token: str = Depends(oauth2_scheme),
    session: AsyncSession = Depends(get_db),
) -> UserPass:
    if security_scopes.scopes:
        authenticate_value = f'Bearer scope="{security_scopes.scope_str}"'
    else:
        authenticate_value = "Bearer"
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": authenticate_value},
    )
    try:
        payload = jwt.decode(token, AUTH_SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
        token_data = TokenData(username=username, role=payload.get("role"))
    except (JWTError, ValidationError):
        raise credentials_exception
    user = await get_user_by_username(session, user_name=token_data.username)
    if user is None:
        raise credentials_exception
    if token_data.role not in security_scopes.scopes:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions",
            headers={"WWW-Authenticate": authenticate_value},
        )
    return user


async def get_current_active_user(
    current_user: UserPass = Depends(get_current_user),
) -> UserPass:
    if current_user.disabled:
        raise HTTPException(status_code=400, detail="Inactive user")
    return current_user
