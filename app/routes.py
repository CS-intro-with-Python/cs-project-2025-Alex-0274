from datetime import datetime
from flask import Blueprint, render_template, request, redirect, url_for, jsonify, abort, current_app
from flasgger import swag_from
from . import db
from .models import TodoItem

bp = Blueprint("main", __name__)


def _parse_priority(value: str | None) -> int:
    try:
        p = int(value) if value is not None else 2
    except ValueError:
        p = 2
    return p if p in (1, 2, 3) else 2


def _parse_due_date(value: str | None):
    if not value:
        return None
    try:
        return datetime.strptime(value, "%Y-%m-%d").date()
    except ValueError:
        return None


def _apply_filters(query):
    status = request.args.get("status", "all")
    q = (request.args.get("q") or "").strip()
    sort = request.args.get("sort", "newest")

    if status == "active":
        query = query.filter(TodoItem.is_done.is_(False))
    elif status == "done":
        query = query.filter(TodoItem.is_done.is_(True))

    if q:
        query = query.filter(TodoItem.title.ilike(f"%{q}%"))

    if sort == "priority":
        query = query.order_by(TodoItem.is_done.asc(), TodoItem.priority.desc(), TodoItem.created_at.desc())
    elif sort == "due":
        query = query.order_by(TodoItem.is_done.asc(), TodoItem.due_date.asc(), TodoItem.created_at.desc())
    else:
        query = query.order_by(TodoItem.is_done.asc(), TodoItem.created_at.desc())

    return query, {"status": status, "q": q, "sort": sort}


@bp.get("/")
def index():
    query, ui = _apply_filters(TodoItem.query)
    items = query.all()
    return render_template("index.html", items=items, ui=ui)


@bp.get("/tasks/new")
def task_new_get():
    return render_template(
        "task_form.html",
        mode="create",
        task=None,
        form_action=url_for("main.task_new_post"),
    )


@bp.post("/tasks/new")
def task_new_post():
    title = (request.form.get("title") or "").strip()
    description = (request.form.get("description") or "").strip() or None
    priority = _parse_priority(request.form.get("priority"))
    due_date = _parse_due_date(request.form.get("due_date"))

    if not title:
        return render_template(
            "task_form.html",
            mode="create",
            task={"title": title, "description": description, "priority": priority, "due_date": due_date},
            form_action=url_for("main.task_new_post"),
            error="Title is required.",
        ), 400

    task = TodoItem(title=title, description=description, priority=priority, due_date=due_date)
    db.session.add(task)
    db.session.commit()

    current_app.logger.info("Created task id=%s title=%r", task.id, task.title)
    return redirect(url_for("main.index"))


@bp.get("/tasks/<int:task_id>/edit")
def task_edit_get(task_id: int):
    task = TodoItem.query.get(task_id)
    if not task:
        abort(404)

    return render_template(
        "task_form.html",
        mode="edit",
        task=task,
        form_action=url_for("main.task_edit_post", task_id=task_id),
    )


@bp.post("/tasks/<int:task_id>/edit")
def task_edit_post(task_id: int):
    task = TodoItem.query.get(task_id)
    if not task:
        abort(404)

    title = (request.form.get("title") or "").strip()
    description = (request.form.get("description") or "").strip() or None
    priority = _parse_priority(request.form.get("priority"))
    due_date = _parse_due_date(request.form.get("due_date"))

    if not title:
        return render_template(
            "task_form.html",
            mode="edit",
            task=task,
            form_action=url_for("main.task_edit_post", task_id=task_id),
            error="Title is required.",
        ), 400

    task.title = title
    task.description = description
    task.priority = priority
    task.due_date = due_date

    db.session.commit()
    current_app.logger.info("Updated task id=%s", task.id)
    return redirect(url_for("main.index"))


@bp.post("/tasks/<int:task_id>/toggle")
@swag_from({
    "tags": ["UI AJAX"],
    "summary": "Toggle task done/undone (used by browser UI)",
    "parameters": [
        {"name": "task_id", "in": "path", "type": "integer", "required": True},
    ],
    "responses": {
        200: {
            "description": "OK",
            "schema": {
                "type": "object",
                "properties": {
                    "ok": {"type": "boolean"},
                    "task": {"type": "object"},
                }
            }
        },
        404: {"description": "Task not found"},
    }
})
def task_toggle(task_id: int):
    task = TodoItem.query.get(task_id)
    if not task:
        return jsonify({"ok": False, "error": "Task not found"}), 404

    task.is_done = not task.is_done
    db.session.commit()

    current_app.logger.info("Toggled task id=%s is_done=%s", task.id, task.is_done)
    return jsonify({"ok": True, "task": task.to_dict()})


@bp.post("/tasks/<int:task_id>/delete")
@swag_from({
    "tags": ["UI AJAX"],
    "summary": "Delete task (used by browser UI)",
    "parameters": [
        {"name": "task_id", "in": "path", "type": "integer", "required": True},
    ],
    "responses": {
        200: {"description": "OK", "schema": {"type": "object", "properties": {"ok": {"type": "boolean"}}}},
        404: {"description": "Task not found"},
    }
})
def task_delete(task_id: int):
    task = TodoItem.query.get(task_id)
    if not task:
        return jsonify({"ok": False, "error": "Task not found"}), 404

    db.session.delete(task)
    db.session.commit()

    current_app.logger.info("Deleted task id=%s", task_id)
    return jsonify({"ok": True})


@bp.get("/api/tasks")
@swag_from({
    "tags": ["REST API"],
    "summary": "List tasks",
    "parameters": [
        {"name": "status", "in": "query", "type": "string", "enum": ["all", "active", "done"], "required": False},
        {"name": "q", "in": "query", "type": "string", "required": False},
        {"name": "sort", "in": "query", "type": "string", "enum": ["newest", "priority", "due"], "required": False},
    ],
    "responses": {
        200: {
            "description": "OK",
            "schema": {"type": "object", "properties": {"items": {"type": "array"}}},
        }
    }
})
def api_list_tasks():
    query, ui = _apply_filters(TodoItem.query)
    items = [t.to_dict() for t in query.all()]
    return jsonify({"items": items, "ui": ui})


@bp.post("/api/tasks")
@swag_from({
    "tags": ["REST API"],
    "summary": "Create task (JSON)",
    "consumes": ["application/json"],
    "parameters": [
        {
            "name": "body",
            "in": "body",
            "required": True,
            "schema": {
                "type": "object",
                "required": ["title"],
                "properties": {
                    "title": {"type": "string"},
                    "description": {"type": "string"},
                    "priority": {"type": "integer", "enum": [1, 2, 3]},
                    "due_date": {"type": "string", "example": "2026-01-20"},
                },
            },
        }
    ],
    "responses": {
        201: {"description": "Created"},
        400: {"description": "Validation error"},
    }
})
def api_create_task():
    data = request.get_json(force=True, silent=True) or {}
    title = (data.get("title") or "").strip()
    if not title:
        return jsonify({"error": "title is required"}), 400

    description = (data.get("description") or "").strip() or None
    priority = _parse_priority(str(data.get("priority")) if data.get("priority") is not None else None)
    due_date = _parse_due_date(data.get("due_date"))

    task = TodoItem(title=title, description=description, priority=priority, due_date=due_date)
    db.session.add(task)
    db.session.commit()

    current_app.logger.info("API created task id=%s", task.id)
    return jsonify({"task": task.to_dict()}), 201


@bp.put("/api/tasks/<int:task_id>")
@swag_from({
    "tags": ["REST API"],
    "summary": "Update task (JSON)",
    "consumes": ["application/json"],
    "parameters": [
        {"name": "task_id", "in": "path", "type": "integer", "required": True},
        {
            "name": "body",
            "in": "body",
            "required": True,
            "schema": {
                "type": "object",
                "properties": {
                    "title": {"type": "string"},
                    "description": {"type": "string"},
                    "priority": {"type": "integer", "enum": [1, 2, 3]},
                    "due_date": {"type": "string"},
                    "is_done": {"type": "boolean"},
                },
            },
        }
    ],
    "responses": {
        200: {"description": "OK"},
        404: {"description": "Not found"},
    }
})
def api_update_task(task_id: int):
    task = TodoItem.query.get(task_id)
    if not task:
        return jsonify({"error": "task not found"}), 404

    data = request.get_json(force=True, silent=True) or {}

    if "title" in data:
        title = (data.get("title") or "").strip()
        if not title:
            return jsonify({"error": "title cannot be empty"}), 400
        task.title = title

    if "description" in data:
        task.description = (data.get("description") or "").strip() or None

    if "priority" in data:
        task.priority = _parse_priority(str(data.get("priority")))

    if "due_date" in data:
        task.due_date = _parse_due_date(data.get("due_date"))

    if "is_done" in data:
        task.is_done = bool(data.get("is_done"))

    db.session.commit()
    current_app.logger.info("API updated task id=%s", task.id)
    return jsonify({"task": task.to_dict()}), 200


@bp.delete("/api/tasks/<int:task_id>")
@swag_from({
    "tags": ["REST API"],
    "summary": "Delete task (JSON)",
    "parameters": [
        {"name": "task_id", "in": "path", "type": "integer", "required": True},
    ],
    "responses": {
        200: {"description": "OK"},
        404: {"description": "Not found"},
    }
})
def api_delete_task(task_id: int):
    task = TodoItem.query.get(task_id)
    if not task:
        return jsonify({"error": "task not found"}), 404

    db.session.delete(task)
    db.session.commit()
    current_app.logger.info("API deleted task id=%s", task_id)
    return jsonify({"ok": True}), 200
