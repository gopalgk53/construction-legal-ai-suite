from urllib import response

import pytest

from fastapi.testclient import TestClient

from main import app

client = TestClient(app)

def test_get_projects():
    response = client.get("/projects")

    assert response.status_code == 200
    assert response.json() == []

def test_create_project():
    payload = {
        "name": "Automated Test Project",
        "status": "Planned",
        "progress": 0,
    }

    response = client.post(
        "/projects",
        json=payload,
    )

    assert response.status_code == 201

    response_data = response.json()

    assert response_data["name"] == "Automated Test Project"
    assert response_data["status"] == "Planned"
    assert response_data["progress"] == 0
    assert "id" in response_data


def test_create_project_with_blank_name():
    payload = {
        "name": "     ",
        "status": "Planned",
        "progress": 0,
    }

    response = client.post(
        "/projects",
        json=payload,
    )

    assert response.status_code == 422

@pytest.mark.parametrize(
    "status, progress, expected_detail",
    [
        (
            "Planned",
            50,
            "Planned projects must have 0% progress",
        ),
        (
            "In Progress",
            0,
            "In Progress projects must have progress between 1 and 99",
        ),
        (
            "In Progress",
            100,
            "In Progress projects must have progress between 1 and 99",
        ),
        (
            "Completed",
            50,
            "Completed projects must have 100% progress",
        ),
    ],
)
def test_invalid_project_states(
    status,
    progress,
    expected_detail,
):
    payload = {
        "name": "Business Rule Test",
        "status": status,
        "progress": progress,
    }

    response = client.post(
        "/projects",
        json=payload,
    )

    assert response.status_code == 400
    assert response.json() == {
        "detail": expected_detail
    }

def test_get_project_by_id(sample_project):
    project_id = sample_project["id"]

    response = client.get(
        f"/projects/{project_id}"
    )

    assert response.status_code == 200

    response_data = response.json()

    assert response_data["id"] == project_id
    assert response_data["name"] == "Sample Project"
    assert response_data["status"] == "Planned"
    assert response_data["progress"] == 0

def test_get_missing_project():
    response = client.get("/projects/999999")

    assert response.status_code == 404
    assert response.json() == {
        "detail": "Project not found"
    }

def test_update_project():
    # Arrange
    create_response = client.post(
        "/projects",
        json={
            "name": "Update Test Project",
            "status": "Planned",
            "progress": 0,
        },
    )

    project_id = create_response.json()["id"]

    update_payload = {
        "name": "Update Test Project",
        "status": "In Progress",
        "progress": 50,
    }

    # Act
    response = client.put(
        f"/projects/{project_id}",
        json=update_payload,
    )

    # Assert
    assert response.status_code == 200

    response_data = response.json()

    assert response_data["id"] == project_id
    assert response_data["name"] == "Update Test Project"
    assert response_data["status"] == "In Progress"
    assert response_data["progress"] == 50

def test_invalid_update_does_not_modify_project():
    # Arrange
    create_response = client.post(
        "/projects",
        json={
            "name": "Database Integrity Test",
            "status": "Planned",
            "progress": 0,
        },
    )

    project_id = create_response.json()["id"]

    # Act
    update_response = client.put(
        f"/projects/{project_id}",
        json={
            "name": "Database Integrity Test",
            "status": "Completed",
            "progress": 50,
        },
    )

    # Assert the update was rejected
    assert update_response.status_code == 400

    # Read the project again from the API
    get_response = client.get(
        f"/projects/{project_id}"
    )

    assert get_response.status_code == 200

    project = get_response.json()

    # Verify original state survived
    assert project["status"] == "Planned"
    assert project["progress"] == 0

def test_update_missing_project():
    response = client.put(
        "/projects/999999",
        json={
            "name": "Ghost Project",
            "status": "Planned",
            "progress": 0,
        },
    )

    assert response.status_code == 404
    assert response.json() == {
        "detail": "Project not found"
    }

def test_delete_project():
    # Arrange
    create_response = client.post(
        "/projects",
        json={
            "name": "Delete Test Project",
            "status": "Planned",
            "progress": 0,
        },
    )

    project_id = create_response.json()["id"]

    # Act
    delete_response = client.delete(
        f"/projects/{project_id}"
    )

    # Assert DELETE succeeded
    assert delete_response.status_code == 200

    # Verify the project is actually gone
    get_response = client.get(
        f"/projects/{project_id}"
    )

    assert get_response.status_code == 404
    assert get_response.json() == {
        "detail": "Project not found"
    }

def test_delete_missing_project():
    response = client.delete(
        "/projects/999999"
    )

    assert response.status_code == 404
    assert response.json() == {
        "detail": "Project not found"
    }

def test_create_project_with_description():
    payload = {
        "name": "Enterprise RAG Platform",
        "status": "Planned",
        "progress": 0,
        "description": "Production RAG platform for legal construction documents.",
    }

    response = client.post(
        "/projects",
        json=payload,
    )

    assert response.status_code == 201

    response_data = response.json()

    assert response_data["name"] == "Enterprise RAG Platform"
    assert response_data["description"] == (
        "Production RAG platform for legal construction documents."
    )

def test_update_project_description(sample_project):
    project_id = sample_project["id"]

    payload = {
        "name": "Updated AI Portfolio Commander",
        "status": "In Progress",
        "progress": 60,
        "description": "Updated production-ready AI portfolio management platform.",
    }

    response = client.put(
        f"/projects/{project_id}",
        json=payload,
    )

    assert response.status_code == 200

    response_data = response.json()

    assert response_data["id"] == project_id
    assert response_data["description"] == (
        "Updated production-ready AI portfolio management platform."
    )
def test_description_exceeds_max_length():
    payload = {
        "name": "Large Description Test",
        "status": "Planned",
        "progress": 0,
        "description": "A" * 1001,
    }

    response = client.post(
        "/projects",
        json=payload,
    )

    assert response.status_code == 422