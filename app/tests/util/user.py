from fastapi.testclient import TestClient

from app.core.config import settings


def user_authentication_headers(
    client: TestClient, username: str, password: str
) -> dict[str, str]:
    data = {"username": username, "password": password}

    r = client.post(f"{settings.API_V1_STR}/user/login", json=data)
    response = r.json()
    auth_token = response["token"]
    headers = {"x-auth-token": auth_token}
    return headers
