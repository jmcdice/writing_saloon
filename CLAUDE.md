# Agent Saloon Development Guidelines

## Build & Test Commands
- Setup: `python -m venv .venv && source .venv/bin/activate && pip install -r requirements.txt`
- Run App: `python run_web.py` or `agent-saloon-web`
- CLI Command: `agent-saloon`
- Tests: `pytest --cov=agent_saloon tests/`
- Test Single File: `pytest tests/path_to_test.py -v`
- Test Single Function: `pytest tests/path_to_test.py::test_function_name -v`
- Type Check: `mypy agent_saloon/`
- Format Code: `black agent_saloon/`
- Sort Imports: `isort agent_saloon/`

## Code Style
- **Formatting**: Black with 88 char line length
- **Types**: Strict typing required (`disallow_untyped_defs=true`)
- **Imports**: Use isort with Black profile compatibility
- **Naming**: 
  - Classes: PascalCase
  - Functions/Variables: snake_case
  - Constants: UPPER_SNAKE_CASE
- **Docstrings**: Google style with type annotations
- **Error Handling**: Use specific exceptions with proper logging
- **Logging**: Use the IRC-style logger module with appropriate log levels