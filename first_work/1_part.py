import time


class DataLayer:
    def __init__(self):
        self.clients = []
        self.tasks = []
        self.responses = []

        self.client_id = 1
        self.task_id = 1
        self.response_id = 1
    def create_client(self, ip: str,
                      locale: str,
                      platform: str):
        client = {
            "id": self.client_id,
            "datetime": int(time.time()),
            "ip": ip,
            "locale": locale,
            "platform": platform
        }
        self.clients.append(client)
        self.client_id += 1
        return "Запись нового клиента создана"

    def delete_client(self, client_id: int):
        if client_id <= len(self.clients):
            self.clients = self.clients[:client_id] + self.clients[client_id + 1:]
            return f"Запись с client_id = {client_id} удалена"
        return "Такого client_id не существует!"

    def get_all_clients(self):
        return self.clients

    def get_client_by_id(self, client_id: int):
        return self.clients[client_id]


    def create_task(self, payload: str,
                    client: int, tags: str,
                    state: str):
        task = {
            "id": self.task_id,
            "datetime": int(time.time()),
            "payload": payload,
            "client": client,
            "tags": tags,
            "state": state
        }
        self.tasks.append(task)
        self.task_id += 1
        return "Запись новой задачи создана"

    def delete_task(self, task_id: int):
        if task_id <= len(self.tasks):
            self.tasks = self.tasks[:task_id] + self.clients[task_id + 1:]
            return f"Запись с task_id = {task_id} удалена"
        return "Такого task_id не существует!"

    def get_all_tasks(self):
        return self.tasks

    def get_task_by_id(self, task_id: int):
        return self.tasks[task_id]


    def create_response(self, output: str,
                        state: str,
                        failure: str, task: int,
                        cache_hit: int, duration: int):
        response = {
            "id": self.response_id,
            "datetime": int(time.time()),
            "output": output,
            "state": state,
            "failure": failure,
            "task": task,
            "cache_hit": cache_hit,
            "duration": duration
        }
        self.responses.append(response)
        self.response_id += 1
        return "Запись нового ответа создана"

    def delete_response(self, response_id: int):
        if response_id <= len(self.responses):
            self.responses = self.responses[:response_id] + self.responses[response_id + 1:]
            return f"Запись с response_id = {response_id} удалена"
        return "Такого response_id не существует!"

    def get_all_responses(self):
        return self.responses

    def get_response_by_id(self, response_id: int):
        return self.responses[response_id]

    def query_right_join(self):
        filtered_tasks = [t for t in self.tasks if t["datetime"] > (int(time.time()) - (8 * 60))] # > (8 * 60)
        result = []
        result_tasks = []
        result_clients = []
        for t in filtered_tasks:
            for client in self.clients:
                if client['id'] == t['client']:
                    result_clients.append(client)

        result_tasks = [t for t in filtered_tasks]

        result.append(result_clients)
        result.append(result_tasks)
        return result

dataLayer = DataLayer()

dataLayer.create_client(ip="192.168.127.12", locale = "Russia", platform= "Mess")
dataLayer.create_client(ip="192.168.111.00", locale = "Tajikistan", platform= "Mess")
dataLayer.create_client(ip="192.168.100.01", locale = "USA", platform= "Mess")

dataLayer.create_task(payload = "server", client=1, tags="important", state="work")
dataLayer.create_task(payload = "server", client=2, tags="sensitive", state="success")
dataLayer.create_task(payload = "server", client=5, tags="disturb", state="unsuccess")

dataLayer.create_response(output = "Session success", state = "finished", failure = "No", task = 1, cache_hit = 0, duration = 0)

# dataLayer.clients = [{'id': 1, 'datetime': 1790522162, 'ip': '192.168.127.12', 'locale': 'Russia', 'platform': 'Mess'}, {'id': 2, 'datetime': 1790522162, 'ip': '192.168.111.00', 'locale': 'Tajikistan', 'platform': 'Mess'}, {'id': 3, 'datetime': 1790522162, 'ip': '192.168.100.01', 'locale': 'USA', 'platform': 'Mess'}]
# dataLayer.tasks = [{'id': 1, 'datetime': 1790522162, 'payload': 'server', 'client': 1, 'tags': 'important', 'state': 'work'}, {'id': 2, 'datetime': 1790522162, 'payload': 'server', 'client': 2, 'tags': 'sensitive', 'state': 'success'}, {'id': 3, 'datetime': 1790522162, 'payload': 'server', 'client': 5, 'tags': 'disturb', 'state': 'unsuccess'}]
# dataLayer.responses = [{'id': 1, 'datetime': 1790522162, 'output': 'Session success', 'state': 'finished', 'failure': 'No', 'task': 1, 'cache_hit': 0, 'duration': 0}]

print(dataLayer.query_right_join())