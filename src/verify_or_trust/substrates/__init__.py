"""Substrate builders — produce the (FM prediction, real label, per-edge correctness) table a benchmark needs.

Each substrate downloads its inputs FROM SOURCE (we do not redistribute licensed third-party data):
  - gears_norman: GEARS (MIT) predictions on Norman 2019 (public, GEO) vs a sceptre ground truth.
  - state_tahoe:  Arc Institute STATE (ST-HVG-Tahoe) released predictions vs real DE — NOTE: Arc's model/data are
                  under a NON-COMMERCIAL license; this builder downloads them from Arc's Hugging Face repo and you
                  must accept Arc's terms. See data/README.md and CARD.md.
"""
