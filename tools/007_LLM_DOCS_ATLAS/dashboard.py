from html import escape
from .cli import _snapshot

def write_dashboard(ctx, destination):
    data = _snapshot(ctx)
    rows = "".join(f"<tr><td>{escape(str(row.get('path','')))}</td><td>{row.get('estimated_tokens',0)}</td></tr>" for row in data["largest_docs"])
    html = f"<!doctype html><meta charset='utf-8'><title>LDA health</title><style>body{{font:16px system-ui;max-width:900px;margin:2rem auto}}td,th{{padding:.4rem;text-align:left}}</style><h1>Repository Documentation Health</h1><p>{data['documents']} documents · {data['estimated_tokens']} estimated tokens · {data['links']} links · {data['symbols']} symbols · {data['code_mappings']} code mappings</p><h2>Largest documents</h2><table><tr><th>Path</th><th>Tokens</th></tr>{rows}</table>"
    destination.parent.mkdir(parents=True, exist_ok=True); destination.write_text(html, encoding="utf-8"); return destination
