# Changelog

## 1.1.0 (2026-11-22)

- Tortured-phrase detection: synonym-spun technical terms from paraphrasing tools, using
  pairs verified against Cabanac et al. 2021 and the Problematic Paper Screener.
- Lookalike-letter detection: Cyrillic/Greek letters inside Latin words. `--clean`
  restores them; real Cyrillic/Greek words and maths symbols are left alone.
- Hidden-text detection in LaTeX/HTML source (white or zero-size text) and
  instructions aimed at AI reviewers.
- New reference sections on tampering and paraphrasing-tool traces, an integrity-check
  section for manuscript reviewers, and a ground rule against similarity laundering.
- SkillSpector: skill folder 7/100 SAFE. Test fixtures with adversarial samples are
  documented in `.skillspector-baseline.yaml`; test file no longer contains raw
  bidi/tag characters (which made v1.0.0's repo-root scan report 63/100).
- 32 tests (was 18), including negative tests for ordinary CSS, Greek notation
  (photon energy h-nu), common phrases and ML-evaluation wording.

## 1.0.0 (2026-11-14)

- Skill rewritten around the November 2026 revision of Wikipedia's "Signs of AI writing":
  GPT-6-era vocabulary, copula avoidance, vague association, notability framing,
  2026 hedging disclaimers, ineffective indicators, signs of human writing.
- New `scripts/scan.py`: per-paragraph density scoring, hard-artifact detection,
  typography stats, invisible-Unicode detection and `--clean`.
- New `references/academic.md`: over-claiming, claim–evidence discipline, grant proposals.
- Claude Code plugin manifest, tests, CI, `.skill` packaging.
