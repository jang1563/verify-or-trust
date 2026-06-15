# Data — provenance, licensing & regeneration

The benchmark **code** (this Git repo) ships no third-party data; inputs are regenerated from source or pulled from
the companion Hugging Face dataset, to respect upstream licenses. Running `vot panels --substrate <name>` downloads
what it needs into `data/raw/` and `data/cache/` (git-ignored).

**What is redistributed, and where:** the companion HF dataset (`jang1563/verify-or-trust`) hosts a *processed
subset of the **public** Norman 2019 cells* (GEO GSE133344) and the derived `gears_norman` substrate table, for
reproducibility of the live `run_de` assay. The Arc STATE/Tahoe outputs are **not** redistributed (non-commercial —
the builder downloads them from Arc's repo under Arc's terms; see below).

## Substrates

### `gears_norman` (public)
- **Norman 2019** CRISPRa perturb-seq (Norman et al., *Science* 2019; GEO **GSE133344**). Public. Shipped by the
  GEARS package as a processed AnnData; the builder fetches it through GEARS.
- **GEARS** (Roohani, Huang & Leskovec, *Nat. Biotechnology* 2024) — MIT license. The builder trains/loads GEARS
  and derives its per-(perturbation, gene) effect prediction.
- **Ground truth** — a held-out sceptre (Barry et al.) differential-expression three-state label, computed by the
  builder; and the cells themselves for the live `run_de` tool.

### `state_tahoe` (Arc Institute — NON-COMMERCIAL)
- **Arc STATE / ST-HVG-Tahoe** released model outputs (`*_pred_de.csv`, `*_real_de.csv`) downloaded from Arc's
  Hugging Face repo `arcinstitute/ST-HVG-Tahoe`. **These are under Arc's Model License + Acceptable Use Policy,
  which is non-commercial.** By running this substrate you download Arc's artifacts at your own request and agree
  to their terms; this repository neither hosts nor relicenses them.
- Gene identities in the Tahoe release are integer indices (not symbols), so the `query_gene` knowledge tool is
  not available for this substrate.

## What IS committed to this Git repo
Only our own artifacts: the panel manifest schema, the derived `gears_norman` substrate, small result tables
(`../results/`), and tests. No cells, no foundation-model outputs, no API keys. (The public Norman cell subset for
the live assay lives in the companion HF dataset, not here.)
