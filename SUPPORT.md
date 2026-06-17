# Support

This repository is a public research benchmark. The best support path depends on
the type of request.

## Use GitHub Issues For

- Reproducibility bugs in documented commands.
- Broken paths in `artifact_manifest.json`.
- Substrate CSV, panel JSONL, or schema-validation problems.
- Documentation, provenance, or citation corrections.
- Questions about release boundaries for included artifacts.

## Use Hugging Face For Downloads

- Verify-or-Trust benchmark data:
  `https://huggingface.co/datasets/jang1563/verify-or-trust`

## Before Opening An Issue

Please run:

```bash
python3 scripts/validate_public_release.py
```

For local benchmark behavior, also include the relevant `vot ...` command or
`make reproduce` output. Do not attach raw upstream datasets, local run
directories, access tokens, or unpublished data.
