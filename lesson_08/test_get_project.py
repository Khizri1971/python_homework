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


def create_project(client, title=None):
    """Создаёт проект и регистрирует его на уборку. Возвращает (id, payload)."""
    payload = {"title": title or f"Autotest GET {uuid.uuid4().hex[:8]}"}
    resp = client.create_project(payload)
    assert resp.status_code == 201, f"Прекондиция: не удалось создать проект: {resp.text}"
    project_id = resp.json()["id"]
    client.register(project_id)
    return project_id, payload


# ---------- Позитивные сценарии ----------

class TestGetProjectPositive:

    def test_get_returns_200_and_id(self, yougile_client):
        """GET существующего проекта → 200, id совпадает с созданным."""
        project_id, _ = create_project(yougile_client)

        response = yougile_client.get_project(project_id)
        assert response.status_code == 200, response.text
        assert response.json()["id"] == project_id
        assert is_uuid(response.json()["id"])

    def test_get_returns_all_required_fields(self, yougile_client):
        """В ответе есть все обязательные поля: id, title, timestamp, deleted."""
        project_id, payload = create_project(yougile_client)

        response = yougile_client.get_project(project_id)
        assert response.status_code == 200, response.text

        body = response.json()
        assert "id" in body, "Нет поля id"
        assert "title" in body, "Нет поля title"
        assert "timestamp" in body, "Нет поля timestamp"
        assert "deleted" in body, "Нет поля deleted"

        assert body["id"] == project_id
        assert body["title"] == payload["title"]

    def test_get_timestamp_is_unix_ms(self, yougile_client):
        """timestamp — число, похоже на Unix-время в миллисекундах."""
        project_id, _ = create_project(yougile_client)

        response = yougile_client.get_project(project_id)
        body = response.json()
        ts = body["timestamp"]

        assert isinstance(ts, (int, float)), f"timestamp не число: {type(ts)}"
        # Разумный диапазон: не раньше 2000 года и не позже 2100
        assert 946684800000 < ts < 4102444800000, f"Подозрительный timestamp: {ts}"

    def test_get_deleted_false_for_active_project(self, yougile_client):
        """У только что созданного проекта deleted = false."""
        project_id, _ = create_project(yougile_client)

        response = yougile_client.get_project(project_id)
        assert response.json().get("deleted") is False

    def test_get_after_update_returns_new_title(self, yougile_client):
        """GET отражает изменения после PUT."""
        project_id, _ = create_project(yougile_client)
        new_title = f"Renamed {uuid.uuid4().hex[:6]}"

        upd = yougile_client.update_project(project_id, {"title": new_title})
        assert upd.status_code == 200, upd.text

        response = yougile_client.get_project(project_id)
        assert response.status_code == 200
        assert response.json()["title"] == new_title

    def test_get_deleted_project_shows_deleted_true(self, yougile_client):
        """После мягкого удаления GET возвращает объект с deleted = true."""
        project_id, _ = create_project(yougile_client)
        yougile_client.update_project(project_id, {"deleted": True})

        response = yougile_client.get_project(project_id)
        assert response.status_code == 200, response.text
        assert response.json().get("deleted") is True

    def test_get_with_title_unicode(self, yougile_client):
        """Юникод в названии сохраняется и возвращается без искажений."""
        title = f"Проект Тест №{uuid.uuid4().hex[:6]} — 🎯"
        project_id, payload = create_project(yougile_client, title=title)

        response = yougile_client.get_project(project_id)
        assert response.json()["title"] == title

    def test_get_twice_returns_consistent_data(self, yougile_client):
        """Два GET подряд возвращают одинаковые ключевые данные (стабильность)."""
        project_id, _ = create_project(yougile_client)

        first = yougile_client.get_project(project_id)
        second = yougile_client.get_project(project_id)

        assert first.status_code == second.status_code == 200
        f, s = first.json(), second.json()
        for key in ("id", "title", "deleted"):
            assert f.get(key) == s.get(key), (
                f"Поле '{key}' изменилось между двумя GET: {f.get(key)} != {s.get(key)}"
            )


# ---------- Негативные сценарии ----------

class TestGetProjectNegative:

    def test_get_without_auth(self, base_url):
        """GET без Authorization запрещён."""
        response = requests.get(
            f"{base_url}/api-v2/projects/4f6f0391-0f94-4d30-9b0e-99430a36d4fb"
        )
        assert response.status_code in (401, 403), response.text

    def test_get_with_invalid_token(self, base_url):
        """Невалидный токен не даёт доступ."""
        response = requests.get(
            f"{base_url}/api-v2/projects/4f6f0391-0f94-4d30-9b0e-99430a36d4fb",
            headers={"Authorization": "Bearer invalid-token-123"},
        )
        assert response.status_code in (401, 403), response.text

    def test_get_nonexistent_project_returns_404(self, yougile_client):
        """GET по несуществующему id → 404."""
        response = yougile_client.get_project(
            "00000000-0000-4000-8000-000000000000"
        )
        assert response.status_code == 404, response.text

    def test_get_with_malformed_id(self, yougile_client):
        """Невалидный формат id (не UUID) → 400 или 404, но не 5xx."""
        response = yougile_client.get_project("not-a-valid-uuid")
        assert response.status_code in (400, 404), response.text

    def test_get_random_uuid_repeatedly(self, yougile_client):
        """Несколько случайных несуществующих id — стабильно 404, без 5xx."""
        for _ in range(3):
            response = yougile_client.get_project(str(uuid.uuid4()))
            assert response.status_code == 404, response.text
