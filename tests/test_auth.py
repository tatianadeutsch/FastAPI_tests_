import pytest

from tests.conftest import client


def test_register():
    client.post("/upload_doc", json={file: UploadFile})