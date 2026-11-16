import unittest
from hypothesis import settings, HealthCheck
from hypothesis.stateful import (
    RuleBasedStateMachine,
    rule,
    initialize,
    run_state_machine_as_test,
)
from client import APIClient
import threading
import time
import os
from api import app

PORT = 5004
BASE_URL = f"http://127.0.0.1:{PORT}"
USER = "admin"
PASS = "secret"


# Запуск Flask в фоне для тестов
def start_server():
    app.config["USERNAME"] = USER
    app.config["PASSWORD"] = PASS
    app.config["TESTING"] = True
    app.run(host="127.0.0.1", port=PORT, use_reloader=False)


class APIStateMachine(RuleBasedStateMachine):
    def __init__(self):
        super().__init__()
        self.client_ids = []
        self.task_ids = []
        self.response_ids = []
        self.api = APIClient(BASE_URL, USER, PASS)

    @rule()
    def create_client(self):
        resp = self.api.create_client("127.0.0.1", "ru", "linux")
        assert resp.status_code == 200
        data = resp.json()
        assert "id" in data
        self.client_ids.append(data["id"])

    @rule()
    def create_task(self):
        if not self.client_ids:
            return
        client_id = self.client_ids[-1]
        resp = self.api.create_task("bW9ja19wYXlsb2Fk",
                                    client_id,
                                    "tag1",
                                    "new")
        assert resp.status_code == 200
        data = resp.json()
        assert "id" in data
        self.task_ids.append(data["id"])

    @rule()
    def get_clients(self):
        resp = self.api.get_all_clients()
        assert resp.status_code == 200
        assert isinstance(resp.json(), list)

    @rule()
    def get_tasks(self):
        if not self.client_ids:
            return
        client_id = self.client_ids[-1]
        resp = self.api.get_all_tasks(client_id)
        assert resp.status_code == 200
        assert isinstance(resp.json(), list)

    @rule()
    def get_report(self):
        resp = self.api.report()
        assert resp.status_code == 200
        assert isinstance(resp.json(), list)

    @rule()
    def delete_task(self):
        if not self.task_ids:
            return
        tid = self.task_ids.pop()
        resp = self.api.delete_task(tid)
        assert resp.status_code == 200

    @rule()
    def delete_client(self):
        if not self.client_ids:
            return
        cid = self.client_ids.pop()
        resp = self.api.delete_client(cid)
        assert resp.status_code == 200


class TestStage2(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        # Очистка БД перед тестами
        if os.path.exists("db.json"):
            os.remove("db.json")
        cls.server_thread = threading.Thread(target=start_server)
        cls.server_thread.daemon = True
        cls.server_thread.start()
        time.sleep(2)  # Ждем запуска сервера

    def test_api_state_machine(self):
        run_state_machine_as_test(
            APIStateMachine,
            settings=settings(
                max_examples=50,
                stateful_step_count=20,
                suppress_health_check=[HealthCheck.too_slow],
            ),
        )
