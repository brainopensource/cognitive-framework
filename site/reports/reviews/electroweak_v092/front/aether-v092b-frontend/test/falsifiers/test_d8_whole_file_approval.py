"""D8: a whole-file creation must be reviewable, or it is unapprovable forever.

`patch.apply` has always accepted whole-file creation through `content`
(`patch-tool.json` documents it; `wiring.py::_effect_of` maps it to a `write`).
`_diff_from` accepted only `diff`/`patch`, so the approval challenge could not
be built for such a request, `_resolve` returned `None`, and the episode
escalated with no effect ever started.

The consequence is larger than it looks: **creating a new file was unapprovable
in every domain.** Coding runs mostly edit files that already exist, so it hid
there. The formal-SAT pack surfaced it immediately, because writing a new
artifact is the normal move in that domain -- which is exactly the kind of
generic defect M-5b exists to find, and is *not* counter-evidence against
generality.

The fix renders the content as an addition-only unified diff: the reviewer
signs the lines that will land, which is strictly more information than an
opaque `content` field. These tests pin that it does not thereby widen what was
authorised.
"""

from __future__ import annotations

import unittest

from vanguard.packages.kernel.model import EffectRequest
from vanguard.packages.runtime.governance.approvals import (
    ApprovalFormatError,
    _diff_from,
)

CONTENT = '{"assignment": {"1": true, "2": true}}'


def _request(**args) -> EffectRequest:
    return EffectRequest(
        action="patch.apply",
        resource={"kind": "fs", "root": "/w", "paths": ["/w/witness.json"]},
        args=args, principal="agent", run_id="run-d8")


class WholeFileCreationIsReviewable(unittest.TestCase):
    def test_content_renders_as_an_addition_only_diff(self) -> None:
        rendered = _diff_from(_request(path="witness.json", content=CONTENT))
        self.assertIn("--- a/witness.json", rendered)
        self.assertIn("+++ b/witness.json", rendered)
        self.assertIn(f"+{CONTENT}", rendered)

    def test_the_reviewer_sees_every_line_that_will_land(self) -> None:
        body = "line one\nline two\nline three"
        rendered = _diff_from(_request(path="a.txt", content=body))
        for line in body.splitlines():
            self.assertIn(f"+{line}", rendered)
        self.assertIn("@@ -0,0 +1,3 @@", rendered)

    def test_an_empty_file_creation_is_still_reviewable(self) -> None:
        rendered = _diff_from(_request(path="empty.txt", content=""))
        self.assertIn("--- a/empty.txt", rendered)

    def test_an_explicit_diff_still_wins_over_content(self) -> None:
        # A request carrying both must be reviewed as the diff it declares;
        # silently preferring `content` would let the signed material differ
        # from the applied one.
        diff = "--- a/x\n+++ b/x\n@@ -1 +1 @@\n-a\n+b"
        self.assertEqual(_diff_from(_request(path="x", diff=diff, content="ignored")),
                         diff + "\n")

    def test_a_request_with_neither_is_still_refused(self) -> None:
        with self.assertRaises(ApprovalFormatError) as ctx:
            _diff_from(_request(path="x"))
        self.assertIn("diff, patch, or content", str(ctx.exception))

    def test_content_without_a_path_is_refused(self) -> None:
        # Rendering a diff for an unnamed file would put an ambiguity in front
        # of the reviewer -- the same defect D7 fixed for headerless hunks.
        with self.assertRaises(ApprovalFormatError):
            _diff_from(_request(content=CONTENT))


if __name__ == "__main__":
    unittest.main()
