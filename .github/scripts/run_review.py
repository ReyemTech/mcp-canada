"""Run a read-only review using temporary AWS credentials and a Mantle project."""

from __future__ import annotations

import json
import os
from pathlib import Path
import re
import subprocess
import sys
import uuid


def build_command(settings: dict[str, str], report: Path) -> list[str]:
    """Validate settings before constructing argv; never interpolate shell code."""
    patterns = {
        "AWS_REGION": r"[a-z]{2}(?:-[a-z]+)+-\d",
        "PR_REVIEW_PROJECT_ID": r"proj_[a-z0-9]+",
        "PR_REVIEW_MODEL": r"openai\.[a-zA-Z0-9._:-]+",
    }
    for key, pattern in patterns.items():
        if not re.fullmatch(pattern, settings.get(key, "")):
            raise RuntimeError(f"Invalid or missing {key}")
    region = settings["AWS_REGION"]
    project = settings["PR_REVIEW_PROJECT_ID"]
    command = [
        "codex", "exec", "--ignore-user-config", "--ignore-rules", "--ephemeral",
        "--sandbox", "read-only", "--color", "never",
        "--config", 'model_provider="amazon-bedrock"',
        "--config", f'model_providers.amazon-bedrock.aws.region="{region}"',
        "--config", f'model_providers.amazon-bedrock.http_headers={{"OpenAI-Project"="{project}"}}',
        "--config", 'model_reasoning_effort="medium"',
        "--config", 'web_search="disabled"',
        "--config", 'shell_environment_policy.inherit="none"',
        "--config", 'shell_environment_policy.set={PATH="/usr/local/bin:/usr/bin:/bin"}',
        "--model", settings["PR_REVIEW_MODEL"],
        "--output-schema", ".github/review/schema.json",
        "--output-last-message", str(report), "-",
    ]
    if settings.get("PR_REVIEW_UNPRIVILEGED_USER"):
        if settings["PR_REVIEW_UNPRIVILEGED_USER"] != "pr-reviewer":
            raise RuntimeError("Invalid reviewer OS account")
        command = [
            "sudo", "-H", "--preserve-env=AWS_ACCESS_KEY_ID,AWS_SECRET_ACCESS_KEY,AWS_SESSION_TOKEN,AWS_REGION,AWS_DEFAULT_REGION,PATH",
            "-u", "pr-reviewer", "--", *command,
        ]
    return command


def provider_environment(settings: dict[str, str]) -> dict[str, str]:
    """Expose only temporary AWS/provider and OS settings to the reviewer process."""
    allowed = {
        "PATH", "HOME", "TMPDIR", "TEMP", "TMP", "LANG", "LC_ALL",
        "SSL_CERT_FILE", "SSL_CERT_DIR", "AWS_ACCESS_KEY_ID", "AWS_SECRET_ACCESS_KEY",
        "AWS_SESSION_TOKEN", "AWS_REGION", "AWS_DEFAULT_REGION",
    }
    return {**{key: value for key, value in settings.items() if key in allowed},
            "AWS_EC2_METADATA_DISABLED": "true"}


def run_review(settings: dict[str, str], execute=subprocess.run) -> None:
    report_dir = Path(settings["RUNNER_TEMP"]) / "pr-review"
    report_dir.mkdir(exist_ok=True)
    report = report_dir / f"pr-review-{uuid.uuid4().hex}.json"
    command = build_command(settings, report)
    prompt = Path(".github/review/prompt.md").read_text(encoding="utf-8")
    try:
        result = execute(command, input=prompt, text=True, env=provider_environment(settings),
                         timeout=720, check=False)
        if result.returncode != 0 or not report.is_file():
            raise RuntimeError("The automated review did not complete")
        raw = report.read_text(encoding="utf-8")
        if len(raw.encode("utf-8")) > 50000:
            raise RuntimeError("Review report exceeds the output limit")
        json.loads(raw)  # Structural/content validation happens in the separate publisher.
        delimiter = f"review_{uuid.uuid4().hex}"
        with Path(settings["GITHUB_OUTPUT"]).open("a", encoding="utf-8") as output:
            output.write(f"final-message<<{delimiter}\n{raw}\n{delimiter}\n")
    finally:
        report.unlink(missing_ok=True)


if __name__ == "__main__":
    try:
        run_review(dict(os.environ))
    except (RuntimeError, ValueError, OSError, subprocess.TimeoutExpired) as exc:
        print(f"Review failed: {type(exc).__name__}", file=sys.stderr)
        raise SystemExit(1) from None
