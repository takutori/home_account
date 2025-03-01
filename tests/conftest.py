import pytest

from app import boot_app



@pytest.fixture
def client():
    with boot_app.test_client() as client:
        yield client