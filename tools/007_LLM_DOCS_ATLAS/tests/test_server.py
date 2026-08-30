import importlib
import json
import threading
import unittest
from urllib.request import urlopen

class TestServer(unittest.TestCase):
    @unittest.skipUnless(__import__('os').environ.get('LDA_SERVER_TESTS') == '1', 'requires local socket permission')
    def test_provider_endpoint_returns_json(self):
        server_module = importlib.import_module('tools.lda.server')
        context = importlib.import_module('tools.007_LLM_DOCS_ATLAS.core.config').AtlasContext.discover()
        server_module.Handler.ctx = context
        server = server_module.ThreadingHTTPServer(('127.0.0.1', 0), server_module.Handler)
        thread = threading.Thread(target=server.serve_forever, daemon=True); thread.start()
        try:
            with urlopen(f'http://127.0.0.1:{server.server_port}/api/providers') as response:
                payload = json.load(response)
            self.assertTrue(payload)
            self.assertIn('provider', payload[0])
        finally:
            server.shutdown(); server.server_close(); thread.join(timeout=2)
