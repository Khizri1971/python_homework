import uuid

import pytest
import requests


def is_uuid(value: object) -> bool:
    if not isinstance(value, str):
        return False
    try:
        uuid.UUID(value)
        return True
    except ValueError:
        return False


# ---------- Позитивные сценарии ----------

class TestCreateProjectPositive:

    def test_create_project_minimal_payload(self, yougile_client, project_payload):
        """Проект создаётся только с названием, ответ 201 + UUID в id."""
        response = yougile_client.create_project(project_payload)
        assert response.status_code == 201, response.text

        body = response.json()
        assert "id" in body, f"В ответе нет id: {body}"
        assert is_uuid(body["id"]), f"id не является UUID: {body['id']}"

        yougile_client.register(body["id"])

    def test_created_project_reachable_via_get(self, yougile_client, project_payload):
        """Созданный проект реально существует — проверяем через GET."""
        create = yougile_client.create_project(project_payload)
        assert create.status_code == 201
        project_id = create.json()["id"]
        yougile_client.register(project_id)

        get = yougile_client.get_project(project_id)
        assert get.status_code == 200
        assert get.json()["title"] == project_payload["title"]

    def test_create_project_with_title_max_length(self, yougile_client):
        """Название на границе допустимой длины — либо создаётся, либо 400/422."""
        payload = {"title": "П" * 249}
        response = yougile_client.create_project(payload)
        assert response.status_code in (201, 400, 422), response.text
        if response.status_code == 201:
            yougile_client.register(response.json()["id"])

    def test_idempotency_key_returns_same_project(
            self, yougile_client, project_payload
    ):
        """Повторный запрос с тем же ключом возвращает тот же проект."""
        key = str(uuid.uuid4())

        first = yougile_client.create_project(project_payload, idempotency_key=key)
        assert first.status_code == 201, first.text
        first_id = first.json()["id"]
        yougile_client.register(first_id)

        second = yougile_client.create_project(project_payload, idempotency_key=key)
        assert second.status_code in (200, 201), second.text
        assert second.json()["id"] == first_id, (
            "Один и тот же ключ вернул разные проекты"
        )

    def test_idempotency_new_key_creates_new_project(
            self, yougile_client, project_payload
    ):
        """Разные ключи → разные проекты."""
        p1 = yougile_client.create_project(project_payload, idempotency_key=str(uuid.uuid4()))
        p2 = yougile_client.create_project(project_payload, idempotency_key=str(uuid.uuid4()))
        assert p1.status_code == p2.status_code == 201
        assert p1.json()["id"] != p2.json()["id"]
        yougile_client.register(p1.json()["id"])
        yougile_client.register(p2.json()["id"])

    def test_create_project_with_nonexistent_user_is_rejected(self, yougile_client):
        """Несуществующий пользователь не должен молча проходить."""
        payload = {
            "title": f"Project with users {uuid.uuid4().hex[:8]}",
            "users": {"4902b994-b806-4af4-acec-018ea5ea6468": "worker"},
        }
        response = yougile_client.create_project(payload)
        assert response.status_code in (400, 404), response.text
        if response.status_code == 201:  # если UUID вдруг реальный — не забыть уборку
            yougile_client.register(response.json()["id"])


# ---------- Негативные сценарии ----------

class TestCreateProjectNegative:

    def test_create_without_auth(self, base_url, project_payload):
        """Без заголовка Authorization создание запрещено."""
        response = requests.post(
            f"{base_url}/api-v2/projects",
            json=project_payload,
            headers={"Content-Type": "application/json"},
        )
        assert response.status_code in (401, 403), response.text

    def test_create_with_invalid_token(self, base_url, project_payload):
        """Невалидный токен не должен давать доступ."""
        response = requests.post(
            f"{base_url}/api-v2/projects",
            json=project_payload,
            headers={
                "Authorization": "Bearer invalid-token-123",
                "Content-Type": "application/json",
            },
        )
        assert response.status_code in (401, 403), response.text

    def test_create_without_title(self, yougile_client):
        """Отсутствует обязательное поле title → 400, а не 201."""
        response = yougile_client.create_project({})
        assert response.status_code == 400, response.text

    def test_create_with_empty_title(self, yougile_client):
        """Пустое название — невалидный запрос."""
        response = yougile_client.create_project({"title": ""})
        assert response.status_code in (400, 422), response.text

    def test_create_with_non_string_title(self, yougile_client):
        """title не строкового типа — сервер отвечает валидацией, не 5xx."""
        response = yougile_client.create_project({"title": 12345})
        assert response.status_code in (400, 422), response.text

    def test_create_with_invalid_users_format(self, yougile_client):
        """users не в формате объект → строка: сервер не должен падать."""
        response = yougile_client.create_project(
            {"title": f"Bad users {uuid.uuid4().hex[:6]}", "users": "not-an-object"}
        )
        assert response.status_code in (400, 422), response.text
