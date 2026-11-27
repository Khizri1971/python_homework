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


# ---------- Хелперы ----------

def create_project(client, title=None):
    """Создаёт проект и регистрирует его на уборку. Возвращает (id, payload)."""
    payload = {"title": title or f"Autotest {uuid.uuid4().hex[:8]}"}
    resp = client.create_project(payload)
    assert resp.status_code == 201, f"Прекондиция: не удалось создать проект: {resp.text}"
    project_id = resp.json()["id"]
    client.register(project_id)
    return project_id, payload


# ---------- Позитивные сценарии ----------

class TestUpdateProjectPositive:

    def test_update_title(self, yougile_client):
        """PUT с новым названием меняет название проекта."""
        project_id, _ = create_project(yougile_client)
        new_title = f"Updated {uuid.uuid4().hex[:8]}"

        response = yougile_client.update_project(project_id, {"title": new_title})
        assert response.status_code == 200, response.text

        body = response.json()
        assert body.get("id") == project_id, response.text

        # Проверяем эффект через GET
        get = yougile_client.get_project(project_id)
        assert get.status_code == 200
        assert get.json()["title"] == new_title, (
            f"Ожидали '{new_title}', получили '{get.json().get('title')}'"
        )

    def test_update_returns_same_id(self, yougile_client):
        """PUT не создаёт новый объект — id остаётся прежним."""
        project_id, _ = create_project(yougile_client)

        response = yougile_client.update_project(
            project_id, {"title": f"Same id check {uuid.uuid4().hex[:6]}"}
        )
        assert response.status_code == 200, response.text
        assert is_uuid(response.json()["id"])
        assert response.json()["id"] == project_id

    def test_partial_update_only_title(self, yougile_client):
        """PUT только с title меняет title, но не затирает прочие поля."""
        project_id, _ = create_project(yougile_client)

        before = yougile_client.get_project(project_id).json()

        response = yougile_client.update_project(
            project_id, {"title": f"Partial {uuid.uuid4().hex[:6]}"}
        )
        assert response.status_code == 200, response.text

        after = yougile_client.get_project(project_id)
        assert after.status_code == 200
        assert after.json().get("title") is not None  # проект жив, не удалён
        # Прочие ключевые поля не изменились (сравниваем то, что есть в обоих ответах)
        for key in ("deleted",):
            if key in before:
                assert after.json().get(key) == before[key], (
                    f"Поле '{key}' изменилось после частичного обновления"
                )

    def test_soft_delete_via_deleted_true(self, yougile_client):
        """PUT {"deleted": true} помечает проект удалённым."""
        project_id, _ = create_project(yougile_client)

        response = yougile_client.update_project(project_id, {"deleted": True})
        assert response.status_code == 200, response.text

        get = yougile_client.get_project(project_id)
        assert get.status_code == 200
        assert get.json().get("deleted") is True

    def test_idempotent_repeated_update(self, yougile_client):
        """Повторный PUT с тем же телом возвращает тот же id и 200."""
        project_id, _ = create_project(yougile_client)
        new_title = f"Repeat {uuid.uuid4().hex[:6]}"

        first = yougile_client.update_project(project_id, {"title": new_title})
        second = yougile_client.update_project(project_id, {"title": new_title})

        assert first.status_code == second.status_code == 200, (first.text, second.text)
        assert first.json()["id"] == second.json()["id"] == project_id


# ---------- Негативные сценарии ----------

class TestUpdateProjectNegative:

    def test_update_without_auth(self, base_url):
        """PUT без Authorization запрещён."""
        response = requests.put(
            f"{base_url}/api-v2/projects/4f6f0391-0f94-4d30-9b0e-99430a36d4fb",
            json={"title": "No auth"},
            headers={"Content-Type": "application/json"},
        )
        assert response.status_code in (401, 403), response.text

    def test_update_with_invalid_token(self, base_url):
        """Невалидный токен не даёт доступ."""
        response = requests.put(
            f"{base_url}/api-v2/projects/4f6f0391-0f94-4d30-9b0e-99430a36d4fb",
            json={"title": "Bad token"},
            headers={"Authorization": "Bearer invalid-token-123",
                     "Content-Type": "application/json"},
        )
        assert response.status_code in (401, 403), response.text

    def test_update_nonexistent_project(self, yougile_client):
        """PUT по несуществующему id → 404, а не 200/5xx."""
        response = yougile_client.update_project(
            "00000000-0000-4000-8000-000000000000", {"title": "Ghost"}
        )
        assert response.status_code == 404, response.text

    def test_update_deleted_project(self, yougile_client):
        """PUT по уже удалённому проекту — 404/400, не 5xx."""
        project_id, _ = create_project(yougile_client)
        yougile_client.update_project(project_id, {"deleted": True})

        response = yougile_client.update_project(project_id, {"title": "Revive"})
        assert response.status_code in (404, 400), response.text

    def test_update_with_invalid_title_type(self, yougile_client):
        """title не строкового типа → валидация (400/422), не 5xx."""
        project_id, _ = create_project(yougile_client)
        response = yougile_client.update_project(project_id, {"title": 12345})
        assert response.status_code in (400, 422), response.text

    def test_update_with_empty_body(self, yougile_client):
        """Пустое тело — сервер отвечает штатно, без 5xx."""
        project_id, _ = create_project(yougile_client)
        response = yougile_client.update_project(project_id, {})
        assert response.status_code in (200, 400, 422), response.text

    def test_update_with_invalid_users_format(self, yougile_client):
        """users не в формате объект → 400/422, не 5xx."""
        project_id, _ = create_project(yougile_client)
        response = yougile_client.update_project(
            project_id, {"title": "Bad users", "users": "not-an-object"}
        )
        assert response.status_code in (400, 422), response.text
