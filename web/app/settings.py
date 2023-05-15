import os

from dotenv import find_dotenv, load_dotenv

load_dotenv(find_dotenv())

APP_HOST = os.environ.get("APP_HOST", default="0.0.0.0")
APP_PORT = os.environ.get("APP_PORT", default=8080)

POSTGRES_USER = os.environ.get("POSTGRES_USER", default="postgres")
POSTGRES_PASSWORD = os.environ.get("POSTGRES_PASSWORD", default="postgres")
POSTGRES_HOST = os.environ.get("POSTGRES_HOST", default="db")
POSTGRES_PORT = os.environ.get("POSTGRES_PORT", default=5432)
POSTGRES_DB = os.environ.get("POSTGRES_DB", default="postgres")

S3_ENDPOINT_URL = os.environ.get("S3_ENDPOINT_URL", default="localhost:9000")
ACCESS_KEY = os.environ.get("ACCESS_KEY", default="minioadmin")
SECRET_KEY = os.environ.get("SECRET_KEY", default="minioadmin")

AUTH_SECRET_KEY = os.environ.get(
    "AUTH_SECRET_KEY",
    default="3c14b0d4a002d2da5deac6a91a8dae6e1e3d1478f4863a0d1c65320c8174a2c0",
)
ALGORITHM = os.environ.get("ALGORITHM", default="HS256")
ACCESS_TOKEN_EXPIRE_MINUTES = os.environ.get("ACCESS_TOKEN_EXPIRE_MINUTES", default=30)
