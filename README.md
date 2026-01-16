# ToDo List (Flask + SQLAlchemy + Jinja + Bootstrap + Docker)

A web-based ToDo application built with Flask. The project includes a browser UI (Jinja + Bootstrap), a JSON REST API with Swagger documentation, automated tests, CI via GitHub Actions, and CD via Render.

## Features
- Create, edit, delete tasks
- Toggle Done/Undone without page reload (fetch -> JSON)
- Filters: All / Active / Done
- Search by title
- Sorting: newest / priority / due date
- REST API (JSON) + Swagger UI

---

## Technologies
- Python 3.11
- Flask
- Flask-SQLAlchemy (SQLite)
- Jinja2 templates
- Bootstrap 5
- JavaScript (fetch) for toggle/delete
- Swagger/OpenAPI UI: Flasgger (`/apidocs`)
- Tests: pytest
- CI: GitHub Actions
- CD: Render (Docker deploy)

---

## Project Structure

todo_app/
app/
**init**.py
models.py
routes.py
templates/
base.html
index.html
task_form.html
_task_card.html
static/
css/
styles.css
js/
main.js
task_form.js
tests/
conftest.py
test_api.py
.github/
workflows/
ci.yml
run.py
requirements.txt
Dockerfile
render.yaml
.dockerignore
README.md

---

## Run Locally (without Docker)

### 1) Install dependencies
```bash
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements.txt
````

### 2) Start the server

```bash
python run.py
```

Open in browser:

* UI: [http://127.0.0.1:5000](http://127.0.0.1:5000)
* Swagger UI: [http://127.0.0.1:5000/apidocs](http://127.0.0.1:5000/apidocs)

---

## Run with Docker

### 1) Build image

```bash
docker build -t todo-app .
```

### 2) Run container

```bash
docker run --rm -p 5000:5000 todo-app
```

Open in browser:

* UI: [http://127.0.0.1:5000](http://127.0.0.1:5000)
* Swagger UI: [http://127.0.0.1:5000/apidocs](http://127.0.0.1:5000/apidocs)

---

## REST API

### Base endpoints

* `GET /api/tasks` — list tasks
  Query params: `status=all|active|done`, `q=<text>`, `sort=newest|priority|due`
* `POST /api/tasks` — create task (JSON)
* `PUT /api/tasks/<id>` — update task (JSON)
* `DELETE /api/tasks/<id>` — delete task (JSON)

### UI AJAX endpoints

Used by the browser UI:

* `POST /tasks/<id>/toggle` — toggle `is_done` (returns JSON)
* `POST /tasks/<id>/delete` — delete task (returns JSON)

Swagger UI:

* `GET /apidocs`

---

## Run Tests

```bash
pytest -q
```

---

## CI (GitHub Actions)

Workflow file:

* `.github/workflows/ci.yml`

What it does:

* installs dependencies
* runs `pytest`

---

## CD (Render)

A simple CD setup using Docker deploy on Render:

1. Push the repository to GitHub
2. On Render: **New** → **Web Service**
3. Connect your GitHub repository
4. Set environment to **Docker**
5. Enable **Auto Deploy**
6. Render will deploy automatically on each push to the selected branch

`render.yaml` is included for convenience.

---

## Logs

### Docker logs (local)

1. Get container id:

```bash
docker ps
```

2. View logs:

```bash
docker logs <container_id>
```

The application logs key actions (create/update/toggle/delete) to stdout, which is the standard approach for Docker-based deployments.

---

## Configuration

Environment variables (optional):

* `DATABASE_URL` — database connection string (default: `sqlite:///todo.db`)
* `SECRET_KEY` — Flask secret key (default: `dev-secret`)
* `LOG_LEVEL` — logging level (default: `INFO`)
