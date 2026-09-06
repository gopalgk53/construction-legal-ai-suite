from fastapi.testclient import TestClient

from main import app


client = TestClient(app)


def create_test_milestone(project_id: int):
    response = client.post(
        f"/projects/{project_id}/milestones",
        json={
            "title": "Complete Automated API Tests",
            "status": "Planned",
            "due_date": "2026-09-30",
        },
    )

    assert response.status_code == 201

    return response.json()


def test_create_milestone(sample_project):
    project_id = sample_project["id"]

    response = client.post(
        f"/projects/{project_id}/milestones",
        json={
            "title": "Complete Automated API Tests",
            "status": "Planned",
            "due_date": "2026-09-30",
        },
    )

    assert response.status_code == 201

    milestone = response.json()

    assert milestone["project_id"] == project_id
    assert milestone["title"] == "Complete Automated API Tests"
    assert milestone["status"] == "Planned"
    assert milestone["due_date"] == "2026-09-30"
    assert "id" in milestone
    assert "created_at" in milestone
    assert "updated_at" in milestone


def test_create_milestone_for_missing_project():
    response = client.post(
        "/projects/999999/milestones",
        json={
            "title": "Invalid Parent Test",
            "status": "Planned",
            "due_date": None,
        },
    )

    assert response.status_code == 404
    assert response.json() == {
        "detail": "Project not found"
    }


def test_list_and_get_milestone(sample_project):
    project_id = sample_project["id"]
    milestone = create_test_milestone(project_id)

    list_response = client.get(
        f"/projects/{project_id}/milestones"
    )

    assert list_response.status_code == 200
    assert len(list_response.json()) == 1

    get_response = client.get(
        f"/projects/{project_id}/milestones/{milestone['id']}"
    )

    assert get_response.status_code == 200
    assert get_response.json()["id"] == milestone["id"]


def test_patch_preserves_unspecified_fields(sample_project):
    project_id = sample_project["id"]
    milestone = create_test_milestone(project_id)

    response = client.patch(
        f"/projects/{project_id}/milestones/{milestone['id']}",
        json={
            "status": "In Progress",
        },
    )

    assert response.status_code == 200

    updated = response.json()

    assert updated["status"] == "In Progress"
    assert updated["title"] == milestone["title"]
    assert updated["due_date"] == milestone["due_date"]


def test_delete_milestone(sample_project):
    project_id = sample_project["id"]
    milestone = create_test_milestone(project_id)

    delete_response = client.delete(
        f"/projects/{project_id}/milestones/{milestone['id']}"
    )

    assert delete_response.status_code == 200

    get_response = client.get(
        f"/projects/{project_id}/milestones/{milestone['id']}"
    )

    assert get_response.status_code == 404
    assert get_response.json() == {
        "detail": "Milestone not found"
    }