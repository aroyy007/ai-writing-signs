import importlib.util
import json
import subprocess
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "skills" / "ai-writing-signs" / "scripts" / "scan.py"
FIX = Path(__file__).resolve().parent / "fixtures"

spec = importlib.util.spec_from_file_location("scan", SCRIPT)
scan = importlib.util.module_from_spec(spec)
spec.loader.exec_module(scan)


def cats(text):
    return scan.scan(text)["category_counts"]


class TestDensity(unittest.TestCase):
    def test_ai_sample_is_dense_with_artifacts(self):
        r = scan.scan((FIX / "ai_sample.txt").read_text(encoding="utf-8"))
        self.assertIn("artifact", r["category_counts"])
        self.assertGreater(r["per_100_words"], 10)
        self.assertTrue(r["verdict"].startswith("hard artifacts"))
        self.assertEqual(len(r["flagged_paragraphs"]), 4)

    def test_human_sample_is_clean(self):
        r = scan.scan((FIX / "human_sample.txt").read_text(encoding="utf-8"))
        self.assertEqual(r["score"], 0)
        self.assertEqual(r["flagged_paragraphs"], [])
        self.assertTrue(r["verdict"].startswith("low density"))

    def test_empty_text(self):
        r = scan.scan("")
        self.assertEqual(r["words"], 0)
        self.assertEqual(r["per_100_words"], 0.0)


class TestPatterns(unittest.TestCase):
    def test_artifacts(self):
        for s in ["As an AI language model, I cannot.", "See contentReference[oaicite:1].",
                  "Founded on 2025-XX-XX by [Founder Names].",
                  "https://a.org/x?utm_source=chatgpt.com", "I hope this helps!"]:
            with self.subTest(s=s):
                self.assertIn("artifact", cats(s))

    def test_negative_parallelism(self):
        self.assertIn("negpar", cats("It is not just a tool, but a movement."))
        self.assertIn("negpar", cats("This isn't a setback — it's an opportunity."))

    def test_tailing_clause(self):
        self.assertIn("tailing", cats("Sales rose 4% in May, highlighting the shift in demand."))

    def test_copula(self):
        self.assertIn("copula", cats("The library serves as a hub for the town."))

    def test_vague_attribution(self):
        self.assertIn("vagueattr", cats("Experts argue that the policy failed."))

    def test_sentence_initial_additionally_is_case_sensitive(self):
        self.assertIn("vocab", cats("It rained. Additionally, it snowed."))
        self.assertNotIn("vocab", cats("we additionally, briefly, note it"))

    def test_numeric_range_is_not_false_range(self):
        self.assertNotIn("falserange", cats("Prices went from 10 to 20, then fell."))

    def test_plain_prose_has_no_hits(self):
        self.assertEqual(cats("The meeting moved to Thursday because Sam is out on Wednesday."), {})


class TestInvisible(unittest.TestCase):
    def test_detect_and_clean(self):
        t = "a​b­c‮d \U000E0041e f"
        inv = scan.scan_invisible(t)
        for k in ("zero-width-space", "soft-hyphen", "bidi-control", "tag-char", "exotic-space"):
            self.assertIn(k, inv)
        self.assertEqual(scan.clean(t), "abcd e f")

    def test_keeps_joiners_in_scripts_and_emoji(self):
        hindi = "क्‍ष"
        family = "\U0001F468‍\U0001F469"
        self.assertEqual(scan.clean(hindi), hindi)
        self.assertEqual(scan.clean(family), family)
        self.assertEqual(scan.scan_invisible(hindi + " " + family), {})

    def test_nbsp_kept_unless_spaces_flag(self):
        self.assertEqual(scan.clean("a b"), "a b")
        self.assertEqual(scan.clean("a b", spaces=True), "a b")

    def test_leading_bom_ignored(self):
        self.assertEqual(scan.scan_invisible("﻿hello"), {})


class TestCLI(unittest.TestCase):
    def run_cli(self, *args, stdin=None):
        return subprocess.run([sys.executable, "-I", str(SCRIPT), *args], input=stdin,
                              capture_output=True, text=True, check=True)

    def test_json_output(self):
        out = self.run_cli(str(FIX / "ai_sample.txt"), "--json").stdout
        self.assertIn("artifact", json.loads(out)["category_counts"])

    def test_stdin_and_text_report(self):
        out = self.run_cli("-", stdin="Experts argue it is a testament to grit.\n").stdout
        self.assertIn("vagueattr", out)

    def test_clean_flag(self):
        res = self.run_cli("-", "--clean", stdin="a​b\n")
        self.assertEqual(res.stdout, "ab\n")
        self.assertIn("removed 1", res.stderr)


if __name__ == "__main__":
    unittest.main()
