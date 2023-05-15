import shutil
import uuid
from datetime import date, datetime
from tempfile import NamedTemporaryFile

from fastapi import APIRouter, Depends, File, HTTPException, Request, Security, UploadFile, status
from fastapi.params import Path, Query
from fastapi.responses import JSONResponse
from minio import Minio
from minio.deleteobjects import DeleteObject
from minio.error import S3Error
from sqlalchemy import exc
from sqlalchemy.ext.asyncio import AsyncSession

from web.app.crud.object import (
    create_object_info_in_db,
    delete_all_objects_from_db,
    delete_one_object_from_db,
    get_object_info_from_db,
)
from web.app.database import get_db
from web.app.models import InboxInfo
from web.app.role import Role
from web.app.schemas import GetResponce, Message, PostResponce, StaticUserDataInDB
from web.app.security import get_current_active_user
from web.app.settings import ACCESS_KEY, S3_ENDPOINT_URL, SECRET_KEY

router = APIRouter(
    tags=["Frames Management"],
    prefix="/frames",
)

client = Minio(
    endpoint=S3_ENDPOINT_URL,
    access_key=ACCESS_KEY,
    secret_key=SECRET_KEY,
    secure=False,
)


@router.post(
    "/",
    response_model=PostResponce,
    status_code=status.HTTP_201_CREATED,
    responses={
        400: {"model": Message},
        401: {"model": Message, "description": "Not authenticated"},
    },
    summary="Upload image(-s) and save info in database",
)
async def post_data(
    request: Request,
    files: list[UploadFile] = File(..., description="JPEG image file format"),
    session: AsyncSession = Depends(get_db),
    current_user: StaticUserDataInDB = Security(
        get_current_active_user,
        scopes=[Role.ADMIN["name"], Role.APP_USER["name"]],
    ),
):
    """."""
    user_bucket_name = str(current_user.user_name) + "-" + datetime.now().strftime("%Y-%m-%d")
    if client.bucket_exists(user_bucket_name):
        pass
    else:
        client.make_bucket(user_bucket_name)
    url = request.url_for("post_data")
    values = []
    res = {"user": current_user.user_name, "user_objects": list()}
    for file in files:
        if file.content_type != "image/jpeg":
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Ivalid data type or image format",
            )
        with NamedTemporaryFile(delete=False) as tmp:
            shutil.copyfileobj(file.file, tmp)
        new_file_name = str(uuid.uuid4()) + ".jpg"
        client.fput_object(
            bucket_name=user_bucket_name,
            object_name=new_file_name,
            file_path=tmp.name,
        )
        values.append(
            InboxInfo(
                url=url,
                filename=new_file_name,
                owner_id=current_user.user_name,
            )
        )
        res["user_objects"].append(
            {
                "file_name": file.filename,
                "object_name": new_file_name,
            }
        )
    await create_object_info_in_db(session, values)
    return res


@router.get(
    "/{bucket_name}",
    response_model=GetResponce,
    responses={
        404: {"model": Message},
        401: {"model": Message, "description": "Not authenticated"},
    },
    summary="Get images for a specified date",
)
async def get_data(
    bucket_name: date = Path(example="2022-07-01"),
    session: AsyncSession = Depends(get_db),
    current_user: StaticUserDataInDB = Security(
        get_current_active_user,
        scopes=[Role.ADMIN["name"], Role.APP_USER["name"]],
    ),
):
    """."""
    try:
        user_bucket_name = str(current_user.user_name) + "-" + str(bucket_name)
        objects = client.list_objects(user_bucket_name)
        res = {"objects": list()}
        for obj in objects:
            download_url = client.get_presigned_url("GET", user_bucket_name, obj.object_name)
            object_info = await get_object_info_from_db(session, obj.object_name)
            res["objects"].append(
                {
                    "object_name": obj.object_name,
                    "download_url": download_url,
                    "registration_date": object_info,
                }
            )
        return res
    except S3Error as err:
        if "NoSuchBucket" in str(err):
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="The specified bucket does not exist",
            )


@router.delete(
    "/{bucket_name}",
    status_code=status.HTTP_200_OK,
    responses={
        200: {"model": Message},
        401: {"model": Message, "description": "Not authenticated"},
        404: {"model": Message},
    },
    summary="Delete image(-s)",
)
async def delete_data(
    bucket_name: date = Path(example="2022-07-01"),
    object_name: str
    | None = Query(
        None,
        title="ObjectCreateInfo name",
        example="5c36e730-bd06-4ce8-be53-74da37a33375.jpg",
    ),
    session: AsyncSession = Depends(get_db),
    current_user: StaticUserDataInDB = Security(
        get_current_active_user,
        scopes=[Role.ADMIN["name"], Role.APP_USER["name"]],
    ),
):
    """."""
    try:
        user_bucket_name = str(current_user.user_name) + "-" + str(bucket_name)
        if object_name:
            await get_object_info_from_db(session, object_name)
            client.remove_object(user_bucket_name, object_name)
            await delete_one_object_from_db(session, object_name)
            return JSONResponse(
                status_code=status.HTTP_200_OK,
                content={"detail": "Specified image successfully deleted"},
            )
        delete_object_list = list(
            map(
                lambda x: DeleteObject(x.object_name),
                client.list_objects(str(user_bucket_name), recursive=True),
            )
        )
        errors = client.remove_objects(str(user_bucket_name), delete_object_list)
        for error in errors:
            print("Error occured when deleting object", error)
        client.remove_bucket(user_bucket_name)
        await delete_all_objects_from_db(session, str(bucket_name), current_user.user_name)
        return JSONResponse(
            status_code=status.HTTP_200_OK,
            content={"detail": "All images for specified date successfully deleted "},
        )
    except exc.NoResultFound:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Image not found")
    except S3Error as err:
        if "NoSuchBucket" in str(err):
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="The specified bucket does not exist",
            )
