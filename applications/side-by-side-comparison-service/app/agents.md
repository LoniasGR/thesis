# Agent guidance

## Scope and structure

This directory contains the Python backend for the side-by-side comparison service.
The related frontend is in `../frontend`; container and deployment configuration is
in the parent directory. Check both sides when changing request/response behavior or
startup configuration.

- `client/client.py` coordinates generated dialogues and suggestion selection.
- `client/rasa_client.py` communicates with the Rasa service.
- `common/` contains intent mappings and dialogue helpers; preserve Greek prompt
  and response text when editing these mappings.
- `db/` contains SQLAlchemy configuration and models.
- `models/schemas.py` defines Pydantic request/response models.

## Development

- The project declares Python 3.14 and uses `uv`; make dependency changes in
  `pyproject.toml` and keep `uv.lock` consistent.
- Relevant configuration is provided through environment variables, including
  `DB_URL`, `LLM_API_KEY`, `LLM_MODEL`, `MOCK_DIALOGUES_URL`, and
  `SMART_SUGGEST_MICROSERVICE_URL`. Never add credentials to source files.
- Check `startServer.sh`, the parent `Dockerfile`, and `docker-compose.yml` when
  changing how the application starts or what it requires at runtime.
- Add focused tests for new behavior and verify service contracts against the
  frontend and dependent services. Do not treat successful Python compilation as
  proof that the service starts or its HTTP contracts work.
