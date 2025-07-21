from fastapi.testclient import TestClient
from fastapi import status

from app.core.config import settings


def test_create_update_delete(
    client: TestClient, root_token_headers: dict[str, str]
) -> None:
    # create
    create_data = {
        "extension": "1234",
        "name": "test",
        "info": "just a test",
        "public": True,
    }

    r = client.post(
        f"{settings.API_V1_STR}/extension", json=create_data, headers=root_token_headers
    )

    assert r.status_code == status.HTTP_201_CREATED
    create_response = r.json()
    assert create_response["extension"] == create_data["extension"]
    assert create_response["name"] == create_data["name"]
    assert not "info" in create_response
    assert not "public" in create_response

    # update
    update_data = {"name": "foobar"}
    r = client.patch(
        f"{settings.API_V1_STR}/extension/{create_response["extension"]}",
        json=update_data,
        headers=root_token_headers,
    )
    assert r.status_code == status.HTTP_200_OK
    update_response = r.json()
    assert update_response["name"] == update_data["name"]

    # delete
    r = client.delete(
        f"{settings.API_V1_STR}/extension/{create_response["extension"]}",
        headers=root_token_headers,
    )

    assert r.status_code == status.HTTP_204_NO_CONTENT


def test_own(client: TestClient, root_token_headers: dict[str, str]) -> None:
    # first create an extension
    create_data = {
        "extension": "1234",
        "name": "test",
        "info": "just a test",
        "public": True,
    }

    r = client.post(
        f"{settings.API_V1_STR}/extension", json=create_data, headers=root_token_headers
    )
    create_response = r.json()

    # check if in own list

    r = client.get(f"{settings.API_V1_STR}/extension/own", headers=root_token_headers)
    assert r.status_code == status.HTTP_200_OK
    own: list[dict[str, any]] = r.json()

    assert any([create_data["extension"] == entry["extension"] for entry in own])
    entry = list(filter(lambda e: e["extension"] == create_data["extension"], own))
    assert len(entry) == 1
    entry = entry[0]

    assert len(entry["password"]) == settings.EXTENSION_PASSWORD_LENGTH
    assert len(entry["token"]) == settings.EXTENSION_TOKEN_LENGTH + len(
        settings.EXTENSION_TOKEN_PREFIX
    )

    # then delete it again
    r = client.delete(
        f"{settings.API_V1_STR}/extension/{create_response["extension"]}",
        headers=root_token_headers,
    )


def test_phonebook(client: TestClient, root_token_headers: dict[str, str]) -> None:
    # first create an extension
    create_data = {
        "extension": "1234",
        "name": "test",
        "info": "just a test",
        "public": True,
    }

    r = client.post(
        f"{settings.API_V1_STR}/extension", json=create_data, headers=root_token_headers
    )
    create_response = r.json()

    # check if in public phonebook

    r = client.get(f"{settings.API_V1_STR}/extension/phonebook")
    assert r.status_code == status.HTTP_200_OK
    phonebook = r.json()

    assert any([create_data["extension"] == entry["extension"] for entry in phonebook])

    # then delete it again
    r = client.delete(
        f"{settings.API_V1_STR}/extension/{create_response["extension"]}",
        headers=root_token_headers,
    )


def test_private_not_in_phonebook(
    client: TestClient, root_token_headers: dict[str, str]
) -> None:
    # first create an extension
    create_data = {
        "extension": "4321",
        "name": "test",
        "info": "just a test",
        "public": False,
    }

    r = client.post(
        f"{settings.API_V1_STR}/extension", json=create_data, headers=root_token_headers
    )
    create_response = r.json()

    # check if in own list

    r = client.get(f"{settings.API_V1_STR}/extension/own", headers=root_token_headers)
    assert r.status_code == status.HTTP_200_OK
    own = r.json()

    assert any([create_data["extension"] == entry["extension"] for entry in own])

    # check if in public phonebook

    r = client.get(f"{settings.API_V1_STR}/extension/phonebook")
    assert r.status_code == status.HTTP_200_OK
    phonebook = r.json()

    assert not any(
        [create_data["extension"] == entry["extension"] for entry in phonebook]
    )

    # check if in phonebook if logged in

    r = client.get(
        f"{settings.API_V1_STR}/extension/phonebook", headers=root_token_headers
    )
    assert r.status_code == status.HTTP_200_OK
    phonebook = r.json()

    assert any([create_data["extension"] == entry["extension"] for entry in phonebook])

    # then delete it again
    r = client.delete(
        f"{settings.API_V1_STR}/extension/{create_response["extension"]}",
        headers=root_token_headers,
    )
