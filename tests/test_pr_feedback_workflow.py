"""Guard the cross-run lock that prevents concurrent CI comment updates."""

from pathlib import Path

import yaml


def test_checks_lock_uses_resolved_pr_before_reading_or_updating_comments():
    workflow = yaml.safe_load(
        (Path(__file__).parents[1] / ".github/workflows/pr-feedback.yml").read_text(
            encoding="utf-8"
        )
    )
    jobs = workflow["jobs"]
    checks = jobs["checks"]
    assert checks.get("concurrency", {}).get("cancel-in-progress") is False
    assert checks["concurrency"]["group"] == (
        "pr-checks-publish-${{ needs.target.outputs.pr_number }}"
    )
    assert checks["needs"] == "target"
    assert jobs["target"]["permissions"]["pull-requests"] == "read"
    assert "pr_number" in jobs["target"]["outputs"]
    assert "needs.target.outputs.pr_number" in checks["if"]
