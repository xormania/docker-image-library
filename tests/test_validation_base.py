import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
from validation_base import select

BASE, GOOD, HEAD = "a" * 40, "b" * 40, "c" * 40


def run(commit=GOOD, number=22, base=BASE, conclusion="success", event="pull_request"):
    return {"head_sha": commit, "conclusion": conclusion, "event": event,
            "pull_requests": [{"number": number, "base": {"sha": base}}]}


class ValidationBaseTests(unittest.TestCase):
    def test_successful_ancestral_validation_can_scope_the_next_update(self):
        self.assertEqual(select([run()], 22, HEAD, BASE, lambda commit, head: commit == GOOD and head == HEAD), GOOD)

    def test_failed_cancelled_other_pr_or_changed_base_cannot_skip_work(self):
        for candidate in (run(conclusion="failure"), run(conclusion="cancelled"),
                          run(number=21), run(base="d" * 40), run(event="workflow_dispatch"),
                          run(commit="invalid")):
            with self.subTest(candidate=candidate):
                self.assertEqual(select([candidate], 22, HEAD, BASE, lambda *_: True), BASE)

    def test_force_pushed_unrelated_heads_and_empty_history_use_full_delta(self):
        self.assertEqual(select([run()], 22, HEAD, BASE, lambda *_: False), BASE)
        self.assertEqual(select([], 22, HEAD, BASE), BASE)

    def test_an_unchanged_successful_head_needs_no_repeat_image_build(self):
        self.assertEqual(select([run(commit=HEAD)], 22, HEAD, BASE, lambda *_: True), HEAD)

    def test_search_continues_past_unusable_newer_runs(self):
        self.assertEqual(select([run(commit="d" * 40), run()], 22, HEAD, BASE,
                                lambda commit, _: commit == GOOD), GOOD)
