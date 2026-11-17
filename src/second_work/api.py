import sys
import subprocess
import json
import os
from db_sqlite import SQLiteDB
import base64
from flask import Flask, request, jsonify, abort
from flask_httpauth import HTTPBasicAuth
from werkzeug.exceptions import HTTPException

current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.abspath(os.path.join(current_dir, "..", ".."))
if project_root not in sys.path:
    sys.path.insert(0, project_root)


app = Flask(__name__)
auth = HTTPBasicAuth()
db = SQLiteDB("app.db")

_BASE_DIR = os.path.dirname(os.path.abspath(__file__))
CONVERTER_PATH = os.path.join(_BASE_DIR, "converter.py")
ARG_USERNAME = 1
ARG_PASSWORD = 2
ARG_TEST_MODE = 3


@app.errorhandler(HTTPException)
def handle_exception(e):
    response = e.get_response()
    response.data = json.dumps(
        {
            "code": e.code,
            "name": e.name,
            "description": e.description,
        }
    )
    response.content_type = "application/json"
    return response


@auth.verify_password
def verify_password(username, password):
    return username == app.config.get("USERNAME") and password == app.config.get(
        "PASSWORD"
    )


@app.route("/private/api/v3/register/client", methods=["POST"])
@auth.login_required
def create_client():
    data = request.json
    if not data or not all(k in data for k in ("ip", "locale", "platform")):
        abort(400, description="Missing required fields")

    c = db.create_client(data["ip"], data["locale"], data["platform"])
    return jsonify(c), 200


@app.route("/private/api/v3/discard/client/<int:id>", methods=["DELETE"])
@auth.login_required
def delete_client(id):
    res = db.delete_client(id)
    if isinstance(res, str):
        abort(404, description=res)
    return jsonify({"status": "deleted", "id": res}), 200


@app.route("/private/api/v3/browse/client", methods=["GET"])
@auth.login_required
def get_all_clients():
    return jsonify(db.get_all_clients()), 200


@app.route("/private/api/v3/show/client", methods=["GET"])
@auth.login_required
def get_client_by_id():
    cid = request.args.get("id", type=int)
    if cid is None:
        abort(400, description="Missing id")

    c = db.get_client_by_id(cid)
    if isinstance(c, str):
        abort(404, description=c)
    return jsonify(c), 200


@app.route("/private/api/v3/register/task", methods=["POST"])
@auth.login_required
def create_task():
    data = request.json
    if not data or not all(k in data for k in ("payload", "client", "tags", "state")):
        abort(400, description="Missing required fields")

    task = db.create_task(data["payload"], data["client"], data["tags"], data["state"])

    if app.config.get("TESTING"):
        output = "Mocked HTML"
        state = "success"
        failure = ""
    else:
        try:
            docx_bytes = base64.b64decode(data["payload"], validate=True)
            process = subprocess.run(
                [sys.executable, CONVERTER_PATH],
                input=docx_bytes,
                capture_output=True,
                check=True,
            )
            output = process.stdout.decode("utf-8", errors="ignore")
            state = "success"
            failure = ""

            os.makedirs("outputs", exist_ok=True)
            with open(f"outputs/task_{task['id']}.html", "w", encoding="utf-8") as f:
                f.write(output)

        except Exception as e:
            output = ""
            state = "failed"
            failure = str(e)

    db.create_response(output, state, failure, task["id"], 0, 1)
    return jsonify(task), 200


@app.route("/private/api/v3/discard/task/<int:id>", methods=["DELETE"])
@auth.login_required
def delete_task(id):
    res = db.delete_task(id)
    if isinstance(res, str):
        abort(404, description=res)
    return jsonify({"status": "deleted", "id": res}), 200


@app.route("/private/api/v3/browse/task/<int:client>", methods=["GET"])
@auth.login_required
def get_all_tasks(client):
    tasks = [t for t in db.get_all_tasks() if t["client"] == client]
    return jsonify(tasks), 200


@app.route("/private/api/v3/show/task", methods=["GET"])
@auth.login_required
def get_task_by_id():
    tid = request.args.get("id", type=int)
    if tid is None:
        abort(400, description="Missing id")

    t = db.get_task_by_id(tid)
    if isinstance(t, str):
        abort(404, description=t)
    return jsonify(t), 200


@app.route("/private/api/v3/browse/response/<int:task>", methods=["GET"])
@auth.login_required
def get_all_responses(task):
    responses = [r for r in db.get_all_responses() if r["task"] == task]
    return jsonify(responses), 200


@app.route("/private/api/v3/show/response", methods=["GET"])
@auth.login_required
def get_response_by_id():
    rid = request.args.get("id", type=int)
    if rid is None:
        abort(400, description="Missing id")

    r = db.get_response_by_id(rid)
    if isinstance(r, str):
        abort(404, description=r)
    return jsonify(r), 200


@app.route("/private/api/v3/browse/report", methods=["GET"])
@auth.login_required
def report():
    return jsonify(db.query_report()), 200


if __name__ == "__main__":
    if len(sys.argv) > ARG_USERNAME:
        username = sys.argv[ARG_USERNAME]
    else:
        username = "admin"

    if len(sys.argv) > ARG_PASSWORD:
        password = sys.argv[ARG_PASSWORD]
    else:
        password = "secret"

    test_mode = len(sys.argv) > ARG_TEST_MODE and sys.argv[ARG_TEST_MODE] == "test"

    app.config["USERNAME"] = username
    app.config["PASSWORD"] = password
    app.config["TESTING"] = test_mode

    app.run(host="127.0.0.1", port=5003)
