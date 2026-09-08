from fastapi.testclient import TestClient

from main import app


client = TestClient(app)


def test_create_learning_session():
    response = client.post(
        "/learning-sessions",
        json={
            "session_date": "2026-09-08",
            "status": "Planned",
            "planned_minutes": 300,
            "completed_minutes": 0,
            "focus": (
                "Build the daily learning-session API"
            ),
            "learned": None,
            "challenges": None,
            "improvements": None,
            "tomorrow_priority": None,
        },
    )

    assert response.status_code == 201

    learning_session = response.json()

    assert learning_session["session_date"] == "2026-09-08"
    assert learning_session["status"] == "Planned"
    assert learning_session["planned_minutes"] == 300
    assert learning_session["completed_minutes"] == 0
    assert learning_session["focus"] == (
        "Build the daily learning-session API"
    )
    assert "id" in learning_session
    assert "created_at" in learning_session
    assert "updated_at" in learning_session


def test_reject_duplicate_learning_session_date():
    session_data = {
        "session_date": "2026-09-08",
        "status": "Planned",
        "planned_minutes": 360,
        "completed_minutes": 0,
        "focus": "First session for this date",
        "learned": None,
        "challenges": None,
        "improvements": None,
        "tomorrow_priority": None,
    }

    first_response = client.post(
        "/learning-sessions",
        json=session_data,
    )

    assert first_response.status_code == 201

    second_response = client.post(
        "/learning-sessions",
        json=session_data,
    )

    assert second_response.status_code == 409
    assert second_response.json() == {
        "detail": (
            "A learning session already exists "
            "for this date"
        )
    }


def test_list_and_get_learning_session():
    first_response = client.post(
        "/learning-sessions",
        json={
            "session_date": "2026-09-07",
            "status": "Completed",
            "planned_minutes": 240,
            "completed_minutes": 260,
            "focus": "Complete project progress",
        },
    )

    second_response = client.post(
        "/learning-sessions",
        json={
            "session_date": "2026-09-08",
            "status": "In Progress",
            "planned_minutes": 360,
            "completed_minutes": 180,
            "focus": "Build learning-session tracking",
        },
    )

    assert first_response.status_code == 201
    assert second_response.status_code == 201

    list_response = client.get(
        "/learning-sessions"
    )

    assert list_response.status_code == 200

    learning_sessions = list_response.json()

    assert len(learning_sessions) == 2
    assert learning_sessions[0]["session_date"] == (
        "2026-09-08"
    )
    assert learning_sessions[1]["session_date"] == (
        "2026-09-07"
    )

    learning_session_id = second_response.json()["id"]

    get_response = client.get(
        f"/learning-sessions/{learning_session_id}"
    )

    assert get_response.status_code == 200
    assert get_response.json()["id"] == (
        learning_session_id
    )
    assert get_response.json()["focus"] == (
        "Build learning-session tracking"
    )

def test_get_missing_learning_session():
    response = client.get(
        "/learning-sessions/999999"
    )

    assert response.status_code == 404
    assert response.json() == {
        "detail": "Learning session not found"
    }


def test_update_learning_session():
    create_response = client.post(
        "/learning-sessions",
        json={
            "session_date": "2026-09-08",
            "status": "Planned",
            "planned_minutes": 300,
            "completed_minutes": 0,
            "focus": "Plan the learning-session API",
        },
    )

    assert create_response.status_code == 201

    learning_session_id = (
        create_response.json()["id"]
    )

    update_response = client.put(
        (
            "/learning-sessions/"
            f"{learning_session_id}"
        ),
        json={
            "session_date": "2026-09-08",
            "status": "Completed",
            "planned_minutes": 300,
            "completed_minutes": 320,
            "focus": "Complete the learning-session API",
            "learned": (
                "Learned model, migration and API layers."
            ),
            "challenges": "Handled date uniqueness.",
            "improvements": (
                "Improved transaction error handling."
            ),
            "tomorrow_priority": (
                "Implement partial session updates."
            ),
        },
    )

    assert update_response.status_code == 200

    updated_session = update_response.json()

    assert updated_session["status"] == "Completed"
    assert updated_session["completed_minutes"] == 320
    assert updated_session["focus"] == (
        "Complete the learning-session API"
    )
    assert updated_session["learned"] == (
        "Learned model, migration and API layers."
    )
    assert updated_session["tomorrow_priority"] == (
        "Implement partial session updates."
    )


def test_patch_learning_session_preserves_fields():
    create_response = client.post(
        "/learning-sessions",
        json={
            "session_date": "2026-09-08",
            "status": "Planned",
            "planned_minutes": 360,
            "completed_minutes": 0,
            "focus": "Build partial session updates",
            "learned": "Learn PATCH semantics.",
            "challenges": None,
            "improvements": None,
            "tomorrow_priority": "Add deletion support.",
        },
    )

    assert create_response.status_code == 201

    original_session = create_response.json()
    learning_session_id = original_session["id"]

    patch_response = client.patch(
        (
            "/learning-sessions/"
            f"{learning_session_id}"
        ),
        json={
            "status": "In Progress",
            "completed_minutes": 180,
        },
    )

    assert patch_response.status_code == 200

    updated_session = patch_response.json()

    assert updated_session["status"] == "In Progress"
    assert updated_session["completed_minutes"] == 180

    assert updated_session["session_date"] == (
        original_session["session_date"]
    )
    assert updated_session["planned_minutes"] == (
        original_session["planned_minutes"]
    )
    assert updated_session["focus"] == (
        original_session["focus"]
    )
    assert updated_session["learned"] == (
        original_session["learned"]
    )
    assert updated_session["tomorrow_priority"] == (
        original_session["tomorrow_priority"]
    )


def test_delete_learning_session():
    create_response = client.post(
        "/learning-sessions",
        json={
            "session_date": "2026-09-08",
            "status": "Planned",
            "planned_minutes": 240,
            "completed_minutes": 0,
            "focus": "Test session deletion",
        },
    )

    assert create_response.status_code == 201

    learning_session_id = (
        create_response.json()["id"]
    )
    learning_session_url = (
        "/learning-sessions/"
        f"{learning_session_id}"
    )

    delete_response = client.delete(
        learning_session_url
    )

    assert delete_response.status_code == 200
    assert delete_response.json() == {
        "message": (
            "Learning session deleted successfully"
        )
    }

    get_response = client.get(
        learning_session_url
    )

    assert get_response.status_code == 404
    assert get_response.json() == {
        "detail": "Learning session not found"
    }


def test_patch_rejects_null_required_field():
    create_response = client.post(
        "/learning-sessions",
        json={
            "session_date": "2026-09-08",
            "status": "Planned",
            "planned_minutes": 360,
            "completed_minutes": 0,
            "focus": "Protect required session fields",
        },
    )

    assert create_response.status_code == 201

    learning_session_id = (
        create_response.json()["id"]
    )
    learning_session_url = (
        "/learning-sessions/"
        f"{learning_session_id}"
    )

    patch_response = client.patch(
        learning_session_url,
        json={
            "focus": None,
        },
    )

    assert patch_response.status_code == 422

    get_response = client.get(
        learning_session_url
    )

    assert get_response.status_code == 200
    assert get_response.json()["focus"] == (
        "Protect required session fields"
    )