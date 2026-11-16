import sqlite3
import time


class SQLiteDB:
    def __init__(self, db_path="app.db"):
        self.db_path = db_path
        self._init_db()

    def _get_conn(self):
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn

    def _init_db(self):
        with self._get_conn() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS Client (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    datetime INTEGER,
                    ip TEXT,
                    locale TEXT,
                    platform TEXT
                )
            """)
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS Task (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    datetime INTEGER,
                    payload TEXT,
                    client INTEGER,
                    tags TEXT,
                    state TEXT,
                    FOREIGN KEY(client) REFERENCES Client(id) ON DELETE CASCADE
                )
            """)
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS Response (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    datetime INTEGER,
                    output TEXT,
                    state TEXT,
                    failure TEXT,
                    task INTEGER,
                    cache_hit INTEGER,
                    duration INTEGER,
                    FOREIGN KEY(task) REFERENCES Task(id) ON DELETE CASCADE
                )
            """)
            conn.commit()

    def create_client(self, ip, locale, platform):
        dt = int(time.time())
        with self._get_conn() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "INSERT INTO Client (datetime, ip, locale, platform) "
                "VALUES (?, ?, ?, ?)",
                (dt, ip, locale, platform),
            )
            conn.commit()
            return {
                "id": cursor.lastrowid,
                "datetime": dt,
                "ip": ip,
                "locale": locale,
                "platform": platform,
            }

    def delete_client(self, client_id):
        with self._get_conn() as conn:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM Client WHERE id = ?", (client_id,))
            conn.commit()
            if cursor.rowcount == 0:
                return "Client not found"
            return client_id

    def get_all_clients(self):
        with self._get_conn() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM Client")
            return [dict(row) for row in cursor.fetchall()]

    def get_client_by_id(self, client_id):
        with self._get_conn() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM Client WHERE id = ?", (client_id,))
            row = cursor.fetchone()
            if not row:
                return "Client not found"
            return dict(row)

    def create_task(self, payload, client, tags, state):
        dt = int(time.time())
        with self._get_conn() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "INSERT INTO Task (datetime, payload, client, tags, state) "
                "VALUES (?, ?, ?, ?, ?)",
                (dt, payload, client, tags, state),
            )
            conn.commit()
            return {
                "id": cursor.lastrowid,
                "datetime": dt,
                "payload": payload,
                "client": client,
                "tags": tags,
                "state": state,
            }

    def delete_task(self, task_id):
        with self._get_conn() as conn:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM Task WHERE id = ?", (task_id,))
            conn.commit()
            if cursor.rowcount == 0:
                return "Task not found"
            return task_id

    def get_all_tasks(self):
        with self._get_conn() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM Task")
            return [dict(row) for row in cursor.fetchall()]

    def get_task_by_id(self, task_id):
        with self._get_conn() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM Task WHERE id = ?", (task_id,))
            row = cursor.fetchone()
            if not row:
                return "Task not found"
            return dict(row)

    def create_response(self, output, state, failure,
                        task, cache_hit, duration):
        dt = int(time.time())
        with self._get_conn() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "INSERT INTO Response "
                "(datetime, output, state, failure, "
                "task, cache_hit, duration) "
                "VALUES (?, ?, ?, ?, ?, ?, ?)",
                (dt, output, state, failure, task, cache_hit, duration),
            )
            conn.commit()
            return {
                "id": cursor.lastrowid,
                "datetime": dt,
                "output": output,
                "state": state,
                "failure": failure,
                "task": task,
                "cache_hit": cache_hit,
                "duration": duration,
            }

    def get_all_responses(self):
        with self._get_conn() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM Response")
            return [dict(row) for row in cursor.fetchall()]

    def get_response_by_id(self, response_id):
        with self._get_conn() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM Response WHERE id = ?",
                           (response_id,))
            row = cursor.fetchone()
            if not row:
                return "Response not found"
            return dict(row)

    def query_report(self):
        eight_min_ago = int(time.time()) - 8 * 60
        with self._get_conn() as conn:
            cursor = conn.cursor()
            cursor.execute(
                """
                SELECT c.platform, t.tags
                FROM Client c
                JOIN Task t ON c.id = t.client
                WHERE t.datetime > ?
            """,
                (eight_min_ago,),
            )
            return [dict(row) for row in cursor.fetchall()]
