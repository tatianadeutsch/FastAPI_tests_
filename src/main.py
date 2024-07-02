
import os
import uuid

import aioredis
import uvicorn
from fastapi import FastAPI, UploadFile, HTTPException
from fastapi_cache import FastAPICache
from fastapi_cache.backends.redis import RedisBackend
from sqlalchemy import select, delete
from starlette.responses import FileResponse, JSONResponse
# from fastapi.responses import FileResponse

from src.database import async_session, session_
from src.celery_app import *
from src.config import REDIS_HOST, REDIS_PORT
from src.models.models import Documents, Documents_text

# Dependency для получения сессии базы данных
def get_db():
    as_session = async_session()
    try:
        yield as_session
    finally:
        as_session.close()

app = FastAPI(title="MY_FastAPI")



@app.get("/", tags=["Приветствие"])
def root_get():
    return FileResponse("src/public/index.html")



@app.post("/upload_doc", tags=["Загрузка файла, добавление записи в БД"])
async def upload_doc(file: UploadFile) -> JSONResponse:
    """
    :description: Сохранение файла на жесткий диск, добавление записи в БД
    :param file: UploadFile
    :return: Сообщение о загрузке файла
    """
    try:
        if file.content_type.split("/")[0] == "image":
            old_name = file.filename
            filename = "%s.%s" % (uuid.uuid4(), old_name)
            # filename = file.filename
            contents = await file.read()
            with open(f"documents/{filename}", "wb") as name_file:
                name_file.write(contents)
                
                # Сохранение названия файла в БД
            async with async_session() as session:
                doc = Documents(path=filename)
                session.add(doc)
                await session.commit()
            return JSONResponse(content={
                "status": "success",
                "data": f"file is saved to folder",
                "details": None,
            }, status_code=201)
        return JSONResponse(content={
            "status": "error",
            "data": None,
            "details": "file format is not supported.",
        }, status_code=400)
    except Exception as e:
        print(e)
        return JSONResponse(content={
            "status": "error",
            "data": None,
            "details": "unknown error",
        }, status_code=500)



@app.delete("/delete_doc/{doc_id}", tags=["Удаление изображения с диска и из БД"])
def delete_doc(doc_id: int) -> JSONResponse:
    """
    :description: Удаление файла с жесткого диска, удаление записи из БД
    :doc_id: id удаляемого файла
    :return: Сообщение об удалении файла
    """
    try:
        with session_() as session:
            query = select(Documents.path).filter(Documents.id == doc_id)
            result = session.scalar(query)
            if result is None:
                return JSONResponse(content={
                    "status": "error",
                    "data": None,
                    "details": "Запись с таким id отсутствует в БД",
                }, status_code=404)

            path = f"documents/{result}"
            os.remove(path)
            stmt = delete(Documents).filter(Documents.id == doc_id)
            session.execute(stmt)
            session.commit()
            return JSONResponse(content={
                "status": "success",
                "data": "Изображение успешно удалено с жесткого диска вместе с записью из БД",
                "details": None,
            }, status_code=200)
    except Exception as e:
        return JSONResponse(content= {
            "status": "error",
            "data": None,
            "details": "unknown error",
        }, status_code=500)


@app.post("/doc_analyse", tags=["Распознавание текста, его добавление в БД"])
async def doc_analyse(doc_id: int) -> dict:
    """
    :description: Распознавание текста с картинки, добавление текста в БД
    :param doc_id: id файла из БД
    :return: помещает распознанные текст в БД
    """
    # redis = aioredis.from_url(
    #     f"redis://{REDIS_HOST}:{REDIS_PORT}", encoding="utf-8", decode_responses=True
    # )
    # FastAPICache.init(RedisBackend(redis), prefix="fastapi-cache")
    try:
        with session_() as session:
            query = select(Documents.path).filter(Documents.id == doc_id)
            result = session.scalar(query)
            if result is None:
                return {
                    "status": "error",
                    "data": None,
                    "details": "Запись с таким id отсутствует в БД",
                }
            path = f"documents/{result}"
            scan.delay(path, doc_id)
            # scan.delay(os.path.join(app_dir, "documents", result), doc_id)
            return {
                "status": "success",
                "data": f"Распознанный текст {result} успешно добавлен в БД",
                "details": None,
            }


    except:
        return {
            "status": "error",
            "data": None,
            "details": "unknown error",
        }


@app.get("/get_text/{doc_id}", tags=["Вывод распознанного текста из БД"])
async def get_text(doc_id: int) -> dict:
    """
    :description: API принимает id документа и возвращает распознанный текст
    :param doc_id: id из базы данных
    :return: вывод распознанного текста
    """
    try:
        with session_() as session:
            query = select(Documents_text.text).filter(Documents_text.id_doc == doc_id)
            res = session.scalar(query)
            if res is None:
                return {
                    "status": "error",
                    "data": None,
                    "details": "Запись с таким id отсутствует в БД",
                }

            return {
                "status": "success",
                "data": f"{res}",
                "details": None,
            }

    except Exception:
        raise HTTPException(
            status_code=500,
            detail={
                "status": "error",
                "data": None,
                "details": "Неизвестная ошибка",
            },
        )


if __name__ == "__main__":
    uvicorn.run("src.main:app", host="127.0.0.1", reload=True)

# 1. Сначала запускаем селери
# 2. Потом фастапи
# 3. В докере не получается запускать селери