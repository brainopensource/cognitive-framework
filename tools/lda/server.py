from __future__ import annotations
import argparse, json, threading, webbrowser
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from urllib.parse import parse_qs, urlparse
from pathlib import Path
from importlib import import_module

legacy = import_module("tools.007_LLM_DOCS_ATLAS")
atlas = import_module("tools.007_LLM_DOCS_ATLAS.atlas")
cfg = import_module("tools.007_LLM_DOCS_ATLAS.core.config")
cli = import_module("tools.007_LLM_DOCS_ATLAS.cli")
fs_provider = import_module("tools.007_LLM_DOCS_ATLAS.providers.filesystem")

HTML_PATH = Path(__file__).parent / "index.html"

def get_html() -> str:
    return HTML_PATH.read_text(encoding="utf-8")

def rescan_catalog(ctx):
    provider = fs_provider.FilesystemProvider()
    res = provider.collect(ctx)
    entities = [e.metadata for e in res.entities if e.metadata.get("path")]
    cat_path = ctx.knowledge / "catalog.jsonl"
    if cat_path.parent.exists():
        lines = [json.dumps(d) for d in entities]
        cat_path.write_text("\n".join(lines) + ("\n" if lines else ""), encoding="utf-8")
    return entities

class Handler(BaseHTTPRequestHandler):
    ctx = None
    def send_json(self, value, status=200):
        body=json.dumps(value, default=str).encode(); self.send_response(status); self.send_header('Content-Type','application/json'); self.send_header('Content-Length',str(len(body))); self.end_headers(); self.wfile.write(body)
    def do_GET(self):
        p=urlparse(self.path)
        try:
            if p.path=='/':
                body=get_html().encode(); self.send_response(200); self.send_header('Content-Type','text/html; charset=utf-8'); self.send_header('Content-Length',str(len(body))); self.end_headers(); self.wfile.write(body); return
            if p.path=='/api/status': return self.send_json(cli._snapshot(self.ctx))
            if p.path=='/api/documents':
                docs = cli._rows(self.ctx,'catalog.jsonl')
                if not docs:
                    docs = rescan_catalog(self.ctx)
                valid_docs = [r for r in docs if (self.ctx.root / r.get('path','')).exists()]
                return self.send_json(valid_docs)
            if p.path=='/api/rescan':
                docs = rescan_catalog(self.ctx)
                return self.send_json({'status':'ok', 'documents':len(docs)})
            if p.path=='/api/relations': return self.send_json([{'source':r.get('source_id'),'target':r.get('target_id'),'kind':r.get('relationship_type','references'),'evidence':'links.jsonl'} for r in cli._rows(self.ctx,'links.jsonl')[:500]])
            if p.path=='/api/context':
                q=parse_qs(p.query); import dataclasses
                return self.send_json(dataclasses.asdict(cli._packet(self.ctx,q.get('task',[''])[0],int(q.get('budget',['16000'])[0]))))
            if p.path=='/api/providers': return self.send_json([{'provider':r.provider,'status':'ERROR' if any(d.severity=='error' for d in r.diagnostics) else 'AVAILABLE','diagnostics':len(r.diagnostics)} for r in atlas.collect(self.ctx)])
            return self.send_json({'error':'not found'},404)
        except (ValueError, KeyError) as exc: return self.send_json({'error':str(exc)},400)
    def log_message(self,*args): pass

def serve(root=None, port=8765, open_browser=False):
    Handler.ctx=cfg.AtlasContext.discover(Path(root) if root else None); server=ThreadingHTTPServer(('127.0.0.1',port),Handler); url=f'http://127.0.0.1:{server.server_port}/'; print(url, flush=True)
    if open_browser: threading.Timer(.2,lambda:webbrowser.open(url)).start()
    try: server.serve_forever()
    except KeyboardInterrupt: pass
    finally: server.server_close()

def main(argv=None):
    p=argparse.ArgumentParser(prog='lda serve'); p.add_argument('--port',type=int,default=8765); p.add_argument('--open',action='store_true'); a=p.parse_args(argv); serve(port=a.port,open_browser=a.open)
