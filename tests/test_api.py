import pytest
from fastapi.testclient import TestClient
from sqlalchemy import select

from app.main import app
from app.database.session import SessionLocal
from app.models import Category, Task, User


@pytest.fixture(scope="module")
def client():
    with TestClient(app) as c:
        yield c


@pytest.fixture(scope="module")
def auth_headers(client):
    email = "suite_test@example.com"
    username = "suitetest"
    password = "TestPassword123!"

    client.post(
        "/api/v1/auth/register",
        json={"email": email, "username": username, "password": password},
    )
    res = client.post(
        "/api/v1/auth/login",
        data={"username": username, "password": password},
    )
    token = res.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}
    yield headers

    # Cleanup
    with SessionLocal() as db:
        user = db.scalar(select(User).where(User.username == username))
        if user:
            db.delete(user)
            db.commit()


def test_root_and_health(client):
    res_root = client.get("/")
    assert res_root.status_code == 200
    assert "Bienvenido" in res_root.json()["message"]

    res_health = client.get("/health")
    assert res_health.status_code == 200
    assert res_health.json() == {"status": "healthy"}


def test_unauthenticated_requests_fail(client):
    assert client.get("/api/v1/categories").status_code == 401
    assert client.get("/api/v1/tasks").status_code == 401


def test_category_and_task_lifecycle_with_set_null(client, auth_headers):
    # 1. Crear categoría
    cat_res = client.post(
        "/api/v1/categories",
        headers=auth_headers,
        json={"name": "Lifecycle Category", "description": "Testing Set Null", "color": "#2563EB"},
    )
    assert cat_res.status_code == 201
    cat_data = cat_res.json()
    cat_id = cat_data["id"]
    assert cat_data["owner_id"] is not None

    # 2. Paginación de categorías
    list_cat = client.get("/api/v1/categories?skip=0&limit=5", headers=auth_headers)
    assert list_cat.status_code == 200
    paginated = list_cat.json()
    assert paginated["total"] >= 1
    assert len(paginated["items"]) >= 1

    # 3. Crear tarea asociada a la categoría
    task_res = client.post(
        "/api/v1/tasks",
        headers=auth_headers,
        json={
            "title": "Lifecycle Task",
            "description": "Will survive category deletion",
            "category_id": cat_id,
            "priority": "medium",
        },
    )
    assert task_res.status_code == 201
    task_data = task_res.json()
    task_id = task_data["id"]
    assert task_data["owner_id"] == cat_data["owner_id"]
    assert task_data["category_id"] == cat_id

    # 4. Eliminar categoría
    del_cat = client.delete(f"/api/v1/categories/{cat_id}", headers=auth_headers)
    assert del_cat.status_code == 204

    # 5. Verificar que la tarea SIGUE EXISTIENDO con category_id = None
    with SessionLocal() as db:
        task_in_db = db.scalar(select(Task).where(Task.id == task_id))
        assert task_in_db is not None, "La tarea fue eliminada indebidamente al borrar la categoría"
        assert task_in_db.category_id is None, "El category_id no se actualizó a None"

        # Limpiar tarea de prueba
        db.delete(task_in_db)
        db.commit()

