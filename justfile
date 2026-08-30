# AETHER Repository Control Surface & Developer Gates

# Default recipe: fast local development check
default: check

# Fast normal development validation loop
check:
	python3 tools/linters/check_boundaries.py
	python3 tools/linters/check_tcb_budget.py
	python3 tools/linters/check_domain_blindness.py
	python3 tools/linters/check_isolation_policy.py
	python3 tools/linters/check_path_hygiene.py
	just docs-check
	@echo "AETHER CHECK: PASS"

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
docs-full: docs-check
	python3 tools/generate_knowledge_base.py
	uv run mkdocs build --strict

# Experimental code intelligence diagram generation (.generated/diagrams/)
docs-diagrams:
	python3 tools/generate_exploratory_diagrams.py

# Local RAG V0 query interface
docs-rag QUERY:
	python3 tools/docs_rag_v0.py "{{QUERY}}"

# Canonical local/CI qualification gate before PR completion or sprint closure
verify:
	uv lock --check
	uv sync --frozen
	python3 tools/linters/check_boundaries.py
	python3 tools/linters/check_tcb_budget.py
	python3 tools/linters/check_domain_blindness.py
	python3 tools/linters/check_isolation_policy.py
	python3 tools/linters/check_path_hygiene.py
	python3 tools/linters/check_event_coverage.py
	python3 tools/linters/check_execution_truth.py
	python3 tools/linters/check_falsifier_ids.py
	python3 tools/linters/scan_secrets.py
	python3 -m unittest discover -s test/kernel -t .
	python3 -m unittest discover -s test/agency -t .
	python3 -m unittest discover -s test/contracts -t .
	npm run typecheck
	npm test
	just docs-full
	@echo "AETHER VERIFY: PASS"

# Release candidate qualification wrapper
release-verify SUBJECT ENVELOPE GIT_RECEIPT:
	python3 tools/release_qualification.py --subject "{{SUBJECT}}" --envelope "{{ENVELOPE}}" --git-receipt "{{GIT_RECEIPT}}"
	@echo "AETHER RELEASE VERIFY: PASS"
