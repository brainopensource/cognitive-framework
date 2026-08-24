import json, unittest, pathlib
from aether_m456.runtime.child_reducer import (fold_child_event, open_children,
    parent_cost, ChildReducerError, OPEN, CLOSED)
from aether_m456.runtime.writer_authority import ADR_0090_KIND_OWNERS, assert_writer

SPAWN = {"kind":"ChildSpawned","parent_episode_id":"ep-parent","child_episode_id":"ep-c1",
  "authority":["fs.read"],"budget_share":{"usd_micros":400},"depth":1,
  "lineage":["ep-parent"],"descriptor_digest":"sha256:"+"a"*64,
  "grant_id":"g-1","settled_intent_key":"idem-1"}
RETURN = {"kind":"ChildReturned","child_episode_id":"ep-c1","outcome":"completed",
  "terminal":"done","cost":{"usd_micros":320,"millis":90},"settled_intent_key":"idem-1"}

class TestReducerContract(unittest.TestCase):
    def test_spawn_opens_a_child_record(self):
        s = fold_child_event({}, SPAWN)
        self.assertEqual(s["ep-c1"].status, OPEN)
        self.assertTrue(s["ep-c1"].reconcilable)

    def test_spawn_then_return_closes(self):
        s = fold_child_event(fold_child_event({}, SPAWN), RETURN)
        self.assertEqual(s["ep-c1"].status, CLOSED)
        self.assertEqual(s["ep-c1"].outcome, "completed")
        self.assertFalse(s["ep-c1"].reconcilable)

    def test_unmatched_spawn_stays_open_for_cold_path(self):
        s = fold_child_event({}, SPAWN)
        self.assertEqual([c.child_episode_id for c in open_children(s)], ["ep-c1"])

    def test_closed_child_needs_no_reconciliation(self):
        s = fold_child_event(fold_child_event({}, SPAWN), RETURN)
        self.assertEqual(open_children(s), ())

    def test_return_without_spawn_is_an_error(self):
        with self.assertRaises(ChildReducerError):
            fold_child_event({}, RETURN)

    def test_duplicate_spawn_is_an_error(self):
        with self.assertRaises(ChildReducerError):
            fold_child_event(fold_child_event({}, SPAWN), SPAWN)

    def test_double_return_is_an_error(self):
        s = fold_child_event(fold_child_event({}, SPAWN), RETURN)
        with self.assertRaises(ChildReducerError):
            fold_child_event(s, RETURN)

    def test_intent_key_mismatch_is_an_error(self):
        s = fold_child_event({}, SPAWN)
        with self.assertRaises(ChildReducerError):
            fold_child_event(s, {**RETURN, "settled_intent_key":"OTHER"})

    def test_fold_is_pure(self):
        base = {}
        fold_child_event(base, SPAWN)
        self.assertEqual(base, {})           # input never mutated

class TestCostConservation(unittest.TestCase):
    def test_child_cost_folds_into_parent(self):
        s = fold_child_event(fold_child_event({}, SPAWN), RETURN)
        self.assertEqual(parent_cost(s), {"usd_micros":320,"millis":90})
    def test_open_child_contributes_no_cost(self):
        self.assertEqual(parent_cost(fold_child_event({}, SPAWN)), {})

class TestSingleWriter(unittest.TestCase):
    def test_spawn_adapter_may_write(self):
        for k in ("ChildSpawned","ChildReturned"):
            assert_writer(k, "spawn_adapter", ADR_0090_KIND_OWNERS)
    def test_kernel_may_not_write_child_events(self):
        with self.assertRaises(PermissionError):
            assert_writer("ChildSpawned", "kernel", ADR_0090_KIND_OWNERS)
    def test_orchestrator_owns_nothing(self):
        with self.assertRaises(PermissionError):
            assert_writer("ChildReturned", "orchestrator", ADR_0090_KIND_OWNERS)
    def test_unregistered_kind_denied(self):
        with self.assertRaises(PermissionError):
            assert_writer("ChildFailed", "spawn_adapter", ADR_0090_KIND_OWNERS)

class TestSchemaVectors(unittest.TestCase):
    def setUp(self):
        p = pathlib.Path(__file__).parent.parent/"aether_m456"/"schemas"/"child_events.schema.json"
        self.s = json.load(open(p))["$defs"]
    def test_required_fields_declared(self):
        self.assertEqual(set(SPAWN) , set(self.s["ChildSpawned"]["required"]))
        self.assertEqual(set(RETURN), set(self.s["ChildReturned"]["required"]))
    def test_no_additional_properties(self):
        for d in self.s.values(): self.assertFalse(d["additionalProperties"])
    def test_depth_is_bounded_in_schema(self):
        self.assertEqual(self.s["ChildSpawned"]["properties"]["depth"]["maximum"], 4)
    def test_no_child_failed_kind_exists(self):
        self.assertNotIn("ChildFailed", self.s)   # rejected alternative stays rejected
