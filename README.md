# CodeCraftHub – Personalized Learning Platform

CodeCraftHub is a small full-stack app for managing learning courses.

- **Backend:** Python + Flask REST API with full CRUD. Data is stored in `courses.json`, so you don't need a database.
- **Frontend:** a single-file dashboard (`index.html`) generated with Bolt.new / Bolt.diy that calls the API from the browser.

## Project structure

```
codecrafthub/
├── app.py            # Flask API (CRUD, validation, CORS, stats, search)
├── courses.json      # JSON data store (created automatically)
├── requirements.txt  # Flask, flask-cors
├── test_api.sh       # curl tests for every endpoint
├── bolt_prompt.txt   # the prompt used in Bolt to generate the dashboard
├── index.html        # the dashboard UI
└── README.md
```

## Prerequisites

- Python 3.9 or later (`python --version`)
- pip
- Git and curl (`git --version`, `curl --version`)

## Setup and run

```bash
cd codecrafthub
python -m venv venv
source venv/bin/activate          # Windows: venv\Scripts\activate
pip install -r requirements.txt
python app.py
```

The API starts at **http://localhost:5000**. Open `index.html` in your browser while the server is running.

## Course model

| Field         | Type   | Rules                                                |
|---------------|--------|------------------------------------------------------|
| `id`          | int    | Auto-generated, starts at 1                          |
| `name`        | string | Required, non-empty                                  |
| `description` | string | Required, non-empty                                  |
| `target_date` | string | Required, `YYYY-MM-DD`                               |
| `status`      | string | Required: `Not Started`, `In Progress`, `Completed`  |
| `created_at`  | string | Auto-generated ISO timestamp (UTC)                   |

## Endpoints

| Method | Endpoint                 | Description                                  | Success |
|--------|--------------------------|----------------------------------------------|---------|
| GET    | `/api/courses`           | List courses (`?search=` and `?status=` work) | 200     |
| GET    | `/api/courses/<id>`      | Get one course                                | 200     |
| POST   | `/api/courses`           | Create a course (all fields required)         | 201     |
| PUT    | `/api/courses/<id>`      | Update a course (send any fields)             | 200     |
| DELETE | `/api/courses/<id>`      | Delete a course                               | 200     |
| GET    | `/api/courses/stats`     | Total and count per status                    | 200     |

Errors: **400** validation failed, **404** not found, **405** wrong method, **415** body is not JSON, **500** server or file error.

### Response format

```json
{ "success": true, "message": "Course created successfully.", "data": { "id": 1, "...": "..." } }
{ "success": false, "error": "Validation failed.", "details": ["'status' must be one of: ..."] }
```

## Testing with curl

Run all tests with `bash test_api.sh`, or run single requests:

```bash
# Create
curl -X POST http://localhost:5000/api/courses -H "Content-Type: application/json" \
  -d '{"name":"Python Basics","description":"Learn loops","target_date":"2026-12-31","status":"Not Started"}'

# Read all / one
curl http://localhost:5000/api/courses
curl http://localhost:5000/api/courses/1

# Update
curl -X PUT http://localhost:5000/api/courses/1 -H "Content-Type: application/json" \
  -d '{"status":"In Progress"}'

# Delete
curl -X DELETE http://localhost:5000/api/courses/1
```

On Windows PowerShell, use `curl.exe` and escape the inner double quotes, or run the commands in Git Bash.

## CORS

CORS is enabled for `/api/*` through `flask-cors`, so the dashboard can call the API from a browser (including when it is opened as a local file or previewed in Bolt). If `flask-cors` is not installed, `app.py` adds the same headers itself.

## Dashboard (Part 2)

1. Start the backend (`python app.py`).
2. In Bolt.new or Bolt.diy, paste the prompt from `bolt_prompt.txt`. Check that `API_BASE_URL` matches your backend URL.
3. Preview the result, then export or copy the HTML into `index.html` in this folder.
4. Open `index.html` in a browser and test add, edit, delete, search and filter.

Note: the Bolt preview runs in the cloud, so it can't reach `localhost` on your machine. The full end-to-end test happens when you open the saved `index.html` locally.

## Troubleshooting

| Problem | Fix |
|---------|-----|
| `ModuleNotFoundError: flask` | Activate the venv and run `pip install -r requirements.txt` |
| `Address already in use` | Stop the other process on port 5000, or change the port in `app.py` and `API_BASE_URL` |
| Dashboard shows "API offline" | Make sure `python app.py` is running and the URL in `index.html` is correct |
| CORS error in the browser console | Install `flask-cors` and restart the server |
| 415 Unsupported Media Type | Add the header `-H "Content-Type: application/json"` |
| `courses.json` is broken | Replace its contents with `[]` |

## Push to GitHub (optional)

```bash
git init
echo "venv/" > .gitignore && echo "__pycache__/" >> .gitignore
git add . && git commit -m "CodeCraftHub: Flask CRUD API and dashboard"
git branch -M main
git remote add origin https://github.com/<your-username>/CodeCraftHub.git
git push -u origin main
```
