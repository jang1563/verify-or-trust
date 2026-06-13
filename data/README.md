# Data — provenance & regeneration (we do not redistribute third-party data)

This benchmark **regenerates** its inputs from source rather than shipping them, to respect upstream licenses.
Running `vot panels --substrate <name>` downloads what it needs into `data/raw/` and `data/cache/` (git-ignored).

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

## What IS committed here
Only our own artifacts: the panel manifest schema, small result tables (`../results/`), and tests. No cells, no
foundation-model outputs, no API keys.
