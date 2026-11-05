import requests
from requests.auth import HTTPBasicAuth

class APIClient:
    def __init__(self, base_url, username, password):
        self.base_url = base_url
        self.auth = HTTPBasicAuth(username, password)

    def create_client(self, ip, locale, platform):
        return requests.post(f"{self.base_url}/private/api/v3/register/client",
                             json={"ip": ip, "locale": locale, "platform": platform},
                             auth=self.auth)

    def delete_client(self, id):
        return requests.delete(f"{self.base_url}/private/api/v3/discard/client/{id}", auth=self.auth)

    def get_all_clients(self):
        return requests.get(f"{self.base_url}/private/api/v3/browse/client", auth=self.auth)

    def get_client_client_by_id(self, id):
        return requests.get(f"{self.base_url}/private/api/v3/show/client", params={"id": id}, auth=self.auth)

    def create_task(self, payload, client, tags, state):
        return requests.post(f"{self.base_url}/private/api/v3/register/task",
                             json={"payload": payload, "client": client, "tags": tags, "state": state},
                             auth=self.auth)

    def delete_task(self, id):
        return requests.delete(f"{self.base_url}/private/api/v3/discard/task/{id}", auth=self.auth)

    def get_all_tasks(self, client):
        return requests.get(f"{self.base_url}/private/api/v3/browse/task/{client}", auth=self.auth)

    def get_task_by_id(self, id):
        return requests.get(f"{self.base_url}/private/api/v3/show/task", params={"id": id}, auth=self.auth)

    def get_all_responses(self, task):
        return requests.get(f"{self.base_url}/private/api/v3/browse/response/{task}", auth=self.auth)

    def get_response_by_id(self, id):
        return requests.get(f"{self.base_url}/private/api/v3/show/response", params={"id": id}, auth=self.auth)

    def report(self):
        return requests.get(f"{self.base_url}/private/api/v3/browse/report", auth=self.auth)