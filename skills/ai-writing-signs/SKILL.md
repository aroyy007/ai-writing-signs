---
name: ai-writing-signs
description: Audit or rewrite text for signs of unedited AI/LLM writing, or draft text that doesn't read as machine-generated. Covers vocabulary by model era, rhetorical templates, formatting/markup and citation artifacts, invisible Unicode, lookalike characters, hidden text, paraphrasing-tool "tortured phrases", and academic over-claiming. Use when the user asks to check for AI writing, humanize text, "does this sound like ChatGPT", audit for AI tells, clean pasted LLM output, check a manuscript for paraphrase-tool traces or hidden text, or when drafting papers, theses, proposals, emails, reviews, READMEs or posts meant to read as human-written.
license: MIT (scripts) and CC BY-SA 4.0 (instructions and references); see https://github.com/aroyy007/ai-writing-signs
---

# Signs of AI writing

Sources: Wikipedia "Signs of AI writing" (WikiProject AI Cleanup, Nov 2026 revision),
academic-humanizer (claim–evidence discipline), watermarks-remover (invisible Unicode),
Cabanac, Labbé & Magazinov 2021 and the Problematic Paper Screener (tortured phrases).

## Ground rules

1. **No single sign proves anything.** The signal is density and co-occurrence: several
   tells clustered in one paragraph, used mechanically. One em dash means nothing.
2. **Hard artifacts are the exception.** Leaked chatbot text (`oaicite`, `utm_source=chatgpt.com`,
   "I hope this helps", `[Insert …]`, knowledge-cutoff disclaimers) is a red flag on its own.
3. **Detectors are unreliable and humans guess near chance.** Never claim text will "pass"
   a detector, and never optimize for one. The goal is better writing, not evasion. If the
   user's venue requires AI-use disclosure, the rewrite does not change that.
4. **Never alter facts.** Numbers, equations, citations, quotes, names, code, and technical
   terms stay as they are. Never invent sources, data, or attributions to replace vague ones;
   flag them for the author instead.
5. **Report patterns, not authorship.** Don't accuse the user. If asked directly, answer
   with the density read, not a verdict on who wrote it.
6. **No similarity laundering.** Don't help lower a plagiarism or similarity score, or
   disguise someone else's text, whether by spinning synonyms, reshuffling syntax,
   placing citations to break up matched spans, or inserting lookalike or invisible
   characters. When text overlaps a source, the fix is to quote it, cite it, or rewrite it
   from the author's own understanding of the source.

## Step 0: scan (always, for any text over ~150 words)

```bash
python3 -I scripts/scan.py FILE            # or: pbpaste | python3 -I scripts/scan.py -
python3 -I scripts/scan.py FILE --json     # machine-readable
python3 -I scripts/scan.py FILE --clean -o CLEAN   # strip invisible chars, fix lookalike letters
```

(Path is relative to this skill's directory.) The scanner catches the mechanical tells:
hard artifacts, era vocabulary, phrase templates, invisible characters, typography stats,
and per-paragraph density. It also finds signs of tampering: tortured phrases
(synonym-spun technical terms), Cyrillic/Greek lookalikes inside Latin words, and
white or zero-size text and reviewer-directed instructions in LaTeX/HTML source. Scan the
`.tex` or HTML source, not a rendered PDF, or the hidden-text check sees nothing. It cannot judge rule-of-three padding, superficial analysis,
elegant variation, false ranges in context, or whether a word is earning its place. That
part is yours: read the flagged paragraphs, then the rest, against `references/patterns.md`.

Treat scanner hits as candidates. A hit inside a quotation, a technical term
("key" in cryptography, "robust" in statistics), or a citation title is not a tell.

## Modes

**Audit** (user wants a check): scan → read whole text → confirm/reject hits → add the
judgment-only patterns → report (format below). Don't rewrite unless asked.

**Rewrite / humanize** (user wants it fixed): audit first, then edit only what's flagged.
Keep the author's voice, structure, and any phrasing that isn't a tell. Re-run the scanner
on the result; the score should drop and no hard artifacts should remain. Return the
cleaned text plus a short change log.

**Write** (you are drafting something meant to read as human-authored): no report. Before
finishing, check your own draft against the "Write-mode filter" in `references/patterns.md`
and run the scanner if it's long.

**Academic / proposal text**: also load `references/academic.md` (over-claiming,
claim–evidence matching, novelty padding, what hedging to keep).

## Audit output format

| # | Quote (exact) | Pattern | Fix |
|---|---|---|---|

Then:
- **Hard artifacts:** list, or "none".
- **Invisible characters:** count by type from the scanner, or "none".
- **Tampering:** tortured phrases, lookalike characters, hidden text, or "none". Report
  what was found and where; it shows the text was processed, not who did it or why.
- **Density:** which paragraphs/sections cluster hits. This is the finding; the raw count isn't.
- **Verdict:** one of *reads clean* / *a few tics worth cutting* / *dense in §X, needs a
  structural rewrite, not word swaps*.

Skip the table entirely if the text is clean; say so in one line.

## References

- `references/patterns.md`: full catalog with fixes, ineffective indicators, signs of
  human writing, write-mode filter. Read before any audit or rewrite.
- `references/academic.md`: papers, theses, rebuttals, grant proposals.
- `scripts/scan.py`: stdlib-only scanner (Python 3.9+). Edit its word lists there.
