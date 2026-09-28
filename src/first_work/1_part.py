import logging
import sys
import time
import socket


logging.basicConfig(
    filename='journal.log',
    level=logging.INFO,
    format='%(asctime)s - %(message)s',
    encoding = 'utf-8'
)

class DataLayer:
    def __init__(self):
        self.clients = []
        self.tasks = []
        self.responses = []

        self.client_id = 1
        self.task_id = 1
        self.response_id = 1

    def create_client(self, ip: str, locale: str, platform: str):
        client = {
            "id": self.client_id,
            "datetime": int(time.time()),
            "ip": ip,
            "locale": locale,
            "platform": platform,
        }
        self.clients.append(client)
        self.client_id += 1
        return client

    def delete_client(self, n_client_id: int):
        if n_client_id in [client["id"] for client in self.clients]:
            self.clients = [c for c in self.clients if c["id"] != n_client_id]
            return n_client_id
        return "Такого id у клиентов не существует!"

    def get_all_clients(self):
        return self.clients

    def get_client_by_id(self, new_client_id: int):
        if new_client_id in [client["id"] for client in self.clients]:
            return next(c for c in self.clients if c["id"] == new_client_id)
        return "Такого id у клиентов не существует!"

    def create_task(self, payload: str, client: int, tags: str, state: str):
        task = {
            "id": self.task_id,
            "datetime": int(time.time()),
            "payload": payload,
            "client": client,
            "tags": tags,
            "state": state,
        }
        self.tasks.append(task)
        self.task_id += 1
        return task

    def delete_task(self, n_task_id: int):
        if n_task_id in [task["id"] for task in self.tasks]:
            self.tasks = [t for t in self.tasks if t["id"] != n_task_id]
            return n_task_id
        return "Такого task_id не существует!"

    def get_all_tasks(self):
        return self.tasks

    def get_task_by_id(self, n_task_id: int):
        if n_task_id in [task["id"] for task in self.tasks]:
            return next(t for t in self.tasks if t["id"] == n_task_id)
        return "Такого id у задач не существует!"

    def create_response(
        self,
        output: str,
        state: str,
        failure: str,
        task: int,
        cache_hit: int,
        duration: int,
    ):
        response = {
            "id": self.response_id,
            "datetime": int(time.time()),
            "output": output,
            "state": state,
            "failure": failure,
            "task": task,
            "cache_hit": cache_hit,
            "duration": duration,
        }
        self.responses.append(response)
        self.response_id += 1
        return response

    def delete_response(self, new_response_id: int):
        if new_response_id in [response["id"] for response in self.responses]:
            self.responses = [
                response
                for response in self.responses
                if response["id"] != new_response_id
            ]
            return new_response_id
        return "Такого response_id не существует!"

    def get_all_responses(self):
        return self.responses

    def get_response_by_id(self, new_response_id: int):
        if new_response_id in [response["id"] for response in self.responses]:
            return next(
                response
                for response in self.responses
                if response["id"] == new_response_id
            )
        return "Такого id у ответов не существует!"

    def query_right_join(self):
        curr_time = int(time.time())
        filtered_tasks = [
            t for t in self.tasks if t["datetime"] > (curr_time - (8 * 60))
        ]  # > (8 * 60)
        result = []
        result_clients = []
        for t in filtered_tasks:
            for client in self.clients:
                if client["id"] == t["client"]:
                    result_clients.append(client)

        result_tasks = [t for t in filtered_tasks]

        result.append(result_clients)
        result.append(result_tasks)
        return result


class Repl:
    def __init__(self):
        self.dataLayer = DataLayer()
        self.commands = {
            "add_client": self.add_client_repl,
            "del_client": self.del_client_repl,
            "get_all_clients": self.get_all_clients_repl,
            "get_client_by_id": self.get_client_by_id_repl,
            "add_task": self.add_task_repl,
            "del_task": self.del_task_repl,
            "get_all_tasks": self.get_all_tasks_repl,
            "get_task_by_id": self.get_task_by_id_repl,
            "add_response": self.add_response_repl,
            "del_response": self.del_response_repl,
            "get_all_responses": self.get_all_responses_repl,
            "get_response_by_id": self.get_response_by_id_repl,
            "query_right_join": self.query_right_join_repl,
            "test_data": self.test_data,
            "exit": self.exit,
        }

    def add_client_repl(self, args):
        if len(args) != 3:
            raise ValueError(
                "Неверное количество атрибутов для создания записи клиента"
            )

        ip, locale, platform = args[0], args[1], args[2]
        client = self.dataLayer.create_client(ip, locale, platform)
        return f"Клиент создан: {client}"

    def del_client_repl(self, args):
        if len(args) != 1:
            m = "Для удаления клиента нужно передать только id клиента"
            raise ValueError(m)

        id = int(args[0])
        client = self.dataLayer.delete_client(id)
        return f"Удален клиент с id: {client}"

    def get_all_clients_repl(self, args):
        if len(args) != 0:
            raise ValueError("Команда не принимает аргументов")

        return self.dataLayer.get_all_clients()

    def get_client_by_id_repl(self, args):
        if len(args) != 1:
            m = "Для получения записи клиента нужно указать только его id"
            raise ValueError(m)
        id = int(args[0])
        return self.dataLayer.get_client_by_id(id)

    def add_task_repl(self, args):
        if len(args) != 4:
            m = "Неверное количество атрибутов для создания записи задачи"
            raise ValueError(m)

        payload, client, tags, state = args[0], args[1], args[2], args[3]
        task = self.dataLayer.create_task(payload, client, tags, state)
        return f"Задача создана: {task}"

    def del_task_repl(self, args):
        if len(args) != 1:
            m = "Для удаления задачи нужно передать только id задачи"
            raise ValueError(m)

        id = int(args[0])
        task = self.dataLayer.delete_task(id)
        return f"Удалена задача с id: {task}"

    def get_all_tasks_repl(self, args):
        if len(args) != 0:
            raise ValueError("Команда не принимает аргументов")

        return self.dataLayer.get_all_tasks()

    def get_task_by_id_repl(self, args):
        if len(args) != 1:
            m = "Для получения записи задачи нужно указать только её id"
            raise ValueError(m)

        id = int(args[0])
        return self.dataLayer.get_task_by_id(id)

    def add_response_repl(self, args):
        if len(args) != 6:
            m = "Неверное количество атрибутов для создания записи ответа"
            raise ValueError(m)

        output, state, failure, task, cache_hit, duration = args
        response = self.dataLayer.create_response(
            output, state, failure, task, cache_hit, duration
        )
        return f"Ответ создан: {response}"

    def del_response_repl(self, args):
        if len(args) != 1:
            m = "Для удаления ответа нужно передать только id ответа"
            raise ValueError(m)

        id = int(args[0])
        response = self.dataLayer.delete_response(id)
        return f"Удален ответ с id: {response}"

    def get_all_responses_repl(self, args):
        if len(args) != 0:
            raise ValueError("Команда не принимает аргументов")

        return self.dataLayer.get_all_responses()

    def get_response_by_id_repl(self, args):
        if len(args) != 1:
            m = "Для получения записи ответа нужно указать только его id"
            raise ValueError(m)

        id = int(args[0])
        return self.dataLayer.get_response_by_id(id)

    def query_right_join_repl(self, args):
        if len(args) != 0:
            raise ValueError("Команда не принимает аргументов")

        return self.dataLayer.query_right_join()

    def exit(self, args):
        if len(args) != 0:
            raise ValueError("Команда не принимает аргументов")

        sys.exit(0)

    def test_data(self, args):
        if len(args) != 0:
            raise ValueError("Команда не принимает аргументов")

        self.dataLayer.create_client(
            ip="192.168.127.12", locale="Russia", platform="Mess"
        )
        self.dataLayer.create_client(
            ip="192.168.111.00", locale="Tajikistan", platform="Mess"
        )
        self.dataLayer.create_client(
            ip="192.168.100.01", locale="Armenia", platform="Mess"
        )

        self.dataLayer.create_task(
            payload="server", client=1, tags="important", state="work"
        )
        self.dataLayer.create_task(
            payload="server", client=2, tags="sensitive", state="success"
        )
        self.dataLayer.create_task(
            payload="server", client=5, tags="disturb", state="unsuccess"
        )

        self.dataLayer.create_response(
            output="Session success",
            state="finished",
            failure="No",
            task=1,
            cache_hit=0,
            duration=0,
        )

        return "Клиенты, задачи и ответы заполнены тестовыми данными"

    def run(self):
        while True:
            try:
                user_input = input("db> ").strip()
                if not user_input:
                    continue

                parts = user_input.split()
                cmd = parts[0].lower()
                args = parts[1:]

                if cmd in self.commands:
                    print(self.commands[cmd](args))
                else:
                    print("Такой команды нет!")
            except Exception as e:
                print(e)

class RPCServer:
    def __init__(self, host='127.0.0.1', port=8080):
        self.data = DataLayer()
        self.host = host
        self.port = port
        self.ops = {
            1: self.data.create_client,
            2: self.data.delete_client,
            3: self.data.get_all_clients,
            4: self.data.get_client_by_id,
            5: self.data.create_task,
            6: self.data.delete_task,
            7: self.data.get_all_tasks,
            8: self.data.get_task_by_id,
            9: self.data.create_response,
            10: self.data.delete_response,
            11: self.data.get_all_responses,
            12: self.data.get_response_by_id,
            13: self.data.query_right_join,
        }

        def recv_exact(self, sock, n):
            data = b''
            while len(data) < n:
                chuck = sock.recv(n - len(data))
                if not chuck:
                    return None
                data += chuck
            return data

        def start(self):
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            s.bind((self.host, self.port))
            s.listen()
            while True:
                conn, addr = s.accept()
                self.handle(conn)

        def handle(self, conn):
            opcode_b = self.recv_exact(conn, 2)
            if not opcode_b:
                break
            opcode = int.from_bytes(opcode_b, "little")

            size_b = self.recv_exact(conn, 4)
            size = int.from_bytes(size_b, "little")

            body_b = self.recv_exact(conn, size)
            args = ...
            try:
                result = self.ops[opcode](*args)
                resp_xml = ...
                status = "OK"
            except Exception as e:
                resp_xml = ...
                status = "ERROR"

            logging.info(f'opcode={opcode} status={status} response={resp_xml}')
            resp_b = resp_xml.encode()


if __name__ == "__main__":
    repl = Repl()
    repl.run()
