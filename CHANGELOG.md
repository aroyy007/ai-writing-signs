# Changelog

## 1.1.0 (2026-11-22)

- Tortured-phrase detection: synonym-spun technical terms from paraphrasing tools, using
  pairs verified against Cabanac et al. 2021 and the Problematic Paper Screener.
- Lookalike-letter detection: Cyrillic/Greek letters inside Latin words. `--clean`
  restores them; real Cyrillic/Greek words and maths symbols are left alone.
- Hidden-text detection in LaTeX/HTML source (white, zero-size, zero-opacity text) and
  instructions aimed at AI reviewers.
- New reference sections on tampering and paraphrasing-tool traces, an integrity-check
  section for manuscript reviewers, and a ground rule against similarity laundering.
- 27 tests (was 18).

## 1.0.0 (2026-11-14)

- Skill rewritten around the November 2026 revision of Wikipedia's "Signs of AI writing":
  GPT-6-era vocabulary, copula avoidance, vague association, notability framing,
  2026 hedging disclaimers, ineffective indicators, signs of human writing.
- New `scripts/scan.py`: per-paragraph density scoring, hard-artifact detection,
  typography stats, invisible-Unicode detection and `--clean`.
- New `references/academic.md`: over-claiming, claim–evidence discipline, grant proposals.
- Claude Code plugin manifest, tests, CI, `.skill` packaging.
