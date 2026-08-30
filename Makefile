.PHONY: clean clean-py clean-benchmark-cache clean-js clean-build clean-test clean-cache clean-wsl clean-all help

help:
	@echo "Repository Cleanup Targets:"
	@echo "  make clean-py       - Remove Python cache & artifacts (__pycache__, *.pyc, .pytest_cache, etc)"
	@echo "  make clean-benchmark-cache - Remove only Python bytecode caches between benchmark rows"
	@echo "  make clean-js       - Remove JavaScript cache & artifacts (node_modules, .next, dist, build)"
	@echo "  make clean-build    - Remove build artifacts & dist folders"
	@echo "  make clean-test     - Remove test cache & coverage reports (.pytest_cache, .coverage, htmlcov)"
	@echo "  make clean-cache    - Remove IDE & editor cache (.vscode, .idea, *.swp, *.swo)"
	@echo "  make clean-wsl      - Remove Windows WSL trash (Zone:Identifier alternate data streams)"
	@echo "  make clean          - Run all cleanup targets (safe for benchmarking)"
	@echo "  make clean-all      - NUCLEAR: Remove everything including node_modules & build dirs"
	@echo ""
	@echo "Usage: make clean-py  OR  make clean-all"

## Python cleanup
clean-benchmark-cache:
	@echo "🧹 Cleaning benchmark Python bytecode caches..."
	find . -type d -name "__pycache__" -prune -exec rm -rf {} + 2>/dev/null || true
	find . -type f \( -name "*.pyc" -o -name "*.pyo" \) -delete 2>/dev/null || true
	@echo "✅ Benchmark bytecode cache cleanup complete"

clean-py:
	@echo "🧹 Cleaning Python cache & artifacts..."
	find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name ".pytest_cache" -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name ".mypy_cache" -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name ".ruff_cache" -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name ".tox" -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name ".eggs" -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name "*.egg-info" -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name "dist" -path "*/build/*" -prune -o -type d -name "dist" -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete 2>/dev/null || true
	find . -type f -name "*.pyo" -delete 2>/dev/null || true
	find . -type f -name "*.pyd" -delete 2>/dev/null || true
	find . -type f -name ".Python" -delete 2>/dev/null || true
	find . -type f -name "*.so" -delete 2>/dev/null || true
	@echo "✅ Python cleanup complete"

## JavaScript cleanup
clean-js:
	@echo "🧹 Cleaning JavaScript cache & artifacts..."
	find . -type d -name ".next" -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name "build" -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name "dist" -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name ".turbo" -exec rm -rf {} + 2>/dev/null || true
	@echo "✅ JavaScript cleanup complete"

## Build artifacts
clean-build:
	@echo "🧹 Cleaning build artifacts..."
	find . -type d -name "build" -not -path "*/node_modules/*" -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name "dist" -not -path "*/node_modules/*" -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name "out" -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name "*.whl" -delete 2>/dev/null || true
	find . -type f -name "*.tar.gz" -delete 2>/dev/null || true
	@echo "✅ Build cleanup complete"

## Test cache & coverage
clean-test:
	@echo "🧹 Cleaning test artifacts & coverage..."
	find . -type d -name ".pytest_cache" -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name "htmlcov" -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name ".coverage" -delete 2>/dev/null || true
	find . -type f -name "coverage.xml" -delete 2>/dev/null || true
	find . -type f -name ".hypothesis" -delete 2>/dev/null || true
	@echo "✅ Test cleanup complete"

## IDE & editor cache
clean-cache:
	@echo "🧹 Cleaning IDE & editor cache..."
	find . -type d -name ".vscode" -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name ".idea" -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name "*.swp" -delete 2>/dev/null || true
	find . -type f -name "*.swo" -delete 2>/dev/null || true
	find . -type f -name "*~" -delete 2>/dev/null || true
	find . -type f -name ".DS_Store" -delete 2>/dev/null || true
	@echo "✅ IDE cache cleanup complete"

## WSL & Windows trash
clean-wsl:
	@echo "🧹 Cleaning WSL/Windows alternate data streams (Zone:Identifier)..."
	find . -type f -name "*:Zone.Identifier" -delete 2>/dev/null || true
	@echo "✅ WSL cleanup complete"

## Safe cleanup - everything except node_modules & build
clean: clean-py clean-js clean-build clean-test clean-cache clean-wsl
	@echo ""
	@echo "🎉 Repository cleanup complete! Ready for benchmarking."
	@echo "   (Preserved: node_modules, critical build files)"

## NUCLEAR - everything
clean-all: clean
	@echo ""
	@echo "⚠️  NUCLEAR CLEAN: Removing node_modules & all artifacts..."
	rm -rf node_modules 2>/dev/null || true
	find . -type d -name "node_modules" -exec rm -rf {} + 2>/dev/null || true
	@echo "✅ Total repo reset complete!"
