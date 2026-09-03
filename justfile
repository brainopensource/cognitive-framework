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

# Local RAG V0 query interface (CANONICAL agent retrieval surface)
docs-rag QUERY:
	python3 tools/docs_rag_v0.py "{{QUERY}}"

# Reverse routing: production code path -> canonical owner docs + symbols
docs-rag-file FILE:
	python3 tools/docs_rag_v0.py --file "{{FILE}}"

# Rebuild the LDA SQLite/FTS index (populate .lda/index.db before lda-query/lda-context)
lda-index:
	uv run lda index

# LDA thin orchestration wrappers.
# NOTE: `lda query` / `lda context` are EXPERIMENTAL for agent retrieval until
# `just lda-doctor` reports index_healthy=true; prefer `just docs-rag` which
# ranks the canonical .generated/knowledge/ catalog with authority boosting.
lda:
	uv run lda serve
lda-status:
	uv run lda status
lda-scan:
	uv run lda scan
lda-check:
	uv run lda check
lda-query QUERY:
	uv run lda query "{{QUERY}}"
lda-context TASK:
	uv run lda context "{{TASK}}"
lda-doctor:
	uv run lda doctor

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

# Install `aether` and `vg` onto ~/.local/bin (survives nvm version switches)
install-cli:
	#!/usr/bin/env bash
	set -euo pipefail
	npm --workspace @vanguard/cli run build
	REPO="$(pwd)"
	BIN="${HOME}/.local/bin"
	mkdir -p "$BIN"
	for name in aether vg; do
	  printf '%s\n' '#!/usr/bin/env bash' "export AETHER_HOME=\"$REPO\"" 'exec node "$AETHER_HOME/vanguard/clients/cli/dist/src/main.js" "$@"' > "$BIN/$name"
	  chmod +x "$BIN/$name"
	done
	echo "Installed $BIN/aether and $BIN/vg"
	echo "Launch: aether"
	if [[ ":$PATH:" != *":$BIN:"* ]]; then
	  echo "Warning: $BIN is not in PATH. Add: export PATH=\"\$HOME/.local/bin:\$PATH\""
	fi
