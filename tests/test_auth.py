import string
from random import choice

from httpx import AsyncClient


def _get_random_email(size: int = 6, chars: str = string.ascii_uppercase + string.digits):
    return ''.join(choice(chars) for _ in range(size))


class Test_A_Auth:
    """
    Приставка '.._A_..' необходима для очередности
    запуска тестов.

    'A' означает, что данный тест будет первым.
    'B' — вторым. И так далее.
    """
    TEST_EMAIL: str = f'{_get_random_email()}@pytest.pytest'
    TEST_PASSWORD: str = "Aa1234567890!"

    async def test_endpoint_register_user(self, ac: AsyncClient):
        response = await ac.post(
            "/auth/register",
            json={
                "name": "pytest",
                "email": self.TEST_EMAIL,
                "password": self.TEST_PASSWORD
            }
        )
        assert response.status_code == 201

    async def test_endpoint_login_user(self, ac: AsyncClient):
        response = await ac.post(
            "/auth/jwt/login",
            data={
                "username": self.TEST_EMAIL,
                "password": self.TEST_PASSWORD
            }
        )
        assert response.status_code == 200
        assert response.json()["access_token"]
