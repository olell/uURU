from fastapi import Response
from fastapi.testclient import TestClient

from app.core.config import settings


def test_root_login(client: TestClient) -> None:
    login_data = {
        "username": settings.DEFAULT_ROOT_USER,
        "password": settings.DEFAULT_ROOT_PASSWORD,
    }

    r = client.post(f"{settings.API_V1_STR}/user/login", json=login_data)

    assert r.status_code == 200


def test_invalid_password(client: TestClient) -> None:
    login_data = {
        "username": "root",
        "password": settings.DEFAULT_ROOT_PASSWORD + "foobar",
    }

    r = client.post(f"{settings.API_V1_STR}/user/login", json=login_data)

    assert r.status_code == 400
    assert r.json().get("detail", None) == "Incorrect username or password"


def test_root_info(client: TestClient, root_token_headers: dict[str, str]) -> None:
    r = client.get(f"{settings.API_V1_STR}/user/", headers=root_token_headers)

    assert r.status_code == 200


def test_invalid_token(client: TestClient) -> None:
    r = client.get(f"{settings.API_V1_STR}/user/", headers={"x-auth-token": "invalid"})

    assert r.status_code == 403


def test_create_read_delete_user(
    client: TestClient, root_token_headers: dict[str, str]
) -> None:
    # create user first
    data = {
        "username": "foobar",
        "role": "user",
        "password": "1234567890",
    }

    r = client.post(
        f"{settings.API_V1_STR}/user/register", headers=root_token_headers, json=data
    )

    assert r.status_code == 201

    user_json = r.json()
    assert user_json["username"] == data["username"]
    assert user_json["role"] == data["role"]
    assert not "password" in user_json.keys()

    # get user info
    r = client.get(
        f"{settings.API_V1_STR}/user?user_id={user_json["id"]}",
        headers=root_token_headers,
    )

    assert r.status_code == 200
    info = r.json()

    assert info["username"] == data["username"]
    assert info["role"] == data["role"]
    assert not "password" in info.keys()

    # then delete it again
    # r = client.delete(
    #     f"{settings.API_V1_STR}/user/{info["id"]}", headers=root_token_headers
    # )

    # assert r.status_code == 204
