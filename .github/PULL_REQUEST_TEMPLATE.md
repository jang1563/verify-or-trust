## Summary

- What changed:
- Why it is needed:

## Release-Surface Checklist

- [ ] `python3 scripts/validate_public_release.py` passes.
- [ ] Tests pass with `pytest`.
- [ ] `make reproduce` still reproduces the LLM-free value proof when benchmark logic changes.
- [ ] New or changed artifacts are reflected in `artifact_manifest.json`.
- [ ] New or changed schema fields are reflected in `SCHEMA.md` and `schemas/`.
- [ ] No local runs, secrets, access tokens, Arc STATE / Tahoe artifacts, or large upstream data files were added.

## Notes

Add any caveats, heavy-regeneration steps, or external-data requirements here.
