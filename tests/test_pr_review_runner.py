"""Behavior checks for the Mantle reviewer process boundary."""

import importlib.util
from pathlib import Path
import subprocess

import pytest


def _load_runner():
    path = Path(__file__).resolve().parents[1] / ".github/scripts/run_review.py"
    spec = importlib.util.spec_from_file_location("pr_review_runner", path)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def _settings():
    return {
        "AWS_REGION": "us-east-1",
        "PR_REVIEW_PROJECT_ID": "proj_example",
        "PR_REVIEW_MODEL": "openai.gpt-6-sol",
    }


def test_mantle_command_selects_the_project_and_read_only_provider(tmp_path):
    runner = _load_runner()
    command = runner.build_command(_settings(), tmp_path / "report.json")
    assert 'model_provider="amazon-bedrock"' in command
    assert 'model_providers.amazon-bedrock.http_headers={"OpenAI-Project"="proj_example"}' in command
    assert 'model_providers.amazon-bedrock.aws.region="us-east-1"' in command
    assert command[command.index("--sandbox") + 1] == "read-only"
    assert command[command.index("--model") + 1] == "openai.gpt-6-sol"
    assert 'shell_environment_policy.inherit="none"' in command


@pytest.mark.parametrize("field,value", [
    ("AWS_REGION", "us-east-1\nother"),
    ("PR_REVIEW_PROJECT_ID", "default"),
    ("PR_REVIEW_PROJECT_ID", 'proj_a"}, env_key="SECRET"'),
    ("PR_REVIEW_MODEL", "--dangerously-bypass-approvals-and-sandbox"),
])
def test_invalid_settings_fail_before_starting_a_reviewer(tmp_path, field, value):
    runner = _load_runner()
    settings = {**_settings(), field: value}
    with pytest.raises(RuntimeError):
        runner.build_command(settings, tmp_path / "report.json")


def test_provider_environment_does_not_accept_bearer_or_openai_credentials():
    runner = _load_runner()
    env = runner.provider_environment({
        "AWS_ACCESS_KEY_ID": "temporary-access", "AWS_SECRET_ACCESS_KEY": "temporary-secret",
        "AWS_SESSION_TOKEN": "temporary-session", "AWS_BEARER_TOKEN_BEDROCK": "unwanted-key",
        "OPENAI_API_KEY": "unwanted-openai-key", "CODEX_API_KEY": "unwanted-other-key",
        "AWS_PROFILE": "unwanted-profile", "GITHUB_TOKEN": "unwanted-github-token", "PATH": "/usr/bin",
    })
    assert env["AWS_SESSION_TOKEN"] == "temporary-session"
    assert env["PATH"] == "/usr/bin"
    for key in ("AWS_BEARER_TOKEN_BEDROCK", "OPENAI_API_KEY", "CODEX_API_KEY", "AWS_PROFILE", "GITHUB_TOKEN"):
        assert key not in env


def test_failed_reviewer_does_not_publish_an_output(tmp_path):
    runner = _load_runner()
    output = tmp_path / "github-output"

    def fail(command, **kwargs):
        return subprocess.CompletedProcess(command, 1)

    with pytest.raises(RuntimeError, match="did not complete"):
        runner.run_review({**_settings(), "GITHUB_OUTPUT": str(output), "RUNNER_TEMP": str(tmp_path)}, execute=fail)
    assert not output.exists()


def test_successful_reviewer_publishes_only_the_json_report(tmp_path):
    runner = _load_runner()
    output = tmp_path / "github-output"
    report = '{"verdict":"ready","summary":"No findings","findings":[],"limitations":["No live calls"]}'

    def succeed(command, **kwargs):
        Path(command[command.index("--output-last-message") + 1]).write_text(report, encoding="utf-8")
        return subprocess.CompletedProcess(command, 0)

    runner.run_review({**_settings(), "GITHUB_OUTPUT": str(output), "RUNNER_TEMP": str(tmp_path)}, execute=succeed)
    assert report in output.read_text(encoding="utf-8")
    assert output.read_text(encoding="utf-8").startswith("final-message<<")
