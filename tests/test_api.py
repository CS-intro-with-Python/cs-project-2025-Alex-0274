def test_create_and_list_tasks(client):
    r = client.post("/api/tasks", json={"title": "Test task", "priority": 3})
    assert r.status_code == 201
    data = r.get_json()
    assert data["task"]["title"] == "Test task"
    task_id = data["task"]["id"]

    r = client.get("/api/tasks")
    assert r.status_code == 200
    data = r.get_json()
    assert len(data["items"]) == 1
    assert data["items"][0]["id"] == task_id


def test_update_task(client):
    r = client.post("/api/tasks", json={"title": "Old"})
    task_id = r.get_json()["task"]["id"]

    r = client.put(f"/api/tasks/{task_id}", json={"title": "New", "is_done": True})
    assert r.status_code == 200
    data = r.get_json()
    assert data["task"]["title"] == "New"
    assert data["task"]["is_done"] is True


def test_toggle_and_delete_ui_endpoints(client):
    r = client.post("/api/tasks", json={"title": "Toggle me"})
    task_id = r.get_json()["task"]["id"]

    r = client.post(f"/tasks/{task_id}/toggle")
    assert r.status_code == 200
    data = r.get_json()
    assert data["ok"] is True
    assert data["task"]["is_done"] is True

    r = client.post(f"/tasks/{task_id}/delete")
    assert r.status_code == 200
    data = r.get_json()
    assert data["ok"] is True

    r = client.delete(f"/api/tasks/{task_id}")
    assert r.status_code == 404
