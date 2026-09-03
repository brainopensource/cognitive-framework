import importlib, json, tempfile, unittest
from pathlib import Path
Entity = importlib.import_module("tools.007_LLM_DOCS_ATLAS.core.models").Entity
serialise = importlib.import_module("tools.007_LLM_DOCS_ATLAS.core.models").serialise

class TestModels(unittest.TestCase):
    def test_serialise_dataclass(self):
        self.assertEqual(serialise(Entity("x","document","x.md"))["id"], "x")

    def test_jsonl_provider_is_optional(self):
        with tempfile.TemporaryDirectory() as d:
            root=Path(d); (root/"docs").mkdir(); (root/"justfile").touch(); (root/".generated/knowledge").mkdir(parents=True)
            (root/".generated/knowledge/catalog.jsonl").write_text(json.dumps({"canonical_id":"x","path":"x.md","estimated_tokens":4})+"\n")
            AtlasContext = importlib.import_module("tools.007_LLM_DOCS_ATLAS.core.config").AtlasContext
            KnowledgeProvider = importlib.import_module("tools.007_LLM_DOCS_ATLAS.providers.knowledge").KnowledgeProvider
            result=KnowledgeProvider().collect(AtlasContext.discover(root))
            self.assertEqual(result.entities[0].id,"x")
