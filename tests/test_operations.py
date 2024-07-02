from enum import Enum

import requests
import pytest
from httpx import AsyncClient
from fastapi.testclient import TestClient
from pydantic import BaseModel

from src.main import app


@pytest.fixture
def url():
    return "http://127.0.0.1:8000"

def test_endpoint_returns_200(url):
    '''Проверка get-запроса'''
    response = requests.get(url)
    assert response.status_code == 200
    assert response.headers["content-type"] == "text/html; charset=utf-8"


client = TestClient(app)

# class Status(Enum):
#     success = "success"
#     error = "error"
#
#
# class TestStatus(BaseModel):
#     status = Status


def test_delete_none():
    response = client.post("/doc_delete/5")
    assert response.status_code == 200
    assert response.json() == {
        "status": "error",
        "data": None,
        "details": "Запись с таким id отсутствует в БД"
    }

def test_delete_success():
    response = client.post("/doc_delete/9")
    assert response.status_code == 200
    assert response.json() == {
                "status": "success",
                "data": "Изображение успешно удалено с жесткого диска вместе с записью из БД",
                "details": None,
            }
def test_delete_error():
    response = client.post("/doc_delete/6")
    assert response.status_code == 200
    assert response.json() == {
            "status": "error",
            "data": None,
            "details": "unknown error",
        }

# def test_no_signs():
#     with pytest.except:
#         length_circum(-10)
#     assert "Диаметр не может быть отрицательным!" == error.value.args[0]



if __name__ == '__main__':
    pytest.main()