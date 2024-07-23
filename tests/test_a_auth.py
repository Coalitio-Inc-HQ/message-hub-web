from httpx import AsyncClient

from tests.conftest import TestUserData

from core import logger


class Test_A_Auth:
    """
    Приставка '.._A_..' необходима для очередности
    запуска тестов.

    'A' означает, что данный тест будет первым.
    'B' — вторым. И так далее.
    """

    async def test_endpoint_register_user(
            self,
            ac: AsyncClient,
            test_user_data: TestUserData
    ):
        response = await ac.post(
            "/auth/register",
            json={
                "name": "pytest",
                "email": test_user_data.data['email'],
                "password": test_user_data.data['password']
            }
        )
        assert response.status_code == 201
        test_user_data.data['id'] = response.json()['id']

    async def test_endpoint_login_user(
            self,
            ac: AsyncClient,
            test_user_data: TestUserData
    ):
        response = await ac.post(
            "/auth/jwt/login",
            data={
                "username": test_user_data.data['email'],
                "password": test_user_data.data['password']
            }
        )
        assert response.status_code == 200
        assert "access_token" in response.json()
        test_user_data.data['access_token'] = response.json()['access_token']
