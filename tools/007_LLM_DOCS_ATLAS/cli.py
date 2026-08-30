"""Command line interface for LDA."""
from __future__ import annotations
import argparse, json, re, shutil, sys
from pathlib import Path
from .atlas import collect
from .core.config import AtlasContext
from .core.models import Candidate, ContextPacket, serialise

def _rows(ctx, name):
    path = ctx.knowledge / name
    if not path.exists(): return []
    return [json.loads(line) for line in path.read_text().splitlines() if line.strip()]

def _snapshot(ctx):
    docs = _rows(ctx, "catalog.jsonl"); links = _rows(ctx, "links.jsonl")
    total = {"documents": len(docs), "canonical_docs": sum(r.get("authority") in {"constitutional", "normative", "canonical"} for r in docs), "non_canonical_docs": sum(r.get("authority") not in {"constitutional", "normative", "canonical"} for r in docs), "lines": sum(r.get("lines", 0) for r in docs), "bytes": sum(r.get("bytes", 0) for r in docs), "estimated_tokens": sum(r.get("estimated_tokens", 0) for r in docs), "links": len(links), "broken_links": 0, "symbols": len(_rows(ctx,"symbols.jsonl")), "code_mappings": len(_rows(ctx,"code-map.jsonl")), "providers": [r.provider for r in collect(ctx)], "largest_docs": sorted(docs, key=lambda r:r.get("estimated_tokens",0), reverse=True)[:5]}
    return total

def _packet(ctx, task, budget):
    terms = set(re.findall(r"[a-zA-Z][a-zA-Z0-9_/-]{2,}", task.lower()))
    docs = []
    for row in _rows(ctx, "catalog.jsonl"):
        hay = " ".join(str(row.get(k,"")) for k in ("canonical_id","path","title","owner","summary")).lower(); hits = sum(t in hay for t in terms)
        authority = row.get("authority"); boost = 8 if authority in {"constitutional","normative","canonical"} else 2
        if hits or boost > 2: docs.append(Candidate(row.get("path",""), "document", row.get("title",row.get("path","")), hits*10+boost, row.get("estimated_tokens",0), "keyword/authority match", authority))
    docs.sort(key=lambda c:(-c.score,c.tokens,c.locator)); chosen=[]; used=0
    for item in docs:
        if used + item.tokens <= budget: chosen.append(item); used += item.tokens
    symbols=[]; code=[]
    for row in _rows(ctx,"symbols.jsonl"):
        if any(t in row.get("symbol","").lower() for t in terms): symbols.append(Candidate(row.get("defined_in",""),"symbol",row.get("symbol",""),20,0,"symbol match"))
    for row in _rows(ctx,"code-map.jsonl"):
        if any(t in (row.get("subsystem","")+row.get("package_path","")).lower() for t in terms): code.append(Candidate(row.get("package_path",""),"code",row.get("subsystem",""),15,0,"code-map match"))
    return ContextPacket(task,budget,used,chosen,code,symbols,[],sorted({c.authority for c in chosen if c.authority}),["Research and reports are excluded by default."])

def main(argv=None):
    parser=argparse.ArgumentParser(prog="lda"); parser.add_argument("--root",type=Path); sub=parser.add_subparsers(dest="command",required=True)
    for name in ("status","scan","check","build","doctor"): sub.add_parser(name).add_argument("--json",action="store_true")
    q=sub.add_parser("query"); q.add_argument("query"); q.add_argument("--json",action="store_true")
    c=sub.add_parser("context"); c.add_argument("task"); c.add_argument("--budget",type=int,default=6000); c.add_argument("--json",action="store_true"); c.add_argument("--include-research",action="store_true")
    i=sub.add_parser("inspect"); i.add_argument("target"); i.add_argument("--json",action="store_true")
    args=parser.parse_args(argv); ctx=AtlasContext.discover(args.root, getattr(args,"include_research",False)); result=None
    if args.command in {"status","scan"}: result=_snapshot(ctx)
    elif args.command == "context": result=serialise(_packet(ctx,args.task,args.budget))
    elif args.command == "query": result=[r for r in _rows(ctx,"catalog.jsonl") if args.query.lower() in json.dumps(r).lower()]
    elif args.command == "inspect": result=next((r for r in _rows(ctx,"catalog.jsonl") if args.target in {r.get("path"),r.get("canonical_id")}), {"error":"not found","target":args.target})
    elif args.command == "doctor": result={"root":str(ctx.root),"knowledge":ctx.knowledge.exists(),"required":["python3"],"optional":{"mkdocs":shutil.which("mkdocs") is not None,"vale":shutil.which("vale") is not None,"markdownlint":shutil.which("markdownlint") is not None}}
    elif args.command == "check": result={"delegation":"use just docs-check/docs-full or docs-build","status":"available"}
    elif args.command == "build":
        from .dashboard import write_dashboard
        path=write_dashboard(ctx, ctx.root / "tools" / "007_LLM_DOCS_ATLAS" / "dashboard.html")
        result={"dashboard":str(path.relative_to(ctx.root)),"status":"built"}
    wants_json=getattr(args,"json",False)
    if wants_json: print(json.dumps(result,indent=2,sort_keys=True))
    else: print(json.dumps(result,indent=2,sort_keys=True) if isinstance(result,(dict,list)) else result)
    return 0

if __name__ == "__main__": sys.exit(main())
