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
        self.assertIn("negpar", cats("This isn't a setback \u2014 it's an opportunity."))

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


class TestTortured(unittest.TestCase):
    def test_spun_terms_flagged(self):
        for s in ["We trained a profound neural organization.", "Results on colossal information sets.",
                  "An irregular backwoods classifier.", "The mean square blunder fell.",
                  "Applications of counterfeit consciousness.", "A high flag to clamor ratio.",
                  "We used k-closest neighbors."]:
            with self.subTest(s=s):
                self.assertIn("tortured", cats(s))

    def test_standard_terms_not_flagged(self):
        s = ("We trained a deep neural network and a random forest on big data, reporting "
             "mean square error, signal to noise ratio, and k-nearest neighbors baselines. "
             "The organization of the paper follows. Facial recognition and naive Bayes are standard.")
        self.assertNotIn("tortured", cats(s))

    def test_counted_once(self):
        self.assertEqual(cats("A profound neural organization.")["tortured"], 1)

    def test_verdict(self):
        self.assertTrue(scan.scan("We used an irregular backwoods.")["verdict"].startswith("tortured"))


class TestHomoglyph(unittest.TestCase):
    def test_mixed_script_words_flagged_and_fixed(self):
        t = "The p\u0430per is r\u03bfbust."  # Cyrillic a, Greek omicron
        self.assertEqual(scan.homoglyph_words(t), ["p\u0430per", "r\u03bfbust"])
        self.assertEqual(scan.clean(t), "The paper is robust.")
        self.assertTrue(scan.scan(t)["verdict"].startswith("lookalike"))

    def test_legitimate_scripts_untouched(self):
        t = "\u0394x is small; the \u041c\u043e\u0441\u043a\u0432\u0430 dataset; \u03b2-cells; 5 \u00b5m; \u03b1\u03b2\u03b3."
        self.assertEqual(scan.homoglyph_words(t), [])
        self.assertEqual(scan.clean(t), t)


class TestHiddenText(unittest.TestCase):
    def test_hidden_text_flagged(self):
        for s in [r"\textcolor{white}{secret}", r"{\color{white} secret}", r"\fontsize{0.1pt}{0}",
                  '<span style="color: #ffffff;">x</span>', '<p style="font-size:0px;">x</p>']:
            with self.subTest(s=s):
                self.assertIn("hiddentext", cats(s))

    def test_ordinary_layout_not_flagged(self):
        for s in [r"\phantom{x}", r"\textcolor{red}{note}", '<p style="font-size:12px;">x</p>',
                  "The white paper was published."]:
            with self.subTest(s=s):
                self.assertNotIn("hiddentext", cats(s))

    def test_reviewer_injection(self):
        # Adversarial sample kept as test data, not code.
        s = (FIX / "reviewer_injection_sample.txt").read_text(encoding="utf-8")
        r = scan.scan(s)
        self.assertIn("injection", r["category_counts"])
        self.assertTrue(r["verdict"].startswith("hidden-text"))


class TestFalsePositives(unittest.TestCase):
    """Ordinary prose and markup that must not trigger the hard verdicts."""

    def assert_clean_of(self, text, *categories):
        got = cats(text)
        for c in categories:
            self.assertNotIn(c, got, msg=f"{c} fired on: {text!r}")

    def test_css_and_latex_layout(self):
        for s in ['<p style="font-size:0.9em;">x</p>', '<p style="font-size: 0.5rem;">x</p>',
                  '<div style="background-color: white;">x</div>', '<td style="border-color:#fff;">',
                  '.fade { opacity: 0; transition: opacity 1s; }', '<span style="opacity:0;">x</span>']:
            with self.subTest(s=s):
                self.assert_clean_of(s, "hiddentext")

    def test_real_hidden_css_still_found(self):
        for s in ['<span style="color:white;">x</span>', '<span style="color: rgb(255,255,255);">x</span>',
                  '<span style="font-size:0;">x</span>', '<span style="font-size:0.01px">x</span>']:
            with self.subTest(s=s):
                self.assertIn("hiddentext", cats(s))

    def test_greek_notation_untouched(self):
        for s in ["The photon energy is h\u03bd.", "Peak at \u03bdmax = 1650 cm-1.",
                  "the \u03bdC=O stretch", "an \u03b9 subscript"]:
            with self.subTest(s=s):
                self.assertEqual(scan.homoglyph_words(s), [])
                self.assertEqual(scan.clean(s), s)

    def test_ordinary_phrases_not_tortured(self):
        for s in ["Options include choice of solver and step size.",
                  "There is a huge information gap between the two groups.",
                  "An enormous information asymmetry exists in this market.",
                  "Neural organization of the visual cortex differs across species.",
                  "Brain organization changes during adolescence.",
                  "A versatile organization of volunteers ran the survey.",
                  "Information mining of public records was not permitted."]:
            with self.subTest(s=s):
                self.assert_clean_of(s, "tortured")

    def test_ml_evaluation_language_not_injection(self):
        for s in ["We design rubrics for LLM graders and compare them with human raters.",
                  "Feedback to AI reviewers was collected after each round.",
                  "Customers who give a positive review are more likely to return.",
                  "Prompts for language model reviewers are listed in Appendix B."]:
            with self.subTest(s=s):
                self.assert_clean_of(s, "injection")


class TestInvisible(unittest.TestCase):
    def test_detect_and_clean(self):
        t = "a\u200bb\u00adc\u202ed \U000E0041e\u2003f"
        inv = scan.scan_invisible(t)
        for k in ("zero-width-space", "soft-hyphen", "bidi-control", "tag-char", "exotic-space"):
            self.assertIn(k, inv)
        self.assertEqual(scan.clean(t), "abcd e f")

    def test_keeps_joiners_in_scripts_and_emoji(self):
        hindi = "\u0915\u094d\u200d\u0937"
        family = "\U0001F468\u200d\U0001F469"
        self.assertEqual(scan.clean(hindi), hindi)
        self.assertEqual(scan.clean(family), family)
        self.assertEqual(scan.scan_invisible(hindi + " " + family), {})

    def test_nbsp_kept_unless_spaces_flag(self):
        self.assertEqual(scan.clean("a\u00a0b"), "a\u00a0b")
        self.assertEqual(scan.clean("a\u00a0b", spaces=True), "a b")

    def test_leading_bom_ignored(self):
        self.assertEqual(scan.scan_invisible("\ufeffhello"), {})


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
        res = self.run_cli("-", "--clean", stdin="a\u200bb\n")
        self.assertEqual(res.stdout, "ab\n")
        self.assertIn("removed 1", res.stderr)


if __name__ == "__main__":
    unittest.main()
