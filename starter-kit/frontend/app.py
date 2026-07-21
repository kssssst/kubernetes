import os

import requests
from flask import Flask, Response, jsonify, render_template_string, request

app = Flask(__name__)

BACKEND_URL = os.getenv("BACKEND_URL", "http://backend:8080")

PAGE = """
<!doctype html>
<html lang="ru">
<head>
    <meta charset="UTF-8">
    <title>Kubernetes Homework</title>
    <style>
        body {
            font-family: Arial, sans-serif;
            max-width: 800px;
            margin: 60px auto;
            padding: 20px;
        }

        button {
            padding: 10px 20px;
            cursor: pointer;
        }

        .box {
            border: 1px solid #ccc;
            padding: 20px;
            margin-top: 20px;
        }
    </style>
</head>

<body>

<h1>Kubernetes Homework</h1>

<div class="box">
    <p>Backend version: <strong id="version">loading...</strong></p>
    <p>Persistent counter: <strong id="counter">loading...</strong></p>

    <button onclick="incrementCounter()">
        Increment counter
    </button>
</div>

<script>

async function refresh() {

    const versionResponse = await fetch('/api/version');
    const versionData = await versionResponse.json();

    document.getElementById('version').textContent =
        versionData.version;

    const counterResponse = await fetch('/api/counter');
    const counterData = await counterResponse.json();

    document.getElementById('counter').textContent =
        counterData.value;
}

async function incrementCounter() {

    await fetch('/api/counter', {
        method: 'POST'
    });

    await refresh();
}

refresh();

</script>

</body>
</html>
"""


@app.get("/")
def index():
    return render_template_string(PAGE)


@app.get("/healthz")
def health():
    return jsonify(status="ok")


@app.route("/api/<path:path>", methods=["GET", "POST", "PUT", "DELETE"])
def proxy(path):
    target = f"{BACKEND_URL}/api/{path}"

    response = requests.request(
        method=request.method,
        url=target,
        data=request.get_data(),
        headers={
            "Content-Type": request.headers.get(
                "Content-Type",
                "application/json",
            )
        },
        timeout=5,
    )

    return Response(
        response.content,
        status=response.status_code,
        content_type=response.headers.get(
            "Content-Type",
            "application/json",
        ),
    )


