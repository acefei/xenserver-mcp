# Project Context

## Environment
- Language: Python 3.x
- Runtime: uv (detected uv.lock)
- Build: uv pip install -e .
- Test: pytest
- Package Manager: uv / pip

## Project Type
- [ ] Library/Package
- [x] Application (MCP Server)
- [ ] Microservice
- [ ] Monorepo
- [ ] Other: [describe]

## Infrastructure
- Container: None detected
- Orchestration: None detected
- CI/CD: .github/workflows detected (but not read yet)
- Cloud: XenServer (On-prem/Cloud)

## Structure
- Source: src/xenserver_mcp
- Tests: tests/
- Docs: docs/
- Entry: src/xenserver_mcp/server.py

## Conventions
- Naming: snake_case (Python)
- Imports: absolute/relative
- Error handling: try/except with logging and format_error
- Testing: pytest with conftest.py

## Notes
- Uses `mcp` package for Model Context Protocol.
- Uses `xen_api` wrapper for XenServer communication.
- Configuration in `config/clusters.json`.
