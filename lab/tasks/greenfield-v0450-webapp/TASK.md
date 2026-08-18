# Task: Greenfield Autonomous Task-Management Web Application

## Requirements
Build a lightweight, dependency-free task-management web application from scratch:

1. **Backend**:
   - Python standard-library HTTP server (e.g. `http.server`, `urllib`, `json`).
   - `GET /api/tasks`: returns JSON array of tasks (e.g. `[{"id": "...", "title": "...", "done": bool}]`).
   - `POST /api/tasks`: accepts JSON `{"title": "..."}` and creates a new task, returning JSON with status 201 or 200.

2. **Frontend UI**:
   - Static HTML / Vanilla JS / CSS interface (e.g. `index.html` or static assets).
   - Allows viewing task list and creating new tasks via the API.

3. **Verification**:
   - Include standalone unit tests validating the HTTP API endpoints.
   - Zero external library dependencies (standard library only).

Verify implementation by running:
`["python3", "-m", "unittest", "discover", "-s", ".", "-p", "test_*.py"]`
