#!/usr/bin/env bash
# CodeCraftHub - curl tests for every endpoint.
# Start the server first:  python app.py
BASE="http://localhost:5000/api/courses"

echo "== 1. CREATE (POST) =="
curl -s -w "\nHTTP %{http_code}\n\n" -X POST "$BASE" \
  -H "Content-Type: application/json" \
  -d '{"name":"Python Basics","description":"Learn variables, loops and functions","target_date":"2026-12-31","status":"Not Started"}'

curl -s -w "\nHTTP %{http_code}\n\n" -X POST "$BASE" \
  -H "Content-Type: application/json" \
  -d '{"name":"Flask REST APIs","description":"Build CRUD APIs with Flask","target_date":"2027-01-15","status":"In Progress"}'

echo "== 2. READ ALL (GET) =="
curl -s -w "\nHTTP %{http_code}\n\n" "$BASE"

echo "== 3. READ ONE (GET) =="
curl -s -w "\nHTTP %{http_code}\n\n" "$BASE/1"

echo "== 4. UPDATE (PUT) =="
curl -s -w "\nHTTP %{http_code}\n\n" -X PUT "$BASE/1" \
  -H "Content-Type: application/json" \
  -d '{"status":"Completed"}'

echo "== 5. STATS & SEARCH (optional) =="
curl -s -w "\nHTTP %{http_code}\n\n" "$BASE/stats"
curl -s -w "\nHTTP %{http_code}\n\n" "$BASE?search=flask"

echo "== 6. DELETE =="
curl -s -w "\nHTTP %{http_code}\n\n" -X DELETE "$BASE/2"

echo "== 7. ERROR CASES =="
echo "-- invalid status (expect 400)"
curl -s -w "\nHTTP %{http_code}\n\n" -X POST "$BASE" \
  -H "Content-Type: application/json" \
  -d '{"name":"Bad","description":"x","target_date":"2026-12-31","status":"Done"}'
echo "-- missing fields (expect 400)"
curl -s -w "\nHTTP %{http_code}\n\n" -X POST "$BASE" \
  -H "Content-Type: application/json" -d '{"name":"Only name"}'
echo "-- bad date (expect 400)"
curl -s -w "\nHTTP %{http_code}\n\n" -X POST "$BASE" \
  -H "Content-Type: application/json" \
  -d '{"name":"x","description":"y","target_date":"31-12-2026","status":"In Progress"}'
echo "-- not found (expect 404)"
curl -s -w "\nHTTP %{http_code}\n\n" "$BASE/999"
