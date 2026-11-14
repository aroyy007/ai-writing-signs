# Academic and proposal text

Load for papers, theses, rebuttals, reviews, and grant proposals (NSF, NIH, ERC, etc.).
Adapted from academic-humanizer's layered approach. Applies on top of `patterns.md`.

## Preserve (do not "humanize" these away)

- Calibrated hedging that reflects real uncertainty ("suggests", "may", "in our setting").
- Passive voice where the actor is irrelevant; "we" where the field uses it.
- Semicolons, formal definitions, technical terms, equations, notation.
- Numbers, citation keys, figure/table refs, quotes: never alter, never invent.

## Academic tells [academic]

- **Over-claiming verbs:** "proves", "demonstrates conclusively", "solves", "establishes"
  for what the evidence only supports. Fix: match the verb to the evidence (shows → suggests
  when n is small or effect untested).
- **Significance hype:** "groundbreaking", "paradigm shift", "revolutionize", "unprecedented",
  "remarkable", "superior performance".
- **Novelty padding:** "To the best of our knowledge, this is the first …" without a search
  claim to back it; "novel" on every noun.
- **Formulaic openers:** "In recent years, X has garnered significant attention", "X plays a
  crucial role in Y", "With the rapid development of …".
- **Empty intensifiers:** "significantly" without a test; "extensive experiments";
  "comprehensive analysis"; "highly effective".
- **Connective overuse:** "Furthermore / Moreover / Additionally" opening consecutive sentences.
- **Generic contribution lists:** three bullets that restate the abstract.
- **Stock gap/impact phrases:** "sheds light on", "paves the way for", "fills this gap",
  "a growing body of literature", "opens new avenues", "valuable insights".
- **Citation dumping:** [3–14] on a generic claim instead of the 1–2 that support it.
- **Overlong sentences** carrying three claims; split them.

## Claim–evidence discipline

Every empirical claim needs a number, figure, table, or citation. Vague magnitudes
("substantially better") become the actual delta against the strongest baseline. If the
evidence isn't in the text, flag `[needs evidence: …]` for the author; don't make it up.

## Grant proposals

Vision and ambition language is expected; keep it. Shift the discipline to
claim–feasibility matching:

- First page carries the weight: hook, gap, central idea, aims, payoff, in that order.
- Aims should name a question, not a technique; avoid aims that depend on each other
  succeeding.
- Replace vague importance ("this is critical for society") with who benefits and how much.
- Broader-impacts boilerplate → concrete activities with owners.
- State the central hypothesis plainly; don't hedge it into nothing.
- Never invent preliminary data, partners, letters, or funding. Flag gaps.

## Output for academic rewrites

Cleaned text, a change log (patterns removed; claims softened or given evidence pointers;
`[needs evidence]` flags), and an explicit line confirming no numbers, equations, or
citations changed.
