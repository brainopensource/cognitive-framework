# AETHER Documentation Control Plane Interface

# Default recipe: run full documentation check surface
default: docs-check

# Fast deterministic documentation checks (metadata, uniqueness, links, lint)
docs-check:
	python3 tools/linters/check_doc_metadata.py
	python3 tools/linters/check_markdown_links.py
	npx markdownlint-cli2 "docs/**/*.md" "README.md" "AGENTS.md" "VISION.md"

# Build documentation site strictly with Material for MkDocs
docs-build:
	uv run mkdocs build --strict

# Serve local documentation site with live reloading
docs-serve:
	uv run mkdocs serve

# Regenerate permanent machine knowledge base (.generated/knowledge/)
docs-knowledge:
	python3 tools/generate_knowledge_base.py

# Full CI documentation gate (check + zero-rebuild knowledge + strict build)
docs-full: docs-check docs-knowledge docs-build

# Experimental code intelligence diagram generation (.generated/diagrams/)
docs-diagrams:
	python3 tools/generate_exploratory_diagrams.py

# Local RAG V0 query interface
docs-rag QUERY:
	python3 tools/docs_rag_v0.py "{{QUERY}}"
