from fastapi.testclient import TestClient

from main import app


client = TestClient(app)


def create_test_milestone(project_id: int):
    response = client.post(
        f"/projects/{project_id}/milestones",
        json={
            "title": "Task Testing Milestone",
            "status": "In Progress",
            "due_date": "2026-09-30",
        },
    )

    assert response.status_code == 201

    return response.json()


def create_test_task(
    project_id: int,
    milestone_id: int,
):
    response = client.post(
        (
            f"/projects/{project_id}"
            f"/milestones/{milestone_id}"
            "/tasks"
        ),
        json={
            "title": "Write Task API tests",
            "description": "Verify the nested Task API.",
            "status": "Planned",
            "priority": "High",
            "due_date": "2026-09-15",
        },
    )

    assert response.status_code == 201

    return response.json()


def test_create_task(sample_project):
    project_id = sample_project["id"]
    milestone = create_test_milestone(project_id)

    task = create_test_task(
        project_id,
        milestone["id"],
    )

    assert task["milestone_id"] == milestone["id"]
    assert task["title"] == "Write Task API tests"
    assert task["status"] == "Planned"
    assert task["priority"] == "High"
    assert task["due_date"] == "2026-09-15"
    assert "id" in task
    assert "created_at" in task
    assert "updated_at" in task


def test_create_task_for_missing_milestone(sample_project):
    project_id = sample_project["id"]

    response = client.post(
        f"/projects/{project_id}/milestones/999999/tasks",
        json={
            "title": "Invalid Parent Test",
            "description": None,
            "status": "Planned",
            "priority": "Medium",
            "due_date": None,
        },
    )

    assert response.status_code == 404
    assert response.json() == {
        "detail": "Milestone not found"
    }


def test_reject_unknown_task_field(sample_project):
    project_id = sample_project["id"]
    milestone = create_test_milestone(project_id)

    response = client.post(
        (
            f"/projects/{project_id}"
            f"/milestones/{milestone['id']}"
            "/tasks"
        ),
        json={
            "title": "Unknown Field Test",
            "status": "Planned",
            "priority": "Medium",
            "priorty": "High",
        },
    )

    assert response.status_code == 422


def test_list_and_get_task(sample_project):
    project_id = sample_project["id"]
    milestone = create_test_milestone(project_id)
    task = create_test_task(
        project_id,
        milestone["id"],
    )

    list_response = client.get(
        (
            f"/projects/{project_id}"
            f"/milestones/{milestone['id']}"
            "/tasks"
        )
    )

    assert list_response.status_code == 200
    assert len(list_response.json()) == 1

    get_response = client.get(
        (
            f"/projects/{project_id}"
            f"/milestones/{milestone['id']}"
            f"/tasks/{task['id']}"
        )
    )

    assert get_response.status_code == 200
    assert get_response.json()["id"] == task["id"]


def test_update_task(sample_project):
    project_id = sample_project["id"]
    milestone = create_test_milestone(project_id)
    task = create_test_task(
        project_id,
        milestone["id"],
    )

    response = client.put(
        (
            f"/projects/{project_id}"
            f"/milestones/{milestone['id']}"
            f"/tasks/{task['id']}"
        ),
        json={
            "title": "Complete Task API tests",
            "description": "All CRUD paths are tested.",
            "status": "Completed",
            "priority": "Medium",
            "due_date": "2026-09-16",
        },
    )

    assert response.status_code == 200

    updated = response.json()

    assert updated["title"] == "Complete Task API tests"
    assert updated["status"] == "Completed"
    assert updated["priority"] == "Medium"
    assert updated["due_date"] == "2026-09-16"


def test_patch_task_preserves_unspecified_fields(
    sample_project,
):
    project_id = sample_project["id"]
    milestone = create_test_milestone(project_id)
    task = create_test_task(
        project_id,
        milestone["id"],
    )

    response = client.patch(
        (
            f"/projects/{project_id}"
            f"/milestones/{milestone['id']}"
            f"/tasks/{task['id']}"
        ),
        json={
            "status": "In Progress",
        },
    )

    assert response.status_code == 200

    updated = response.json()

    assert updated["status"] == "In Progress"
    assert updated["title"] == task["title"]
    assert updated["description"] == task["description"]
    assert updated["priority"] == task["priority"]
    assert updated["due_date"] == task["due_date"]


def test_delete_task(sample_project):
    project_id = sample_project["id"]
    milestone = create_test_milestone(project_id)
    task = create_test_task(
        project_id,
        milestone["id"],
    )

    delete_response = client.delete(
        (
            f"/projects/{project_id}"
            f"/milestones/{milestone['id']}"
            f"/tasks/{task['id']}"
        )
    )

    assert delete_response.status_code == 200

    get_response = client.get(
        (
            f"/projects/{project_id}"
            f"/milestones/{milestone['id']}"
            f"/tasks/{task['id']}"
        )
    )

    assert get_response.status_code == 404
    assert get_response.json() == {
        "detail": "Task not found"
    }

def test_task_completion_updates_milestone_progress(
    sample_project,
):
    project_id = sample_project["id"]
    milestone = create_test_milestone(project_id)

    first_task = create_test_task(
        project_id,
        milestone["id"],
    )
    second_task = create_test_task(
        project_id,
        milestone["id"],
    )

    milestone_url = (
        f"/projects/{project_id}"
        f"/milestones/{milestone['id']}"
    )

    response = client.get(milestone_url)

    assert response.json()["progress"] == 0
    assert response.json()["status"] == "Planned"

    client.patch(
        f"{milestone_url}/tasks/{first_task['id']}",
        json={"status": "Completed"},
    )

    response = client.get(milestone_url)

    assert response.json()["progress"] == 50
    assert response.json()["status"] == "In Progress"

    client.patch(
        f"{milestone_url}/tasks/{second_task['id']}",
        json={"status": "Completed"},
    )

    response = client.get(milestone_url)

    assert response.json()["progress"] == 100
    assert response.json()["status"] == "Completed"

def test_deleting_completed_task_recalculates_progress(
    sample_project,
):
    project_id = sample_project["id"]
    milestone = create_test_milestone(project_id)

    completed_task = create_test_task(
        project_id,
        milestone["id"],
    )
    create_test_task(
        project_id,
        milestone["id"],
    )

    milestone_url = (
        f"/projects/{project_id}"
        f"/milestones/{milestone['id']}"
    )

    client.patch(
        f"{milestone_url}/tasks/{completed_task['id']}",
        json={"status": "Completed"},
    )

    response = client.get(milestone_url)
    assert response.json()["progress"] == 50

    client.delete(
        f"{milestone_url}/tasks/{completed_task['id']}"
    )

    response = client.get(milestone_url)

    assert response.json()["progress"] == 0
    assert response.json()["status"] == "Planned"