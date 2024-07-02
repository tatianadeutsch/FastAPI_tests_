
from starlette.testclient import TestClient

from src.main import app
from src.models.models import Documents
# from fastapi.testclient import TestClient

from tests.conftest import session_test

file_name = "testfile.jpg"
doc_file = "doctest.txt"
client = TestClient(app)

# @pytest.mark.skip
def test_upload_valid_file(test_db):
    """Тест на загрузку файла с допустимым расширением"""
    with client:
        with open(f"documents/{file_name}", "rb") as f:
            # with session_test() as session:
            #     stmt = Documents(path=file_name)
            #     session.add(stmt)
            #     session.commit()
            response = client.post(f"http://127.0.0.1:8000/upload_doc", files={"file": (file_name, f, "image/jpeg")})

        assert response.status_code == 201
        assert response.json() == {
                        "status": "success",
                        "data": "file is saved to folder",
                        "details": None,
                    }
    # os.remove(file_name)

def test_upload_invalid_file(test_db, session_db):
    """Формат не поддерживается"""

    with open(f"documents/{doc_file}", "wb") as f:
        f.write(b"test document content")
    with client:
        with open(f"documents/{doc_file}", "rb") as f:
            response = client.post(f"http://127.0.0.1:8000/upload_doc", files={"file": (doc_file, "text/plain")})

        assert response.status_code == 400
        assert response.json() == {'status': 'error',
                                   'data': None,
                                   'details': 'file format is not supported.'}



def test_delete(test_db, session_db, client):
    '''Удаление записи из БД и с жестого диска'''


    # Добавляем тестовый файл в базу данных
    test_file = Documents(path="test_file.jpg")
    session_db.add(test_file)
    session_db.commit()


    # Удаляем файл через API
    with client:
        response = client.delete(f"http://127.0.0.1:8000/delete_doc/172")
        print(response.json())
    assert response.status_code == 200

    # # Проверяем, что файл был удален
    # deleted_file = session_db.query(Documents.path).filter(Documents.id == {test_file.id}).first()
    # assert deleted_file is None
