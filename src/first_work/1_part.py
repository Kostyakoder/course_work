import sys
import time
import socket
import xml.etree.ElementTree as ET


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
            "client": int(client),
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
        ]
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
            "create_client": self.create_client_repl,
            "delete_client": self.delete_client_repl,
            "get_all_clients": self.get_all_clients_repl,
            "get_client_by_id": self.get_client_by_id_repl,
            "create_task": self.create_task_repl,
            "delete_task": self.delete_task_repl,
            "get_all_tasks": self.get_all_tasks_repl,
            "get_task_by_id": self.get_task_by_id_repl,
            "create_response": self.create_response_repl,
            "delete_response": self.delete_response_repl,
            "get_all_responses": self.get_all_responses_repl,
            "get_response_by_id": self.get_response_by_id_repl,
            "query_right_join": self.query_right_join_repl,
            "test_data": self.test_data,
            "help": self.help_repl,
            "exit": self.exit,
        }

    def create_client_repl(self, args):
        n = 3
        if len(args) != n:
            raise ValueError(
                "Неверное количество атрибутов для создания записи клиента"
            )

        ip, locale, platform = args[0], args[1], args[2]
        client = self.dataLayer.create_client(ip, locale, platform)
        return f"Клиент создан: {client}"

    def delete_client_repl(self, args):
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

    def create_task_repl(self, args):
        n = 4
        if len(args) != n:
            m = "Неверное количество атрибутов для создания записи задачи"
            raise ValueError(m)

        payload, client, tags, state = args[0], args[1], args[2], args[3]
        task = self.dataLayer.create_task(payload, client, tags, state)
        return f"Задача создана: {task}"

    def delete_task_repl(self, args):
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

    def create_response_repl(self, args):
        n = 6
        if len(args) != n:
            m = "Неверное количество атрибутов для создания записи ответа"
            raise ValueError(m)

        output, state, failure, task, cache_hit, duration = args
        response = self.dataLayer.create_response(
            output, state, failure, task, cache_hit, duration
        )
        return f"Ответ создан: {response}"

    def delete_response_repl(self, args):
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

    def help_repl(self, args):
        if len(args) != 0:
            raise ValueError("Команда не принимает аргументов")

        return (
            "Пиши str-значения без кавычек !!!\n"
            "Доступные команды:\n"
            "  create_client ip:str locale:str platform:str\n"
            "      Создаёт нового клиента.\n"
            "  delete_client id:int\n"
            "      Удаляет клиента по id.\n"
            "  get_all_clients\n"
            "      Возвращает список всех клиентов.\n"
            "  get_client_by_id id:int\n"
            "      Возвращает клиента по id.\n"
            "  create_task payload:str client:int tags:str state:str\n"
            "      Создаёт новую задачу.\n"
            "  delete_task id:int\n"
            "      Удаляет задачу по id.\n"
            "  get_all_tasks\n"
            "      Возвращает список всех задач.\n"
            "  get_task_by_id id:int\n"
            "      Возвращает задачу по id.\n"
            "  create_response output:str state:str failure:str "
            "           task:int cache_hit:int duration:int\n"
            "      Создаёт новый ответ.\n"
            "  delete_response id:int\n"
            "      Удаляет ответ по id.\n"
            "  get_all_responses\n"
            "      Возвращает список всех ответов.\n"
            "  get_response_by_id id:int\n"
            "      Возвращает ответ по id.\n"
            "  query_right_join\n"
            "      RIGHT JOIN задач и клиентов за последние 8 минут.\n"
            "  test_data\n"
            "      Заполняет хранилище тестовыми данными.\n"
            "  help\n"
            "      Показывает эту памятку.\n"
            "  exit\n"
            "      Завершает работу программы."
        )

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
                user_input = input("db_repl> ").strip()
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


class RPCBase:
    def __init__(self, host="127.0.0.1", port=8080):
        self.host = host
        self.port = port

    def serialize(self, obj, tag="data"):
        root = ET.Element(tag)

        def build(elem, obj):
            if isinstance(obj, dict):
                for k, v in obj.items():
                    child = ET.SubElement(elem, str(k))
                    build(child, v)
            elif isinstance(obj, list):
                for item in obj:
                    child = ET.SubElement(elem, "item")
                    build(child, item)
            else:
                elem.text = str(obj)

        build(root, obj)
        return ET.tostring(root, encoding="unicode")

    def deserialize(self, xml_str):
        root = ET.fromstring(xml_str)

        def parse(elem):
            if len(elem) == 0:
                text = (elem.text or "").strip()
                try:
                    return int(text)
                except ValueError:
                    return text
            if all(c.tag == "item" for c in elem):
                return [parse(c) for c in elem]
            return {c.tag: parse(c) for c in elem}

        return parse(root)

    def recv_bytes(self, sock, n):
        data = b""
        while len(data) < n:
            chunk = sock.recv(n - len(data))
            if not chunk:
                raise ConnectionError
            data += chunk
        return data

    def recv_request(self, sock):
        opcode = int.from_bytes(self.recv_bytes(sock, 2), "little")
        size = int.from_bytes(self.recv_bytes(sock, 4), "little")
        body = self.recv_bytes(sock, size).decode("utf-8")
        return opcode, self.deserialize(body)

    def recv_response(self, sock):
        opcode = int.from_bytes(self.recv_bytes(sock, 2), "little")
        size = int.from_bytes(self.recv_bytes(sock, 5), "little")
        body = self.recv_bytes(sock, size).decode("utf-8")
        return opcode, self.deserialize(body)

    def send_request(self, sock, opcode, req):
        body = self.serialize(req, "args").encode("utf-8")
        sock.sendall(opcode.to_bytes(2, "little"))
        sock.sendall(len(body).to_bytes(4, "little"))
        sock.sendall(body)

    def send_response(self, sock, opcode, result):
        body = self.serialize(result, "response").encode("utf-8")
        sock.sendall(opcode.to_bytes(2, "little"))
        sock.sendall(len(body).to_bytes(5, "little"))
        sock.sendall(body)


class RPCServer(RPCBase):
    def __init__(self, host="127.0.0.1", port=5060):
        super().__init__(host, port)
        self.repl = Repl()
        self.ops = {
            1: self.repl.create_client_repl,
            2: self.repl.delete_client_repl,
            3: self.repl.get_all_clients_repl,
            4: self.repl.get_client_by_id_repl,
            5: self.repl.create_task_repl,
            6: self.repl.delete_task_repl,
            7: self.repl.get_all_tasks_repl,
            8: self.repl.get_task_by_id_repl,
            9: self.repl.create_response_repl,
            10: self.repl.delete_response_repl,
            11: self.repl.get_all_responses_repl,
            12: self.repl.get_response_by_id_repl,
            13: self.repl.query_right_join_repl,
            14: self.repl.test_data,
            15: self.repl.help_repl,
        }

    def start(self):
        s = socket.socket()
        s.bind((self.host, self.port))
        s.listen(1)
        print(f"RPC server on {self.host}:{self.port}")
        while True:
            conn, addr = s.accept()
            print(f"Client connected: {addr}")
            self.handle(conn)

    def handle(self, conn):
        while True:
            try:
                opcode, args = self.recv_request(conn)
            except ConnectionError:
                break

            if not isinstance(args, list):
                args = [args] if args else []

            print(f"[server] opcode={opcode} args={args}")

            try:
                result = self.ops[opcode](*args)
                status = "OK"
            except Exception as e:
                result = str(e)
                status = "ERROR"

            print(f"[server] result={result} status={status}")
            # logging.info(...)
            self.send_response(conn, opcode, result)
        conn.close()


class RPCClient(RPCBase):
    OPS = {
        "create_client": 1,
        "delete_client": 2,
        "get_all_clients": 3,
        "get_client_by_id": 4,
        "create_task": 5,
        "delete_task": 6,
        "get_all_tasks": 7,
        "get_task_by_id": 8,
        "create_response": 9,
        "delete_response": 10,
        "get_all_responses": 11,
        "get_response_by_id": 12,
        "query_right_join": 13,
        "test_data": 14,
        "help": 15,
    }

    def __init__(self, host="127.0.0.1", port=5060):
        super().__init__(host, port)
        self.sock = socket.socket()
        self.sock.connect((self.host, self.port))

    def _call(self, name, *args):
        opcode = self.OPS[name]
        self.send_request(self.sock, opcode, list(args))
        _, result = self.recv_response(self.sock)
        return result

    def create_client(self, args):
        return self._call("create_client", args)

    def delete_client(self, args):
        return self._call("delete_client", args)

    def get_all_clients(self, args):
        return self._call("get_all_clients", args)

    def get_client_by_id(self, args):
        return self._call("get_client_by_id", args)

    def create_task(self, args):
        return self._call("create_task", args)

    def delete_task(self, args):
        return self._call("delete_task", args)

    def get_all_tasks(self, args):
        return self._call("get_all_tasks", args)

    def get_task_by_id(self, args):
        return self._call("get_task_by_id", args)

    def create_response(self, args):
        return self._call("create_response", args)

    def delete_response(self, args):
        return self._call("delete_response", args)

    def get_all_responses(self, args):
        return self._call("get_all_responses", args)

    def get_response_by_id(self, args):
        return self._call("get_response_by_id", args)

    def query_right_join(self, args):
        return self._call("query_right_join", args)

    def test_data(self, args):
        return self._call("test_data", args)

    def help(self, args):
        return self._call("help", args)

    def run(self):
        while True:
            try:
                user_input = input("db_rpc_client> ").strip()
                if not user_input:
                    continue

                parts = user_input.split()
                cmd = parts[0].lower()
                args = parts[1:]

                if cmd == "exit":
                    break

                if cmd not in self.OPS:
                    print("Такой команды нет!")
                    continue
                method = getattr(self, cmd)
                print(method(args))

            except Exception as e:
                print(e)


if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "server":
        print("Сервер поднят")
        RPCServer(host="127.0.0.1", port=5007).start()
    elif len(sys.argv) > 1 and sys.argv[1] == "client":
        c = RPCClient(host="127.0.0.1", port=5007)
        c.run()
    else:
        print("Usage: python file.py server|client")