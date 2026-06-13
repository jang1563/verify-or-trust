# Release process (verification-gated)

This repo is ported from research code with a **gate at every step** — nothing proceeds until the gate is green.
Quality bar: a stranger can clone, `pip install -e .`, run one command, and reproduce the headline numbers; no
hardcoded paths, no private deps, no secrets; licensed data is downloaded-from-source, never redistributed.

| step | component | gate (must pass) | status |
|---|---|---|---|
| 2 | repo skeleton (pkg, pyproject, license, CLI, stubs) | `pip install -e .` + `pytest` green | ✅ |
| 3a | panels builder + CLI | panels regenerate research set faithfully (110 panels, gene-set & n_wrong match) + fixture tests | ✅ |
| 3b | GEARS substrate table SHIPPED (public-derived, redistributable) -> benchmark runs immediately. state_tahoe builder (Arc HF) + gears regeneration builder: pending | ◑ |
| 4 | baselines | K1 reproduces on research panels (oracle +23.4% vs random) + fixture tests | ✅ |
| 5 | grader | re-grades the research no-hint episodes to the EXACT published numbers + oracle-episode test | ✅ |
| 6 | env + tools (live DE, query_gene, equivalence, Anthropic SDK, key via env) | mocked-LLM dry-run + LIVE 1-panel run + grade all green | ✅ |
| 7 | CARD + README + results tables (with caveats) | "stranger" read-through: quickstart runs as written | ☐ |
| 8 | Makefile reproduce (panels + K1 from committed GEARS substrate) | clean checkout: panels + K1 reproduce (+23.4%) | ✅ |
| 9 | private GitHub (jang1563/verify-or-trust) + private HF dataset (jang1563/verify-or-trust) — both pushed | ✅ |
| 10 | flip public | separate decision | ☐ |
