import os
import uuid

import pytest
import requests
from dotenv import load_dotenv

# Загружаем iпеременные из файла .env
load_dotenv()

BASE_URL = os.getenv("YOUGILE_BASE_URL", "https://ru.yougile.com")


@pytest.fixture(scope="session")
def base_url() -> str:
    return BASE_URL


@pytest.fixture(scope="session")
def api_token() -> str:
    """Если в .env уже есть ключ — используем его.
    Иначе запрашиваем новый по логину, паролю и companyId."""
    token = os.getenv("aDfAxK6D1HLKHI7gu7m19g749A9647d3HjTAvdq-MagiROFoWH7JH6LBbOFvM8z8"
                      )
    if token:
        return token

    login = os.getenv("YOUGILE_LOGIN")
    password = os.getenv("YOUGILE_PASSWORD")
    company_id = os.getenv("YOUGILE_COMPANY_ID")

    assert login and password and company_id, (
        "Заполни YOUGILE_LOGIN, YOUGILE_PASSWORD и YOUGILE_COMPANY_ID в .env "
        "или укажи готовый YOUGILE_TOKEN"
    )

    response = requests.post(
        f"{BASE_URL}/api-v2/auth/keys",
        json={"login": login, "password": password, "companyId": company_id},
    )
    response.raise_for_status()
    return response.json()["key"]


@pytest.fixture(scope="session")
def auth_headers(api_token: str) -> dict:
    return {"Authorization": f"Bearer {api_token}", "Content-Type": "application/json"}


@pytest.fixture(scope="session")
def yougile_client(base_url: str, auth_headers: dict):
    """Тонкий клиент над API: create_project / get_project / delete_project."""

    class YougileClient:
        def __init__(self):
            self.session = requests.Session()
            self.session.headers.update(auth_headers)
            self.created_ids = []

        def create_project(self, payload: dict, idempotency_key: str | None = None):
            headers = {}
            if idempotency_key is not None:
                headers["Key-Idempotency"] = idempotency_key
            return self.session.post(
                f"{base_url}/api-v2/projects", json=payload, headers=headers
            )

        def update_project(self, project_id: str, payload: dict):
            return self.session.put(f"{base_url}/api-v2/projects/{project_id}", json=payload)

        def get_project(self, project_id: str):
            return self.session.get(f"{base_url}/api-v2/projects/{project_id}")

        def delete_project(self, project_id: str):
            return self.session.delete(f"{base_url}/api-v2/projects/{project_id}")

        def register(self, project_id: str):
            self.created_ids.append(project_id)

    client = YougileClient()
    yield client

    # Уборка: удаляем всё, что создали за сессию
    for pid in client.created_ids:
        client.delete_project(pid)


@pytest.fixture
def project_payload() -> dict:
    return {"title": f"Autotest project {uuid.uuid4().hex[:8]}"}
