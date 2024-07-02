import os
import uuid
from sqlalchemy import select, delete

from fastapi import UploadFile
from sqlalchemy import insert, delete

# from conftest import client, session_test, test_db, override_get_async_session
import pytest
import io

from src.main import app
from src.models.models import Documents
from fastapi.testclient import TestClient

from tests.conftest import session_test

file_name = "testfile.jpg"
client = TestClient(app)

def test_upload_valid_file(test_db):
    """Тест на загрузку файла с допустимым расширением"""
    with open(file_name, "wb") as f:
        # f_name = "%s.%s" % (uuid.uuid4(), file_name.split("/")[-1])
        f.write(b'content')
        with session_test() as session:
            stmt = Documents(path= file_name)
            session.add(stmt)
            session.commit()
    with client:
        with open(file_name, "rb") as f:
            response = client.post(f"http://127.0.0.1:8000/upload_doc", files={"file": (file_name, f, "image/jpeg")})

        assert response.status_code == 201
        assert response.json() == {
                        "status": "success",
                        "data": "file is saved to folder",
                        "details": None,
                    }
    os.remove(file_name)
# f"documents/{f_name}"

# @pytest.mark.skip(reason="Этот тест пропускается, потом разберусь.")
# def test_upload_ok():
#     '''Все ОК. Файл загружается'''
#     with open(file_name, "rb") as image_file:
#         f_name = "%s.%s" % (uuid.uuid4(),file_name.split("/")[-1])
#         contents = image_file.read()
#         with open(f"documents/{f_name}", "wb") as f:
#             f.write(contents)
#         with session_test() as session:
#             stmt = Documents(path=f_name)
#             session.add(stmt)
#             session.commit()
#     response = client.post(f"http://127.0.0.1:8000/upload_doc", files={"file": (f"documents/{f_name}", f, "image/jpeg")})
#     assert response.status_code == 201
#     assert response.json() == {
#   "status": "success",
#   "data": "file is saved to folder",
#   "details": "null"
# }
#
# @pytest.mark.skip(reason="Этот тест пропускается, потом разберусь.")
# @pytest.mark.parametrize('первое_значение, второе_значение, результат', [(1, 2, 3)])
# def test_add(first_number, second_number, result):
#     assert first_number + second_number == result


# def test_upload_unknown_error():
#     '''Ошибка сервера'''
#     with open("/home/nepogoda/Downloads/Про работу.jpg", "rb") as image_file:
#         response = client.post("/upload_doc", files={"file": ("/home/nepogoda/Downloads/Про работу.jpg", image_file, "image/jpeg")})
#     assert response.status_code == 500
#     assert response.json() == {'data': None, 'details': 'unknown error', 'status': 'error'}
#
#
# def test_upload_non_image_file():
#     '''Формат файла не поддерживается'''
#     with open("/home/nepogoda/Documents/itm/PY-45.doc", "rb") as document_file:
#         response = client.post("/upload_doc", files={"file": ("/home/nepogoda/Documents/postgres.odt", document_file, "text/plain")})
#     assert response.status_code == 400
#     assert response.json() == {'data': None, 'details': 'file format is not supported.', 'status': 'error'}
#
#
# def test_add():
#     '''Добавление названия файла в БД'''
#     with session_test() as session:
#         stmt = Documents(path="/home/nepogoda/Downloads/Про работу.jpg")
#         session.add(stmt)
#         session.commit()
#
#
# def test_upload_file():
#     # file_content = b"Hello, world!"
#     # file = io.BytesIO(file_content)
#     file_name = "testfile.jpg"
#
#     response = client.post("/upload_doc", files={"file": file_name})
#
#     assert response.status_code == 201
#
#
# def test_none_delete(override_get_async_session):
#     '''Запись с таким ID в БД отсутствует'''
#     response = client.delete(f"http://127.0.0.1:8000/doc_delete/1")
#     assert response.status_code == 404
#     assert response.json() == {
#                 "status": "error",
#                 "data": None,
#                 "details": "Запись с таким id отсутствует в БД",
#             }
# #
def test_delete():
    '''Удаление записи из БД и с жестого диска'''

    with session_test() as session:
        query = select(Documents.path).filter(Documents.id == 1)
        result = session.scalar(query)
        path = f"documents/{result}"
        os.remove(path)
        stmt = delete(Documents).filter(Documents.id == 1)
        session.execute(stmt)
        session.commit()
    response = client.delete(f"http://127.0.0.1:8000/doc_delete/1")

    assert response.status_code == 204
    assert response.json() == {
                "status": "success",
                "data": "Изображение успешно удалено с жесткого диска вместе с записью из БД",
                "details": None,
            }



# pytest -s -vv tests/test_register.py
# pytest -s -vv tests/test_register.py --alluredir=allureress
# allure serve allureress
