import sys
import time
import subprocess
import json
import os
import base64
from flask import Flask, request, jsonify, abort
from flask_httpauth import HTTPBasicAuth

current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.abspath(os.path.join(current_dir, '..', '..'))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

from src.first_work.main import DataLayer

app = Flask(__name__)
auth = HTTPBasicAuth()
DB_FILE = 'db.json'

_BASE_DIR = os.path.dirname(os.path.abspath(__file__))
CONVERTER_PATH = os.path.join(_BASE_DIR, "converter.py")

class FileDB(DataLayer):
    def __init__(self):
        super().__init__()
        self._load()

    def _load(self):
        if os.path.exists(DB_FILE):
            with open(DB_FILE, 'r', encoding='utf-8') as f:
                state = json.load(f)
                self.clients = state.get("clients", [])
                self.tasks = state.get("tasks", [])
                self.responses = state.get("responses", [])
                self.client_id = state.get("client_id", 1)
                self.task_id = state.get("task_id", 1)
                self.response_id = state.get("response_id", 1)
        else:
            self._save()

    def _save(self):
        state = {
            "clients": self.clients,
            "tasks": self.tasks,
            "responses": self.responses,
            "client_id": self.client_id,
            "task_id": self.task_id,
            "response_id": self.response_id
        }
        with open(DB_FILE, 'w', encoding='utf-8') as f:
            json.dump(state, f, indent=2, ensure_ascii=False)

    def create_client(self, ip, locale, platform):
        res = super().create_client(ip, locale, platform)
        self._save()
        return res

    def delete_client(self, n_client_id):
        res = super().delete_client(n_client_id)
        self._save()
        return res

    def create_task(self, payload, client, tags, state):
        res = super().create_task(payload, client, tags, state)
        self._save()
        return res

    def delete_task(self, n_task_id):
        res = super().delete_task(n_task_id)
        self._save()
        return res

    def create_response(self, output, state, failure, task, cache_hit, duration):
        res = super().create_response(output, state, failure, task, cache_hit, duration)
        self._save()
        return res

db = FileDB()

@auth.verify_password
def verify_password(username, password):
    return (username == app.config.get('USERNAME') and
            password == app.config.get('PASSWORD'))


@app.route('/private/api/v3/register/client', methods=['POST'])
@auth.login_required
def create_client():
    data = request.json
    if not data or not all(k in data for k in ('ip', 'locale', 'platform')):
        abort(400, description="Missing required fields")

    c = db.create_client(data['ip'], data['locale'], data['platform'])
    return jsonify(c), 200

@app.route('/private/api/v3/discard/client/<int:id>', methods=['DELETE'])
@auth.login_required
def delete_client(id):
    res = db.delete_client(id)
    if isinstance(res, str):
        abort(404, description=res)
    return jsonify({"status": "deleted", "id": res}), 200


@app.route('/private/api/v3/browse/client', methods=['GET'])
@auth.login_required
def get_all_clients():
    return jsonify(db.get_all_clients()), 200


@app.route('/private/api/v3/show/client', methods=['GET'])
@auth.login_required
def get_client_by_id():
    cid = request.args.get('id', type=int)
    if cid is None: abort(400, description="Missing id")

    # Используем ваш метод
    c = db.get_client_by_id(cid)
    if isinstance(c, str):  # Если вернулась строка, значит не найден
        abort(404, description=c)
    return jsonify(c), 200

@app.route('/private/api/v3/register/task', methods=['POST'])
@auth.login_required
def create_task():
    data = request.json
    if not data or not all(k in data for k in ('payload', 'client', 'tags', 'state')):
        abort(400, description="Missing required fields")

    # Используем ваш метод
    task = db.create_task(data['payload'], data['client'], data['tags'], data['state'])

    # Вызов конвертера (первый этап)
    if app.config.get('TESTING'):
        output = "Mocked HTML"
        state = "success"
        failure = ""
    else:
        try:
            docx_bytes = base64.b64decode(data['payload'])
            process = subprocess.run(
                [sys.executable, CONVERTER_PATH],
                input=docx_bytes,  # 👈 БАЙТЫ, а НЕ base64-строка!
                capture_output=True,
                check=True,
            )
            output = process.stdout
            state = "success"
            failure = ""
            os.makedirs("outputs", exist_ok=True)
            with open(f"outputs/task_{task['id']}.html", "w", encoding="utf-8") as f:
                f.write(output)
        except Exception as e:  # <-- Ловим ЛЮБЫЕ ошибки (включая FileNotFoundError)
            output = ""
            state = "failed"
            failure = str(e)

    # Создаем ответ через ваш метод
    db.create_response(output, state, failure, task['id'], 0, 1)
    return jsonify(task), 200


@app.route('/private/api/v3/discard/task/<int:id>', methods=['DELETE'])
@auth.login_required
def delete_task(id):
    res = db.delete_task(id)
    if isinstance(res, str):
        abort(404, description=res)
    return jsonify({"status": "deleted", "id": res}), 200


@app.route('/private/api/v3/browse/task/<int:client>', methods=['GET'])
@auth.login_required
def get_all_tasks(client):
    tasks = [t for t in db.get_all_tasks() if t["client"] == client]
    return jsonify(tasks), 200


@app.route('/private/api/v3/show/task', methods=['GET'])
@auth.login_required
def get_task_by_id():
    tid = request.args.get('id', type=int)
    if tid is None: abort(400, description="Missing id")

    t = db.get_task_by_id(tid)
    if isinstance(t, str):
        abort(404, description=t)
    return jsonify(t), 200


@app.route('/private/api/v3/browse/response/<int:task>', methods=['GET'])
@auth.login_required
def get_all_responses(task):
    responses = [r for r in db.get_all_responses() if r["task"] == task]
    return jsonify(responses), 200


@app.route('/private/api/v3/show/response', methods=['GET'])
@auth.login_required
def get_response_by_id():
    rid = request.args.get('id', type=int)
    if rid is None: abort(400, description="Missing id")

    r = db.get_response_by_id(rid)
    if isinstance(r, str):
        abort(404, description=r)
    return jsonify(r), 200


@app.route('/private/api/v3/browse/report', methods=['GET'])
@auth.login_required
def report():
    return jsonify(db.query_right_join()), 200


if __name__ == '__main__':
    username = sys.argv[1] if len(sys.argv) > 1 else 'admin'
    password = sys.argv[2] if len(sys.argv) > 2 else 'secret'
    test_mode = len(sys.argv) > 3 and sys.argv[3] == 'test'

    app.config['USERNAME'] = username
    app.config['PASSWORD'] = password
    app.config['TESTING'] = test_mode

    app.run(host='127.0.0.1', port=5012)