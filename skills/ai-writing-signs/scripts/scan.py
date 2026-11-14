#!/usr/bin/env python3
"""Scan text for mechanical signs of unedited AI writing.

Usage:
  scan.py FILE|-            text report
  scan.py FILE --json       JSON report
  scan.py FILE --clean [-o OUT] [--spaces]
                            strip invisible/format Unicode; write cleaned text

Heuristic only. Hits are candidates for a human (or model) to confirm in context.
Stdlib only, Python 3.9+.
"""
import argparse
import json
import re
import sys
import unicodedata
from collections import Counter, defaultdict

# --------------------------------------------------------------------------
# Pattern tables: (category, weight, [regex, ...]). Case-insensitive, \b-bounded
# where it makes sense. Edit here; references/patterns.md explains each category.
# --------------------------------------------------------------------------

def words(*ws):
    return [r"\b" + w + r"\b" for w in ws]

PATTERNS = [
    ("artifact", 5.0, [
        r"\bas an ai (language )?model\b", r"\bas of my (last )?knowledge (update|cutoff)\b",
        r"\bi hope this helps\b", r"^\s*(certainly|of course|absolutely|great question)[!,.]",
        r"\blet me know if\b", r"\bwould you like me to\b", r"\bhere(?:'s| is) (?:your|the|a) (?:revised|updated|draft|article|summary|essay|version)\b",
        r"\bas requested\b", r"\bmore detailed breakdown\b",
        r"\[(?:insert|add|describe|your|placeholder|company name|founder)[^\]\n]{0,60}\]",
        r"\((?:add|insert) your [^)\n]{0,40}\)",
        r"\b20\d\d-XX-XX\b", r"\bINSERT_[A-Z_]+\d*\b", r"\bexample\.com/source\d*\b",
        r"contentReference\[", r"\boaicite\b", r"\bturn\d+(?:search|news|view)\d+\b", r"【[^】]{0,40}†[^】]{0,40}】",
        r"utm_source=(?:chatgpt\.com|openai|copilot\.com|perplexity)", r"referrer=grok\.com",
    ]),
    ("vocab", 1.0, words(
        "delve[sd]?", "delving", "tapestry", "testament", "pivotal", "underscor(?:e|es|ed|ing)",
        "meticulous(?:ly)?", "intricac(?:y|ies)", "intricate", "interplay", "garner(?:ed|s|ing)?",
        "bolster(?:ed|s|ing)?", "boasts?", "vibrant", "enduring", "showcas(?:e|es|ed|ing)",
        "fosters?", "fostering", "fostered", "realm", "beacon", "multifaceted", "commendable",
        "paramount", "noteworthy", "holistic", "seamless(?:ly)?", "cutting-edge", "ever-evolving",
        "game-changer", "deep dive", "unleash(?:es|ed|ing)?", "leverag(?:e|es|ed|ing)",
        "utiliz(?:e|es|ed|ing)", "facilitat(?:e|es|ed|ing)", "commenc(?:e|es|ed|ing)",
        "quietly", "universally", "dependable", "prioritiz(?:e|es|ed|ing)",
        "landscape", "crucial", "align(?:s|ed)? with", "enhanc(?:e|es|ed|ing)",
        "fast-paced world", "in today's [a-z-]+ (?:world|landscape|era)",
    ) + [r"(?:^|[.!?]\s+)Additionally,"]),
    ("copula", 1.0, [
        r"\b(?:serves|stands|functions|operates) as (?:a|an|the)\b",
        r"\b(?:boasts|features) (?:a|an)\b", r"\brefers to (?:a|an|the)\b",
    ]),
    ("negpar", 2.0, [
        r"\bnot (?:just|only|merely|simply)\b[^.?!\n]{0,80}\bbut\b",
        r"\b(?:it|this|that)(?:'s| is)n?(?:'t| not)\b[^.?!\n]{0,60}[,;:—–-]\s*(?:it|this|that)(?:'s| is)\b",
        r"\bisn't (?:just )?(?:a|an|about)\b[^.?!\n]{0,50}—",
        r"\bno [a-z]+, no [a-z]+, just\b",
    ]),
    ("tailing", 2.0, [
        r",\s+(?:highlighting|underscoring|emphasizing|showcasing|reflecting|symbolizing|ensuring|"
        r"contributing to|fostering|cultivating|illustrating|cementing|solidifying|marking|"
        r"signaling|signalling|paving the way|setting the stage)\b",
    ]),
    ("significance", 2.0, [
        r"\b(?:pivotal|crucial|vital|significant|key|central|instrumental) role\b",
        r"\b(?:is|stands as|serves as) a testament\b", r"\btestament to\b",
        r"\b(?:significant|major|important|key) milestone\b", r"\bwatershed moment\b",
        r"\bindelible mark\b", r"\blasting (?:legacy|impact)\b", r"\bsetting the stage for\b",
        r"\bevolving landscape\b", r"\breflects? (?:a )?broader\b", r"\bdeeply rooted\b",
        r"\bkey turning point\b", r"\bfocal point\b", r"\bmarks? a (?:shift|turning point)\b",
    ]),
    ("falserange", 1.0, [
        r"\bfrom (?:the )?(?!\d)[a-z][a-z -]{2,25} to (?:the )?(?!\d)[a-z][a-z -]{2,25},",
    ]),
    ("editorial", 1.0, [
        r"\bit(?:'s| is) (?:important|crucial|essential|worth) (?:to note|noting|mentioning)\b",
        r"\bit should be noted\b", r"\bno discussion (?:of [^,]+ )?would be complete\b",
        r"\bbased on (?:the )?available information\b", r"\bnot widely documented\b",
        r"\bnot publicly available\b", r"\bmaintains a low profile\b",
        r"\bshould be treated as\b[^.\n]{0,60}\brather than\b", r"\bdoes not establish\b",
    ]),
    ("summary", 1.0, [
        r"(?:^|\n)\s*(?:In summary|In conclusion|Overall|Ultimately|In essence|To sum up)\b,?",
    ]),
    ("vagueattr", 2.0, [
        r"\b(?:studies|research|reports) (?:show|suggest|indicate)s?\b", r"\bexperts (?:argue|agree|say|note|believe)\b",
        r"\bobservers have (?:noted|cited|pointed)\b", r"\bsome critics argue\b", r"\bindustry reports\b",
        r"\bmany (?:believe|argue|experts)\b", r"\bit is widely (?:believed|accepted|recognized)\b",
        r"\bseveral (?:sources|publications)\b",
    ]),
    ("association", 1.0, [
        r"\b(?:in connection with|in association with)\b", r"\b(?:particularly|widely|closely) associated with\b",
    ]),
    ("notability", 1.0, [
        r"\bhas garnered (?:significant |widespread |considerable )?(?:attention|recognition|acclaim)\b",
        r"\b(?:independent|widespread|national|regional|local) (?:media )?coverage\b",
        r"\b(?:media|news|trade|tech|business) (?:outlets|publications)\b",
        r"\b(?:maintains|has) an? (?:active|strong) (?:social media|online|digital) presence\b",
        r"\b(?:databases|records|listings|filings) (?:identify|list|describe)\b",
    ]),
    ("promo", 1.5, words(
        "nestled", "in the heart of", "breathtaking", "renowned", "must-visit", "world-class",
        "rich (?:cultural )?(?:heritage|history|tapestry)", "stunning", "unparalleled",
    )),
    ("academic", 1.0, words(
        "groundbreaking", "paradigm shift", "revolutioniz(?:e|es|ed|ing)", "unprecedented",
        "remarkabl(?:e|y)", "superior performance", "sheds? light on", "paves? the way",
        "fills? (?:this|the|a) gap", "a growing body of", "opens? (?:up )?new avenues",
        "valuable insights", "extensive experiments", "comprehensive (?:analysis|overview|review|study)",
        "has (?:attracted|received) (?:significant|increasing|growing) attention",
        "with the rapid (?:development|advancement|growth) of", "in recent years",
    ) + [r"(?:^|[.!?]\s+)(?:Furthermore|Moreover),"]),
]

COMPILED = [(cat, w, [re.compile(p, re.I | re.M) for p in pats]) for cat, w, pats in PATTERNS]
# Sentence-initial patterns must stay case-sensitive.
COMPILED = [(c, w, [re.compile(r.pattern, re.M) if r.pattern.startswith("(?:^|[.!?]") or r.pattern.startswith("(?:^|\\n)") else r for r in rs]) for c, w, rs in COMPILED]

# --------------------------------------------------------------------------
# Invisible / format characters
# --------------------------------------------------------------------------
EXOTIC_SPACES = set(range(0x2000, 0x200B)) | {0x202F, 0x205F, 0x3000, 0x1680}
BLANK_FILLERS = {0x3164, 0xFFA0, 0x180F, 0x115F, 0x1160}
KEEP_IN_CONTEXT = {0x200C, 0x200D}  # ZWNJ/ZWJ: needed in Indic/Arabic scripts and emoji sequences


def is_nonchar(cp):
    return 0xFDD0 <= cp <= 0xFDEF or (cp & 0xFFFE) == 0xFFFE


def char_kind(ch):
    cp = ord(ch)
    if ch in "\n\t\r":
        return None
    if cp in BLANK_FILLERS:
        return "blank-filler"
    if is_nonchar(cp):
        return "noncharacter"
    if 0xE0000 <= cp <= 0xE007F:
        return "tag-char"
    if cp in (0x202A, 0x202B, 0x202C, 0x202D, 0x202E) or 0x2066 <= cp <= 0x2069:
        return "bidi-control"
    if cp in EXOTIC_SPACES:
        return "exotic-space"
    if cp == 0x00A0:
        return "nbsp"
    if unicodedata.category(ch) == "Cf":
        return {0x200B: "zero-width-space", 0x200C: "zwnj", 0x200D: "zwj", 0x2060: "word-joiner",
                0xFEFF: "bom/zwnbsp", 0x00AD: "soft-hyphen"}.get(cp, "format-Cf")
    return None


def _needs_joiner(text, i):
    """ZWJ/ZWNJ is legitimate between two non-ASCII letters/symbols (scripts, emoji)."""
    prev = text[i - 1] if i > 0 else ""
    nxt = text[i + 1] if i + 1 < len(text) else ""
    return bool(prev and nxt and ord(prev) > 0x7F and ord(nxt) > 0x7F)


def scan_invisible(text):
    counts = Counter()
    for i, ch in enumerate(text):
        k = char_kind(ch)
        if not k:
            continue
        if ord(ch) in KEEP_IN_CONTEXT and _needs_joiner(text, i):
            continue
        if ord(ch) == 0xFEFF and i == 0:
            continue
        counts[k] += 1
    return counts


def clean(text, spaces=False):
    out = []
    for i, ch in enumerate(text):
        k = char_kind(ch)
        if not k:
            out.append(ch)
        elif k == "nbsp":
            out.append(" " if spaces else ch)
        elif k == "exotic-space":
            out.append(" ")
        elif ord(ch) in KEEP_IN_CONTEXT and _needs_joiner(text, i):
            out.append(ch)
        # everything else dropped
    return "".join(out)

# --------------------------------------------------------------------------
# Typography stats
# --------------------------------------------------------------------------

def typography(text):
    lines = text.splitlines()
    heads = [l.lstrip("# ").strip() for l in lines if re.match(r"^#{1,6}\s", l)]
    title_case = sum(1 for h in heads if len(h.split()) >= 3 and
                     sum(w[:1].isupper() for w in h.split()[1:]) >= len(h.split()[1:]) * 0.8)
    emoji_lead = sum(1 for l in lines if re.match(r"^\s*(?:[-*]\s*)?[\U0001F300-\U0001FAFF☀-➿]", l))
    return {
        "em_dash": text.count("—"),
        "spaced_em_dash": len(re.findall(r" — ", text)),
        "curly_quotes": len(re.findall(r"[“”‘’]", text)),
        "markdown_bold": len(re.findall(r"\*\*[^*\n]+\*\*", text)),
        "bold_lead_bullets": len(re.findall(r"^\s*[-*\d.]+\s+\*\*[^*]+:\*\*", text, re.M)),
        "md_headings": len(heads),
        "title_case_headings": title_case,
        "emoji_line_starts": emoji_lead,
        "hyphen_ranges": len(re.findall(r"\b(?:1[89]|20)\d\d-(?:1[89]|20)?\d\d\b", text)),
    }

# --------------------------------------------------------------------------

def paragraphs(text):
    """Yield (start_line, paragraph_text)."""
    line = 1
    for block in re.split(r"(\n\s*\n)", text):
        if block.strip() and not re.fullmatch(r"\n\s*\n", block):
            lead = len(block) - len(block.lstrip("\n"))
            yield line + lead, block.strip("\n")
        line += block.count("\n")


def scan(text):
    paras = []
    totals = Counter()
    total_score = 0.0
    total_words = 0
    for start, p in paragraphs(text):
        nwords = len(re.findall(r"\b\w+\b", p))
        total_words += nwords
        hits = defaultdict(list)
        score = 0.0
        for cat, w, regs in COMPILED:
            for r in regs:
                for m in r.finditer(p):
                    hits[cat].append(m.group(0).strip())
                    score += w
        if hits:
            for c, hs in hits.items():
                totals[c] += len(hs)
            total_score += score
            paras.append({
                "line": start, "words": nwords, "score": round(score, 1),
                "categories": len(hits), "hits": {c: hs for c, hs in hits.items()},
                "preview": re.sub(r"\s+", " ", p)[:90],
            })
    density = round(100 * total_score / total_words, 2) if total_words else 0.0
    if totals["artifact"]:
        verdict = "hard artifacts present: remove before anything else"
    elif density < 1.5:
        verdict = "low density: likely reads clean"
    elif density < 4:
        verdict = "moderate: a few tics worth cutting"
    else:
        verdict = "high density: structural rewrite, not word swaps"
    flagged = [p for p in paras if p["score"] >= 4 or p["categories"] >= 3 or "artifact" in p["hits"]]
    return {
        "words": total_words, "score": round(total_score, 1), "per_100_words": density,
        "verdict": verdict, "category_counts": dict(totals.most_common()),
        "invisible": dict(scan_invisible(text)), "typography": typography(text),
        "flagged_paragraphs": flagged, "all_paragraphs_with_hits": len(paras),
    }


def print_report(r):
    print(f"words={r['words']}  score={r['score']}  per100={r['per_100_words']}  -> {r['verdict']}")
    if r["category_counts"]:
        print("categories: " + ", ".join(f"{k}={v}" for k, v in r["category_counts"].items()))
    inv = r["invisible"]
    print("invisible: " + (", ".join(f"{k}={v}" for k, v in inv.items()) if inv else "none")
          + ("   (run --clean to strip)" if any(k != "nbsp" for k in inv) else ""))
    t = {k: v for k, v in r["typography"].items() if v}
    print("typography: " + (", ".join(f"{k}={v}" for k, v in t.items()) if t else "none"))
    fp = r["flagged_paragraphs"]
    print(f"\nflagged paragraphs: {len(fp)} of {r['all_paragraphs_with_hits']} with any hit")
    for p in sorted(fp, key=lambda x: -x["score"]):
        print(f"\n  L{p['line']}  score={p['score']}  cats={p['categories']}  words={p['words']}")
        print(f"    \"{p['preview']}...\"")
        for c, hs in p["hits"].items():
            uniq = list(dict.fromkeys(hs))
            print(f"    {c}: " + " | ".join(uniq[:6]) + (" ..." if len(uniq) > 6 else ""))


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("file", help="path or - for stdin")
    ap.add_argument("--json", action="store_true")
    ap.add_argument("--clean", action="store_true", help="strip invisible/format chars and output text")
    ap.add_argument("--spaces", action="store_true", help="with --clean, also convert NBSP to space")
    ap.add_argument("-o", "--out", help="with --clean, write here instead of stdout")
    a = ap.parse_args()
    text = sys.stdin.read() if a.file == "-" else open(a.file, encoding="utf-8", errors="replace").read()
    if a.clean:
        cleaned = clean(text, a.spaces)
        removed = len(text) - len(cleaned)
        if a.out:
            open(a.out, "w", encoding="utf-8").write(cleaned)
        else:
            sys.stdout.write(cleaned)
        print(f"[clean] removed {removed} chars; {dict(scan_invisible(text))}", file=sys.stderr)
        return
    r = scan(text)
    if a.json:
        json.dump(r, sys.stdout, ensure_ascii=False, indent=1)
        print()
    else:
        print_report(r)


if __name__ == "__main__":
    main()
