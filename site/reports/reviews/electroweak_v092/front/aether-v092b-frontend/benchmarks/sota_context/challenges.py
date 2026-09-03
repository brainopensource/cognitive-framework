"""Five hermetic challenges with public tests and stricter hidden oracles."""

from __future__ import annotations

from benchmarks.swe_bench.challenges import SWEProChallenge


def _large_catalog() -> str:
    rows = ["# Generated fixture: intentionally large context.\n", "ROWS = [\n"]
    for index in range(6000):
        alias = f"item-{index}"
        if index == 5999:
            alias = "item-42"  # hidden collision near EOF
        rows.append(f"    ({index}, {alias!r}, 'payload-{index}'),\n")
    rows.append("]\n")
    return "".join(rows)


CHALLENGES: dict[str, SWEProChallenge] = {
    "sota_easy_config_precedence": SWEProChallenge(
        challenge_id="sota_easy_config_precedence",
        tier=1,
        title="Typed Configuration Precedence",
        kind="bugfix",
        brief=(
            "Fix config loading across `config/defaults.py`, `config/coerce.py`, and "
            "`config/loader.py`. Precedence must be defaults < file values < environment, "
            "booleans must be typed, and caller inputs must not be mutated. Run public tests."
        ),
        files={
            "config/__init__.py": "from .loader import load_config\n",
            "config/defaults.py": "DEFAULTS = {'debug': False, 'workers': 2, 'region': 'local'}\n",
            "config/coerce.py": (
                "def coerce(key, value):\n"
                "    if key == 'workers':\n        return int(value)\n"
                "    if key == 'debug':\n        return bool(value)  # BUG: 'false' is true\n"
                "    return value\n"
            ),
            "config/loader.py": (
                "from .defaults import DEFAULTS\nfrom .coerce import coerce\n\n"
                "def load_config(file_values, environ):\n"
                "    result = file_values  # BUG: mutates caller\n"
                "    result.update(DEFAULTS)  # BUG: defaults overwrite file\n"
                "    for key in DEFAULTS:\n"
                "        env_key = 'APP_' + key.upper()\n"
                "        if env_key in environ:\n            result[key] = coerce(key, environ[env_key])\n"
                "    return result\n"
            ),
            "test_config_public.py": (
                "import unittest\nfrom config import load_config\n\n"
                "class Public(unittest.TestCase):\n"
                " def test_precedence_and_types(self):\n"
                "  source={'workers': 4}; out=load_config(source, {'APP_DEBUG':'false','APP_WORKERS':'8'})\n"
                "  self.assertEqual(out, {'debug':False,'workers':8,'region':'local'})\n"
                "  self.assertEqual(source, {'workers':4})\n"
            ),
        },
        oracle_code=(
            "import unittest\nfrom config import load_config\n"
            "class Hidden(unittest.TestCase):\n"
            " def test_true_spellings(self):\n"
            "  for value in ('1','true','TRUE','yes','on'):\n"
            "   self.assertIs(load_config({}, {'APP_DEBUG':value})['debug'], True)\n"
            " def test_false_spellings(self):\n"
            "  for value in ('0','false','FALSE','no','off'):\n"
            "   self.assertIs(load_config({}, {'APP_DEBUG':value})['debug'], False)\n"
            "if __name__=='__main__': unittest.main()\n"
        ),
    ),
    "sota_medium_public_interface": SWEProChallenge(
        challenge_id="sota_medium_public_interface",
        tier=3,
        title="Public Interface Migration with Compatibility",
        kind="feature",
        brief=(
            "Migrate the public `User.name` interface to `display_name` across all callers. "
            "Keep a read-only deprecated `name` compatibility property, make serializers emit "
            "only `display_name`, update importers, and run all public tests."
        ),
        files={
            "users/__init__.py": "from .model import User\nfrom .service import greeting\n",
            "users/model.py": (
                "from dataclasses import dataclass\n@dataclass\nclass User:\n"
                "    user_id: str\n    name: str\n"
            ),
            "users/service.py": "def greeting(user):\n    return f'Hello, {user.name}!'\n",
            "users/serializer.py": "def dump_user(user):\n    return {'id': user.user_id, 'name': user.name}\n",
            "users/importer.py": "from .model import User\ndef load(row):\n    return User(row['id'], row['display_name'])\n",
            "test_users_public.py": (
                "import unittest\nfrom users.model import User\nfrom users.service import greeting\n"
                "from users.serializer import dump_user\nfrom users.importer import load\n"
                "class Public(unittest.TestCase):\n"
                " def test_new_surface_and_compatibility(self):\n"
                "  u=User('1', display_name='Ada'); self.assertEqual(u.name,'Ada')\n"
                "  self.assertEqual(greeting(u),'Hello, Ada!')\n"
                "  self.assertEqual(dump_user(u),{'id':'1','display_name':'Ada'})\n"
                "  self.assertEqual(load({'id':'2','display_name':'Lin'}).display_name,'Lin')\n"
                " def test_name_is_read_only(self):\n"
                "  u=User('1',display_name='Ada')\n"
                "  with self.assertRaises((AttributeError, TypeError)): u.name='Other'\n"
            ),
        },
        oracle_code=(
            "import inspect,unittest\nfrom users.model import User\nfrom users.serializer import dump_user\n"
            "class Hidden(unittest.TestCase):\n"
            " def test_signature_and_wire_contract(self):\n"
            "  self.assertIn('display_name',inspect.signature(User).parameters)\n"
            "  self.assertNotIn('name',inspect.signature(User).parameters)\n"
            "  self.assertNotIn('name',dump_user(User('x','N')))\n"
            "if __name__=='__main__': unittest.main()\n"
        ),
    ),
    "sota_medium_idempotent_ledger": SWEProChallenge(
        challenge_id="sota_medium_idempotent_ledger",
        tier=4,
        title="Idempotent Ledger and Deterministic Reducer",
        kind="bugfix",
        brief=(
            "Fix the ledger so duplicate event IDs are idempotent, conflicting duplicate payloads "
            "raise `ValueError`, sequence numbers remain contiguous, and account reduction is stable "
            "after replay. Changes span store, events, and reducer. Run public tests."
        ),
        files={
            "ledger/__init__.py": "from .store import EventStore\nfrom .reducer import balance\n",
            "ledger/events.py": (
                "from dataclasses import dataclass\n@dataclass(frozen=True)\nclass Event:\n"
                " event_id: str\n account: str\n delta: int\n sequence: int = 0\n"
            ),
            "ledger/store.py": (
                "from dataclasses import replace\nclass EventStore:\n"
                " def __init__(self): self._events=[]\n"
                " def append(self,event):\n"
                "  stored=replace(event,sequence=len(self._events)+1)\n"
                "  self._events.append(stored)\n  return stored\n"
                " def read(self): return tuple(self._events)\n"
            ),
            "ledger/reducer.py": "def balance(events,account):\n return sum(e.delta for e in events if e.account==account)\n",
            "test_ledger_public.py": (
                "import unittest\nfrom ledger.events import Event\nfrom ledger import EventStore,balance\n"
                "class Public(unittest.TestCase):\n"
                " def test_idempotency_and_conflict(self):\n"
                "  s=EventStore(); e=Event('e1','a',5); first=s.append(e); again=s.append(e)\n"
                "  self.assertEqual(first,again); self.assertEqual(len(s.read()),1)\n"
                "  with self.assertRaises(ValueError): s.append(Event('e1','a',6))\n"
                "  second=s.append(Event('e2','a',-2)); self.assertEqual(second.sequence,2)\n"
                "  self.assertEqual(balance(s.read(),'a'),3)\n"
            ),
        },
        oracle_code=(
            "import unittest\nfrom ledger.events import Event\nfrom ledger import EventStore,balance\n"
            "class Hidden(unittest.TestCase):\n"
            " def test_cross_account_replay(self):\n"
            "  s=EventStore(); events=[Event('1','a',4),Event('2','b',9),Event('1','a',4)]\n"
            "  for e in events:s.append(e)\n"
            "  self.assertEqual([e.sequence for e in s.read()],[1,2])\n"
            "  self.assertEqual((balance(s.read(),'a'),balance(s.read(),'b')),(4,9))\n"
            "if __name__=='__main__': unittest.main()\n"
        ),
    ),
    "sota_hard_large_catalog_collision": SWEProChallenge(
        challenge_id="sota_hard_large_catalog_collision",
        tier=6,
        title="Large Catalog Collision and Stable Lookup",
        kind="bugfix",
        brief=(
            "`catalog/data.py` is a large generated file. Fix the multi-file catalog loader so "
            "duplicate aliases are detected deterministically (raise `AliasCollision` naming both "
            "IDs), exact ID lookup remains available, and input order cannot change the verdict. "
            "Do not rewrite the generated data file. Use bounded search and run public tests."
        ),
        files={
            "catalog/__init__.py": "from .registry import Registry, AliasCollision\n",
            "catalog/data.py": _large_catalog(),
            "catalog/errors.py": "class AliasCollision(ValueError):\n pass\n",
            "catalog/registry.py": (
                "from .errors import AliasCollision\nclass Registry:\n"
                " def __init__(self,rows):\n"
                "  self.by_id={row[0]:row for row in rows}\n"
                "  self.by_alias={row[1]:row for row in rows}  # BUG: last wins\n"
                " def by_exact_id(self,item_id): return self.by_id[item_id]\n"
                " def by_name(self,alias): return self.by_alias[alias]\n"
            ),
            "catalog/loader.py": "from .data import ROWS\nfrom .registry import Registry\ndef load(): return Registry(ROWS)\n",
            "test_catalog_public.py": (
                "import unittest\nfrom catalog import Registry,AliasCollision\n"
                "class Public(unittest.TestCase):\n"
                " def test_collision_is_deterministic(self):\n"
                "  rows=[(2,'same','b'),(1,'same','a')]\n"
                "  for ordered in (rows,list(reversed(rows))):\n"
                "   with self.assertRaisesRegex(AliasCollision,'1.*2|2.*1'): Registry(ordered)\n"
                " def test_exact_lookup(self): self.assertEqual(Registry([(7,'x','p')]).by_exact_id(7)[2],'p')\n"
            ),
        },
        oracle_code=(
            "import unittest\nfrom catalog.loader import load\nfrom catalog import AliasCollision\n"
            "class Hidden(unittest.TestCase):\n"
            " def test_near_eof_collision(self):\n"
            "  with self.assertRaisesRegex(AliasCollision,'42.*5999|5999.*42'): load()\n"
            "if __name__=='__main__': unittest.main()\n"
        ),
    ),
    "sota_hard_atomic_quota": SWEProChallenge(
        challenge_id="sota_hard_atomic_quota",
        tier=7,
        title="Atomic Multi-Shard Quota Reservation",
        kind="bugfix",
        brief=(
            "Fix quota reservation across model, shard store, coordinator, and API. A reservation "
            "must be atomic across shards, rollback on partial failure, be idempotent by request ID, "
            "and never expose negative capacity. Run all public tests."
        ),
        files={
            "quota/__init__.py": "from .api import reserve\nfrom .store import ShardStore\n",
            "quota/model.py": (
                "from dataclasses import dataclass\n@dataclass(frozen=True)\nclass Request:\n"
                " request_id:str\n amounts:dict[str,int]\n"
            ),
            "quota/store.py": (
                "class ShardStore:\n"
                " def __init__(self,capacities): self.capacities=dict(capacities); self.fail_on=set()\n"
                " def take(self,shard,amount):\n"
                "  if shard in self.fail_on: raise RuntimeError('injected failure')\n"
                "  self.capacities[shard]-=amount\n"
                " def give_back(self,shard,amount): self.capacities[shard]+=amount\n"
            ),
            "quota/coordinator.py": (
                "class Coordinator:\n"
                " def __init__(self,store): self.store=store; self.settled={}\n"
                " def reserve(self,request):\n"
                "  for shard,amount in request.amounts.items(): self.store.take(shard,amount)\n"
                "  self.settled[request.request_id]=True\n  return True\n"
            ),
            "quota/api.py": (
                "from .model import Request\nfrom .coordinator import Coordinator\n"
                "def reserve(store,request_id,amounts): return Coordinator(store).reserve(Request(request_id,amounts))\n"
            ),
            "test_quota_public.py": (
                "import unittest\nfrom quota.model import Request\nfrom quota.coordinator import Coordinator\nfrom quota.store import ShardStore\n"
                "class Public(unittest.TestCase):\n"
                " def test_atomic_rollback_and_idempotency(self):\n"
                "  s=ShardStore({'a':5,'b':5}); c=Coordinator(s); s.fail_on.add('b')\n"
                "  with self.assertRaises(RuntimeError): c.reserve(Request('r1',{'a':3,'b':2}))\n"
                "  self.assertEqual(s.capacities,{'a':5,'b':5}); s.fail_on.clear()\n"
                "  self.assertTrue(c.reserve(Request('r1',{'a':3,'b':2})))\n"
                "  self.assertTrue(c.reserve(Request('r1',{'a':3,'b':2})))\n"
                "  self.assertEqual(s.capacities,{'a':2,'b':3})\n"
                " def test_insufficient_capacity(self):\n"
                "  s=ShardStore({'a':1}); c=Coordinator(s)\n"
                "  with self.assertRaises(ValueError): c.reserve(Request('x',{'a':2}))\n"
                "  self.assertEqual(s.capacities['a'],1)\n"
            ),
        },
        oracle_code=(
            "import unittest\nfrom quota.model import Request\nfrom quota.coordinator import Coordinator\nfrom quota.store import ShardStore\n"
            "class Hidden(unittest.TestCase):\n"
            " def test_three_shard_reverse_failure(self):\n"
            "  s=ShardStore({'a':4,'b':4,'c':4}); c=Coordinator(s); s.fail_on={'c'}\n"
            "  with self.assertRaises(RuntimeError): c.reserve(Request('z',{'a':1,'b':2,'c':3}))\n"
            "  self.assertEqual(s.capacities,{'a':4,'b':4,'c':4})\n"
            "if __name__=='__main__': unittest.main()\n"
        ),
    ),
}

TIERS = {
    "sota-easy": ("sota_easy_config_precedence",),
    "sota-medium": (
        "sota_medium_public_interface",
        "sota_medium_idempotent_ledger",
    ),
    "sota-hard": (
        "sota_hard_large_catalog_collision",
        "sota_hard_atomic_quota",
    ),
}
