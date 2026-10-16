from datetime import datetime, timedelta
from fastapi import FastAPI, Form, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from prometheus_client import Counter, Gauge, generate_latest, CONTENT_TYPE_LATEST
import os
import psutil

app = FastAPI(title="Lab Monitoring App")

# Метрики Prometheus
REQUEST_COUNT = Counter('app_requests_total', 'Total HTTP Requests')
VISIT_COUNT = Counter('app_visits_total', 'Total page visits')
CPU_GAUGE = Gauge('app_cpu_usage_percent', 'Current CPU usage percent')
MEMORY_GAUGE = Gauge('app_memory_usage_bytes', 'Current Memory usage in bytes')

# Временное хранилище в памяти (чтобы можно было редактировать/добавлять данные)
notes = ["Привет! Это первая заметка в системе."]


@app.get("/", response_class=HTMLResponse)
def read_root(request: Request):
    REQUEST_COUNT.inc()
    VISIT_COUNT.inc()

    # Обновляем метрики ресурсов
    CPU_GAUGE.set(psutil.cpu_percent())
    MEMORY_GAUGE.set(psutil.virtual_memory().used)

    notes_html = "".join([f"<li>{note}</li>" for note in notes])

    html_content = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <title>Системное ПО - Лабораторная</title>
        <meta charset="utf-8">
        <style>
            body {{ font-family: Arial, sans-serif; margin: 40px; background: #f4f4f9; color: #333; }}
            .card {{ background: white; padding: 20px; border-radius: 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); margin-bottom: 20px; }}
            input[type="text"] {{ width: 70%; padding: 8px; margin-right: 10px; }}
            button {{ padding: 8px 15px; background: #007BFF; color: white; border: none; border-radius: 4px; cursor: pointer; }}
            button:hover {{ background: #0056b3; }}
        </style>
    </head>
    <body>
        <h1>🚀 Мониторинг и управление приложением</h1>

        <div class="card">
            <h3>📝 Редактирование данных (Добавить заметку)</h3>
            <form action="/add" method="post">
                <input type="text" name="note" placeholder="Введите текст заметки..." required>
                <button type="submit">Добавить</button>
            </form>
            <h3>Список заметок:</h3>
            <ul>{notes_html}</ul>
        </div>

        <div class="card">
            <h3>📊 Ссылки на мониторинг</h3>
            <p><a href="/metrics" target="_blank">Метрики Prometheus (Ресурсы, посещения)</a></p>
            <p><a href="/health" target="_blank">Health Check (/health)</a></p>
        </div>
    </body>
    </html>
    """
    return HTMLResponse(content=html_content)


@app.post("/add")
def add_note(note: str = Form(...)):
    notes.append(note)
    return RedirectResponse(url="/", status_code=303)


@app.get("/health")
def health_check():
    return {"status": "healthy", "timestamp": datetime.now().isoformat()}


@app.get("/metrics")
def metrics():
    # Обновляем системные метрики перед отдачей
    CPU_GAUGE.set(psutil.cpu_percent())
    MEMORY_GAUGE.set(psutil.virtual_memory().used)
    return HTMLResponse(content=generate_latest(), media_type=CONTENT_TYPE_LATEST)