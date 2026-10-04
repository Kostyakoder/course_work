import hypothesis.strategies as st
from hypothesis.stateful import (
    Bundle,
    RuleBasedStateMachine,
    invariant,
    rule,
)
from hypothesis import settings, Phase


import importlib.util
from pathlib import Path

_mod_path = Path("/home/koder/kis_python_cource_work/src/first_work/1_part.py")
_spec = importlib.util.spec_from_file_location("rpc_module", _mod_path)
mod = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(mod)
client_ids = Bundle("client_ids")
task_ids = Bundle("task_ids")
response_ids = Bundle("response_ids")


class RPCModel:
    def __init__(self):
        self.clients = {}
        self.tasks = {}
        self.responses = {}
        self.next_client_id = 1
        self.next_task_id = 1
        self.next_response_id = 1

    def add_client(self, ip, locale, platform):
        cid = self.next_client_id
        self.clients[cid] = {
            "id": cid,
            "ip": ip,
            "locale": locale,
            "platform": platform,
        }
        self.next_client_id += 1
        return cid

    def remove_client(self, cid):
        if cid in self.clients:
            del self.clients[cid]
            return True
        return False

    def add_task(self, payload, client_id, tags, state):
        tid = self.next_task_id
        self.tasks[tid] = {
            "id": tid,
            "payload": payload,
            "client": client_id,
            "tags": tags,
            "state": state,
        }
        self.next_task_id += 1
        return tid

    def remove_task(self, tid):
        if tid in self.tasks:
            del self.tasks[tid]
            return True
        return False

    def add_response(self, output, state, failure,
                     task_id, cache_hit, duration):
        rid = self.next_response_id
        self.responses[rid] = {
            "id": rid,
            "output": output,
            "state": state,
            "failure": failure,
            "task": task_id,
            "cache_hit": cache_hit,
            "duration": duration,
        }
        self.next_response_id += 1
        return rid

    def remove_response(self, rid):
        if rid in self.responses:
            del self.responses[rid]
            return True
        return False


@settings(
    max_examples=50,
    stateful_step_count=30,
    phases=[Phase.generate, Phase.reuse, Phase.shrink],
    deadline=None,
)
class RPCStateMachine(RuleBasedStateMachine):
    def __init__(self):
        super().__init__()
        self.server = mod.RPCServer(host="127.0.0.1", port=0)
        self.dl = self.server.repl.dataLayer
        self.model = RPCModel()

    @rule(
        target=client_ids,
        ip=st.text(
            min_size=1,
            alphabet=st.characters(blacklist_categories=("Cc", "Cs"))
        ),
        locale=st.text(
            min_size=1,
            alphabet=st.characters(blacklist_categories=("Cc", "Cs"))
        ),
        platform=st.text(
            min_size=1,
            alphabet=st.characters(blacklist_categories=("Cc", "Cs"))
        ),
    )
    def create_client(self, ip, locale, platform):
        result = self.server.ops[1]([ip, locale, platform])
        cid = self.model.add_client(ip, locale, platform)
        assert str(cid) in result, f"Ожидался id {cid} в ответе: {result}"
        assert cid in [c["id"] for c in self.dl.get_all_clients()]
        return cid

    @rule(cid=client_ids)
    def delete_client(self, cid):
        result = self.server.ops[2]([str(cid)])
        removed = self.model.remove_client(cid)
        if removed:
            assert (
                str(cid) in result
            ), f"Ожидалось подтверждение удаления {cid}: {result}"
            assert cid not in [c["id"] for c in self.dl.get_all_clients()]
        else:
            assert "не существует" in result.lower()

    @rule()
    def get_all_clients(self):
        result = self.server.ops[3]([])
        model_ids = set(self.model.clients.keys())
        system_ids = {c["id"] for c in result} \
            if isinstance(result, list) else set()
        assert (
            model_ids == system_ids
        ), f"Рассинхрон ID клиентов: модель {model_ids}, система {system_ids}"

    @rule(cid=client_ids)
    def get_client_by_id(self, cid):
        result = self.server.ops[4]([str(cid)])
        if cid in self.model.clients:
            assert isinstance(result, dict), (
                f"Ожидался словарь для id={cid}, "
                f"получили {type(result)}: {result}"
            )
            assert result["id"] == cid
        else:
            assert "не существует" in str(result).lower()

    @rule(
        target=task_ids,
        payload=st.text(min_size=1),
        cid=client_ids,
        tags=st.text(min_size=1),
        state=st.sampled_from(["work", "success", "unsuccess", "pending"]),
    )
    def create_task(self, payload, cid, tags, state):
        result = self.server.ops[5]([payload, str(cid), tags, state])
        tid = self.model.add_task(payload, cid, tags, state)
        assert str(tid) in result, f"Ожидался id задачи {tid}: {result}"
        assert tid in [t["id"] for t in self.dl.get_all_tasks()]
        return tid

    @rule(tid=task_ids)
    def delete_task(self, tid):
        result = self.server.ops[6]([str(tid)])
        removed = self.model.remove_task(tid)
        if removed:
            assert str(tid) in result
            assert tid not in [t["id"] for t in self.dl.get_all_tasks()]
        else:
            assert "не существует" in result.lower()

    @rule()
    def get_all_tasks(self):
        result = self.server.ops[7]([])
        model_ids = set(self.model.tasks.keys())
        system_ids = {t["id"] for t in result} \
            if isinstance(result, list) else set()
        assert (
            model_ids == system_ids
        ), f"Рассинхрон ID задач: модель {model_ids}, система {system_ids}"

    @rule(tid=task_ids)
    def get_task_by_id(self, tid):
        result = self.server.ops[8]([str(tid)])
        if tid in self.model.tasks:
            assert isinstance(result, dict)
            assert result["id"] == tid
        else:
            assert "не существует" in str(result).lower()

    @rule(
        target=response_ids,
        output=st.text(min_size=1),
        state=st.sampled_from(["finished", "failed", "pending"]),
        failure=st.text(min_size=1),
        tid=task_ids,
        cache_hit=st.integers(min_value=0, max_value=1),
        duration=st.integers(min_value=0, max_value=10_000),
    )
    def create_response(self, output, state, failure,
                        tid, cache_hit, duration):
        result = self.server.ops[9](
            [output, state, failure, str(tid), str(cache_hit), str(duration)]
        )
        rid = self.model.add_response(output, state, failure,
                                      tid, cache_hit, duration)
        assert str(rid) in result, f"Ожидался id ответа {rid}: {result}"
        assert rid in [r["id"] for r in self.dl.get_all_responses()]
        return rid

    @rule(rid=response_ids)
    def delete_response(self, rid):
        result = self.server.ops[10]([str(rid)])
        removed = self.model.remove_response(rid)
        if removed:
            assert str(rid) in result
            assert rid not in [r["id"] for r in self.dl.get_all_responses()]
        else:
            assert "не существует" in result.lower()

    @rule()
    def get_all_responses(self):
        result = self.server.ops[11]([])
        model_ids = set(self.model.responses.keys())
        system_ids = {r["id"] for r in result} \
            if isinstance(result, list) else set()
        assert (
            model_ids == system_ids
        ), f"Рассинхрон ID ответов: модель {model_ids}, система {system_ids}"

    @rule(rid=response_ids)
    def get_response_by_id(self, rid):
        result = self.server.ops[12]([str(rid)])
        if rid in self.model.responses:
            assert isinstance(result, dict)
            assert result["id"] == rid
        else:
            assert "не существует" in str(result).lower()

    @rule()
    def query_right_join(self):
        result = self.server.ops[13]([])
        assert isinstance(result, list)
        assert len(result) == 2

    @rule()
    def test_data(self):
        result = self.server.ops[14]([])
        assert "заполнены" in result.lower()

        self.model.add_client("192.168.127.12", "Russia", "Mess")
        self.model.add_client("192.168.111.00", "Tajikistan", "Mess")
        self.model.add_client("192.168.100.01", "Armenia", "Mess")

        self.model.add_task("server", 1, "important", "work")
        self.model.add_task("server", 2, "sensitive", "success")
        self.model.add_task("server", 5, "disturb", "unsuccess")

        self.model.add_response("Session success", "finished", "No", 1, 0, 0)

    @rule()
    def help(self):
        result = self.server.ops[15]([])
        assert "Доступные команды" in result

    @invariant()
    def invariants(self):
        assert len(self.model.clients) == len(self.dl.get_all_clients())
        assert len(self.model.tasks) == len(self.dl.get_all_tasks())
        assert len(self.model.responses) == len(self.dl.get_all_responses())

        system_client_ids = [c["id"] for c in self.dl.get_all_clients()]
        assert len(system_client_ids) == len(
            set(system_client_ids)
        ), "Дубли ID клиентов!"


TestRPCStateMachine = RPCStateMachine.TestCase
