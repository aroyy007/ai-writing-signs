# Pattern catalog

Each pattern: what it looks like → fix. Tag in brackets = scanner category
(`judgment` = scanner can't see it). Patterns are overrepresented in LLM output, not
exclusive to it; human writing influenced by LLM-heavy blogs/LinkedIn drifts the same way.

## A. Hard artifacts (red flag alone) [artifact]

- **Chatbot address:** "Certainly!", "Of course!", "Here is your …", "I hope this helps",
  "Let me know if …", "Would you like me to …", "more detailed breakdown", "As requested".
- **Refusals / cutoffs:** "As an AI language model …", "As of my last knowledge update …".
- **Unfilled templates:** `[Insert statistic]`, `[Company Name]`, `(Add your URL here)`,
  `2025-XX-XX`, `INSERT_SOURCE_URL_30`, `example.com/source1`, `<!-- Add if available -->`.
- **Leaked tool markup:** `contentReference[oaicite:1]`, `oaicite`, `turn0search0`,
  `【…†source】`, attribution JSON, footnote return arrows `↩` in plain prose.
- **Tracking params in citations:** `utm_source=chatgpt.com`, `utm_source=openai`,
  `utm_source=copilot.com`, `referrer=grok.com`.
- **Markdown in a non-markdown target** (Word, LaTeX, wiki, email): `**bold**`, `#` headings,
  `---` rules, `[text](url)`, fenced code blocks.

Fix: delete or fill. These are editing failures, not style.

## B. Vocabulary [vocab]

Era lists help date text; one word is weak evidence, clusters are strong. Replace with the
plain word or cut (utilize→use, commence→start, facilitate→help, leverage→use).

- **GPT-4 (2023–mid-24):** additionally (sentence-initial), boasts, bolstered, crucial,
  delve, emphasizing, enduring, garner, intricate/intricacies, interplay, landscape
  (abstract), meticulous(ly), pivotal, underscore, tapestry, testament, valuable, vibrant.
- **GPT-4o (mid-24–mid-25):** align with, enhance, fostering, highlighting, showcasing,
  plus the above.
- **GPT-5 (mid-25–mid-26):** emphasizing, enhance, highlighting, showcasing; shift to
  notability/attribution language (§D) rather than flashy adjectives.
- **GPT-6 (mid-26 on):** leverage, multifaceted, foster, prioritize, quietly, steady,
  dependable, echoed, universally; weaker: challenge, clearer, practical, matters.
  Prose gets more periods/commas and uniform 8–20-word sentences instead of em dashes.
- **Grok:** causal, empirical, correlate, underscore.
- **Perennial:** realm, beacon, commendable, paramount, noteworthy, robust, holistic,
  seamless, cutting-edge, ever-evolving, navigate/journey/unlock/unleash (metaphorical),
  deep dive, game-changer, in today's fast-paced world.
- **Spelling mismatch:** American spelling in otherwise British/Commonwealth text.

## C. Sentence templates

- **Copula avoidance** [copula]: "serves as / stands as / functions as / represents / marks a",
  "boasts / features / offers a", "refers to" in a definition. Fix: use "is"/"has".
- **Negative parallelism** [negpar]: "not just X, but Y", "It's not X, it's Y",
  "isn't a setback — it's an opportunity", "no X, no Y, just Z", and the newer reversed
  "Y rather than X". Fix: state Y once.
- **Tailing -ing clause** [tailing]: fact + ", highlighting / underscoring / reflecting /
  ensuring / contributing to / fostering …". Fix: delete; if the significance is real, give
  it its own sentence with content.
- **Significance inflation** [significance]: "plays a pivotal role", "is a testament to",
  "marks a significant milestone", "indelible mark", "setting the stage for", "evolving
  landscape", "reflects broader trends", "deeply rooted". Fix: scale the claim to the fact.
- **Rule of three** [judgment]: reflexive triplets of adjectives or clauses. Test: does the
  third add anything? Cut to what differs.
- **False range** [falserange]: "from intimate gatherings to global movements". No real
  spectrum between the ends. Fix: name the two things or drop the frame.
- **Editorial asides / disclaimers** [editorial]: "It's important to note", "It's worth
  noting", "based on available information", "not widely documented", "maintains a low
  profile", and the 2026 forms "should be treated as … rather than …", "does not
  establish", "should not be confused with". Fix: cut, or make it a sourced claim.
- **Compulsive summary** [summary]: "In summary / In conclusion / Overall / Ultimately"
  after a short passage. Fix: cut unless the section is long.
- **Elegant variation** [judgment]: renaming the same thing each mention ("the artists" →
  "the non-conformist collective" → "the group"). Fix: repeat the noun.

## D. Attribution and content

- **Vague attribution** [vagueattr]: "studies show", "experts argue", "observers have
  noted", "industry reports", "several sources" (with few cited). Most consequential in
  factual writing: often covers an unverified claim. Fix: name the source or flag it.
  Never invent one.
- **Vague association** [association]: "in connection with", "associated with",
  "particularly associated with". Fix: say what the relationship is.
- **Notability / media framing** [notability]: "has garnered attention", "featured in
  national media outlets", "independent coverage", "maintains an active social media
  presence", "databases/records list X as". Describes sources instead of saying what
  they say.
- **Promotional tone in a neutral register** [promo]: nestled, in the heart of,
  breathtaking, renowned, rich heritage, must-visit, world-class.
- **Superficial analysis** [judgment]: claims that fit any topic ("reflects a growing
  trend") with no mechanism, number, or example.
- **Template structure** [judgment]: "Challenges", "Future Outlook", "Despite these
  challenges…", "Awards and recognition" sections bolted onto unrelated topics;
  "X and Y" headings everywhere.

## E. Formatting and typography [typography]

- Bold on every key term or every bullet lead ("**Term:** definition").
- Inline-header bullet lists where prose would connect the ideas.
- Title Case Headings (vs sentence case), wrong heading levels, multiple H1s.
- Emoji as heading prefixes or bullets in formal registers.
- Curly quotes in a context that otherwise uses straight quotes (paste artifact).
- Spaced em dashes ("the request — not the answer —") where comma/colon/parentheses fit.
  Strong-ish 2022–Sept 2026; newer models avoid them, so absence proves nothing.
- Hyphen instead of en dash for ranges (1990-2000).

## F. Invisible characters [invisible]

Zero-width space U+200B, ZWNJ/ZWJ U+200C/D outside scripts that need them, word joiner
U+2060, BOM U+FEFF mid-text, soft hyphen U+00AD, bidi controls U+202A–202E/U+2066–2069,
tag characters U+E0000–E007F, other Cf characters, noncharacters (U+FDD0–FDEF, xFFFE/xFFFF),
blank-rendering fillers U+3164/U+FFA0/U+180F, exotic spaces (U+2000–200A, U+202F, U+205F).
These come from copy-paste, rich-text editors, or deliberate watermarking. Strip with
`scan.py --clean` (keeps NBSP and ZWJ/ZWNJ inside non-Latin scripts and emoji sequences).
Statistical token watermarks can't be detected or removed this way; don't claim otherwise.

## G. Ineffective indicators (do not flag on these alone)

Perfect grammar; "robotic" or "fancy" prose; mixed registers; transition words alone
("Additionally"); unsourced content; em dashes alone; abrupt cut-offs; old dates;
a detector score. Non-native writers and some school traditions avoid repetition and use
formal transitions naturally.

## H. Signs of human writing

Text predating 30 Nov 2022; author can explain their choices; unspaced em dashes
(typeset style); plain constructions like "there is a", "wrote" (not "authored"),
"perhaps", "in order to"; deliberate repetition of the same noun; specific, checkable
detail; uneven sentence lengths; small idiosyncrasies.

## Write-mode filter

Before handing over prose meant to read as human-authored:

- [ ] No §A artifacts, no markdown in a non-markdown target.
- [ ] "is/has" instead of "serves as/boasts"; no "not X but Y" unless it's doing real work.
- [ ] No tailing -ing significance clauses; no inflated stakes.
- [ ] Every factual claim has a named source, number, or example, or is cut.
- [ ] Lists only where items are genuinely parallel; prose otherwise. Bold sparingly.
- [ ] Sentence length varies (some short, some long); not a uniform 15-word metronome.
- [ ] Same thing, same name. No synonym cycling.
- [ ] No closing summary on a short piece; no "let me know" sign-off in standalone text.
- [ ] Match the user's spelling variant and punctuation habits.

## Density rule of thumb

3+ distinct patterns in one paragraph → flag the paragraph. One tell in a clean
2,000-word piece → don't mention it.
