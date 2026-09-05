from urllib import response

import pytest

from fastapi.testclient import TestClient

from main import app

import time

from datetime import datetime

client = TestClient(app)

def test_get_projects():
    response = client.get("/projects")

    assert response.status_code == 200

    data = response.json()

    assert "items" in data
    assert "total" in data
    assert "limit" in data
    assert "offset" in data

    assert isinstance(data["items"], list)
    assert data["total"] == len(data["items"])
    assert data["limit"] == 10
    assert data["offset"] == 0

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

def test_patch_project_progress_only(sample_project):
    project_id = sample_project["id"]

    setup_response = client.put(
        f"/projects/{project_id}",
        json={
            "name": "Sample Project",
            "status": "In Progress",
            "progress": 50,
            "description": None,
        },
    )

    assert setup_response.status_code == 200

    response = client.patch(
        f"/projects/{project_id}",
        json={
            "progress": 70,
        },
    )

    assert response.status_code == 200

    response_data = response.json()

    assert response_data["id"] == project_id
    assert response_data["name"] == "Sample Project"
    assert response_data["status"] == "In Progress"
    assert response_data["progress"] == 70
    assert response_data["description"] is None

def test_patch_project_rejects_invalid_merged_state(
    sample_project,
):
    project_id = sample_project["id"]

    setup_response = client.put(
        f"/projects/{project_id}",
        json={
            "name": "Sample Project",
            "status": "In Progress",
            "progress": 50,
            "description": None,
        },
    )

    assert setup_response.status_code == 200

    response = client.patch(
        f"/projects/{project_id}",
        json={
            "status": "Completed",
        },
    )

    assert response.status_code == 400
    assert response.json() == {
        "detail": "Completed projects must have 100% progress"
    }

def test_patch_project_to_completed(sample_project):
    project_id = sample_project["id"]

    setup_response = client.put(
        f"/projects/{project_id}",
        json={
            "name": "Sample Project",
            "status": "In Progress",
            "progress": 50,
            "description": "Project currently in development",
        },
    )

    assert setup_response.status_code == 200

    response = client.patch(
        f"/projects/{project_id}",
        json={
            "status": "Completed",
            "progress": 100,
        },
    )

    assert response.status_code == 200

    response_data = response.json()

    assert response_data["id"] == project_id
    assert response_data["name"] == "Sample Project"
    assert response_data["status"] == "Completed"
    assert response_data["progress"] == 100

    # PATCH must preserve fields that were not supplied.
    assert response_data["description"] == (
        "Project currently in development"
    )

def test_patch_project_clear_description(sample_project):
    project_id = sample_project["id"]

    setup_response = client.put(
        f"/projects/{project_id}",
        json={
            "name": "Enterprise RAG",
            "status": "In Progress",
            "progress": 50,
            "description": "Existing project description",
        },
    )

    assert setup_response.status_code == 200

    response = client.patch(
        f"/projects/{project_id}",
        json={
            "description": None,
        },
    )

    assert response.status_code == 200

    response_data = response.json()

    assert response_data["description"] is None
    assert response_data["name"] == "Enterprise RAG"
    assert response_data["status"] == "In Progress"
    assert response_data["progress"] == 50

def test_patch_missing_project():
    response = client.patch(
        "/projects/999999",
        json={
            "description": "Should not work",
        },
    )

    assert response.status_code == 404
    assert response.json() == {
        "detail": "Project not found"
    }

def test_patch_project_with_blank_name(sample_project):
    project_id = sample_project["id"]

    response = client.patch(
        f"/projects/{project_id}",
        json={
            "name": "   ",
        },
    )

    assert response.status_code == 422

def test_patch_project_updates_timestamp(sample_project):
    project_id = sample_project["id"]

    before_response = client.get(
        f"/projects/{project_id}"
    )

    assert before_response.status_code == 200

    before_data = before_response.json()

    created_at_before = datetime.fromisoformat(
        before_data["created_at"]
    )

    updated_at_before = datetime.fromisoformat(
        before_data["updated_at"]
    )

    time.sleep(0.01)

    response = client.patch(
        f"/projects/{project_id}",
        json={
            "description": "Timestamp update test",
        },
    )

    assert response.status_code == 200

    after_data = response.json()

    created_at_after = datetime.fromisoformat(
        after_data["created_at"]
    )

    updated_at_after = datetime.fromisoformat(
        after_data["updated_at"]
    )

    assert created_at_after == created_at_before
    assert updated_at_after > updated_at_before

def test_filter_projects_by_status():
    client.post(
        "/projects",
        json={
            "name": "Planned Project",
            "status": "Planned",
            "progress": 0,
        },
    )

    client.post(
        "/projects",
        json={
            "name": "Completed Project",
            "status": "Completed",
            "progress": 100,
        },
    )

    response = client.get(
        "/projects",
        params={
            "status": "Completed",
        },
    )

    data = response.json()
    projects = data["items"]

    assert response.status_code == 200
    assert len(projects) == 1
    assert data["total"] == 1
    assert projects[0]["name"] == "Completed Project"
    assert projects[0]["status"] == "Completed"

def test_filter_projects_with_invalid_status():
    response = client.get(
        "/projects",
        params={
            "status": "Finished",
        },
    )

    assert response.status_code == 422

def test_search_projects_by_name():
    client.post(
        "/projects",
        json={
            "name": "Enterprise RAG Platform",
            "status": "Planned",
            "progress": 0,
        },
    )

    client.post(
        "/projects",
        json={
            "name": "Multi-Agent Workflow",
            "status": "Planned",
            "progress": 0,
        },
    )

    response = client.get(
        "/projects",
        params={
            "search": "rag",
        },
    )

    assert response.status_code == 200

    data = response.json()
    projects = data["items"]

    assert len(projects) == 1
    assert data["total"] == 1
    assert projects[0]["name"] == "Enterprise RAG Platform"

def test_filter_projects_by_status_and_search():
    client.post(
        "/projects",
        json={
            "name": "Enterprise RAG Production",
            "status": "Completed",
            "progress": 100,
        },
    )

    client.post(
        "/projects",
        json={
            "name": "Enterprise RAG Prototype",
            "status": "Planned",
            "progress": 0,
        },
    )

    client.post(
        "/projects",
        json={
            "name": "Multi-Agent Platform",
            "status": "Completed",
            "progress": 100,
        },
    )

    response = client.get(
        "/projects",
        params={
            "status": "Completed",
            "search": "rag",
        },
    )

    data = response.json()
    projects = data["items"]

    assert response.status_code == 200
    assert len(projects) == 1
    assert data["total"] == 1
    assert projects[0]["name"] == "Enterprise RAG Production"
    assert projects[0]["status"] == "Completed"

def test_blank_search_returns_all_projects():
    client.post(
        "/projects",
        json={
            "name": "Enterprise RAG",
            "status": "Planned",
            "progress": 0,
        },
    )

    client.post(
        "/projects",
        json={
            "name": "Multi-Agent Workflow",
            "status": "Planned",
            "progress": 0,
        },
    )

    response = client.get(
        "/projects",
        params={
            "search": "   ",
        },
    )

    assert response.status_code == 200

    data = response.json()
    projects = data["items"]

    assert len(projects) == 2
    assert data["total"] == 2

def test_projects_pagination():
    for index in range(5):
        response = client.post(
            "/projects",
            json={
                "name": f"Project {index + 1}",
                "status": "Planned",
                "progress": 0,
            },
        )

        assert response.status_code == 201

    response = client.get(
        "/projects",
        params={
            "limit": 2,
            "offset": 1,
        },
    )

    assert response.status_code == 200

    data = response.json()
    projects = data["items"]

    assert len(projects) == 2
    assert data["total"] == 5
    assert data["limit"] == 2
    assert data["offset"] == 1

    assert projects[0]["name"] == "Project 2"
    assert projects[1]["name"] == "Project 3"

def test_project_route_contract():
    schema = client.app.openapi()

    paths = schema["paths"]

    assert "/projects" in paths
    assert "/projects/{project_id}" in paths

    assert "get" in paths["/projects"]
    assert "post" in paths["/projects"]

    assert "get" in paths["/projects/{project_id}"]
    assert "put" in paths["/projects/{project_id}"]
    assert "patch" in paths["/projects/{project_id}"]
    assert "delete" in paths["/projects/{project_id}"]

def test_projects_pagination_rejects_zero_limit():
    response = client.get(
        "/projects",
        params={
            "limit": 0,
        },
    )

    assert response.status_code == 422


def test_projects_pagination_rejects_limit_above_maximum():
    response = client.get(
        "/projects",
        params={
            "limit": 101,
        },
    )

    assert response.status_code == 422


def test_projects_pagination_rejects_negative_offset():
    response = client.get(
        "/projects",
        params={
            "offset": -1,
        },
    )

    assert response.status_code == 422