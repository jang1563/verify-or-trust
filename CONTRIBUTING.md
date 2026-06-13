# Contributing

Thanks for your interest. This is a research benchmark; contributions that improve correctness, reproducibility,
or add substrates are very welcome.

## Dev setup
```bash
pip install -e ".[agent,dev]"
pytest          # tests must pass
ruff check src tests
```

## Ground rules
- **Every numerical claim is gated by a test or a one-command reproduction** (`make reproduce`). New components
  must add their gate (see `RELEASE.md`).
- **No hardcoded paths, no private dependencies, no secrets.** API keys come from the environment.
- **Do not redistribute licensed third-party data.** Substrates download from source (see `data/README.md`).
- Keep the public surface honest — limitations belong in `CARD.md`, not buried.

## Adding a substrate
Implement `verify_or_trust/substrates/<name>.build_substrate` to emit the table in `SCHEMA.md`, downloading inputs
from source. Add a builder test or a documented heavy-regeneration path.
