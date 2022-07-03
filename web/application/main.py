import platform
import shutil
import uuid
from datetime import datetime, date
from tempfile import NamedTemporaryFile
from typing import List

import databases
import sqlalchemy
import uvicorn as uvicorn
from fastapi import FastAPI, UploadFile, Request, File
from fastapi.params import Path, Query
from fastapi.responses import JSONResponse
from minio import Minio
from minio.deleteobjects import DeleteObject
from minio.error import S3Error
from pydantic import BaseModel, HttpUrl

client = Minio(
    "127.0.0.1:9000",
    access_key="minioadmin",
    secret_key="minioadmin",
    secure=False,
)

DATABASE_URL = "postgresql://postgres:mirniy@127.0.0.1:5432/postgres"

database = databases.Database(DATABASE_URL)

metadata = sqlalchemy.MetaData()

inbox_table = sqlalchemy.Table(
    "inbox",
    metadata,
    sqlalchemy.Column("id", sqlalchemy.Integer, primary_key=True, index=True),
    sqlalchemy.Column("url", sqlalchemy.String),
    sqlalchemy.Column("filename", sqlalchemy.String, unique=True),
    sqlalchemy.Column("registration_datetime", sqlalchemy.TIMESTAMP),
)

engine = sqlalchemy.create_engine(DATABASE_URL)

metadata.create_all(engine)


class ObjectCreateInfo(BaseModel):
    object_name: str
    created_at: datetime


class PostResponce(BaseModel):
    objects: List[ObjectCreateInfo]


class ObjectGetInfo(BaseModel):
    object_name: str
    download_url: HttpUrl
    registration_date: datetime


class GetResponce(BaseModel):
    objects: List[ObjectGetInfo]


class Message(BaseModel):
    message: str


app = FastAPI()


@app.on_event("startup")
async def startup():
    await database.connect()


@app.on_event("shutdown")
async def shutdown():
    await database.disconnect()


@app.post(
    "/frames/",
    response_model=PostResponce,
    status_code=201,
    responses={400: {"model": Message}},
    summary="Upload image(-s) and save info in database",
)
async def post_data(
    request: Request,
    files: list[UploadFile] = File(..., description="JPEG image file format"),
):
    """."""
    if client.bucket_exists(datetime.now().strftime("%Y-%m-%d")):
        pass
    else:
        client.make_bucket(datetime.now().strftime("%Y-%m-%d"))
    url = request.url_for("post_data")
    values = []
    res = {"objects": list()}
    sys_type = platform.system()
    if sys_type == "Windows":
        temporary_delete = False
    else:
        temporary_delete = True

    for file in files:
        print(file)
        if file.content_type != "image/jpeg":
            return JSONResponse(
                status_code=400,
                content={"message": "Ivalid data type or image format"},
            )
        with NamedTemporaryFile(delete=temporary_delete) as tmp:
            shutil.copyfileobj(file.file, tmp)
        new_file_name = str(uuid.uuid4()) + ".jpg"
        created_at = datetime.now()
        client.fput_object(
            bucket_name=datetime.now().strftime("%Y-%m-%d"),
            object_name=new_file_name,
            file_path=tmp.name,
        )
        values.append(
            {
                "url": url,
                "filename": new_file_name,
                "registration_datetime": created_at,
            }
        )
        res["objects"].append(
            {"object_name": new_file_name, "created_at": created_at}
        )
    query = inbox_table.insert()
    await database.execute_many(query, values)
    return res


@app.get(
    "/frames/{bucket_name}",
    response_model=GetResponce,
    responses={404: {"model": Message}},
    summary="Get images for a specified date",
)
async def get_data(bucket_name: date = Path(example="2022-07-01")):
    """."""
    try:
        objects = client.list_objects(str(bucket_name))
        res = {"objects": list()}
        for obj in objects:
            download_url = client.presigned_get_object(
                str(bucket_name), obj.object_name
            )
            query = (
                f"SELECT filename, registration_datetime "
                f"FROM inbox WHERE filename = '{obj.object_name}'"
            )
            db_row = await database.fetch_one(query=query)
            res["objects"].append(
                {
                    "object_name": db_row[0],
                    "download_url": download_url,
                    "registration_date": db_row[1],
                }
            )
        return res
    except S3Error as exc:
        if "NoSuchBucket" in str(exc):
            return JSONResponse(
                status_code=404,
                content={"message": "The specified bucket does not exist"},
            )


@app.delete(
    "/frames/{bucket_name}",
    status_code=200,
    responses={404: {"model": Message}, 200: {"model": Message}},
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
):
    """."""
    try:
        bucket_name = str(bucket_name)
        if object_name:
            check_id_query = inbox_table.select().where(
                inbox_table.c.filename == object_name
            )
            if not await database.fetch_one(query=check_id_query):
                return JSONResponse(
                    status_code=404, content={"message": "Image not found"}
                )
            client.remove_object(bucket_name, object_name)
            del_item_query = inbox_table.delete().where(
                inbox_table.c.filename == object_name
            )
            await database.execute(del_item_query)
            return JSONResponse(
                status_code=200,
                content={"message": "Specified image successfully deleted"},
            )
        delete_object_list = list(
            map(
                lambda x: DeleteObject(x.object_name),
                client.list_objects(str(bucket_name), recursive=True),
            )
        )
        print(delete_object_list)
        errors = client.remove_objects(str(bucket_name), delete_object_list)
        for error in errors:
            print("error occured " "when deleting object", error)
        client.remove_bucket(bucket_name)
        del_group_query = (
            f"DELETE FROM inbox "
            f"WHERE DATE(registration_datetime) = '{bucket_name}'"
        )
        await database.execute(del_group_query)
        return JSONResponse(
            status_code=200,
            content={
                "message": "All images for "
                "specified date successfully deleted "
            },
        )
    except S3Error as exc:
        if "NoSuchBucket" in str(exc):
            return JSONResponse(
                status_code=404,
                content={"message": "The specified bucket does not exist"},
            )


if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="127.0.0.1",
        port=8000,
        log_level="info",
        reload=True,
    )
