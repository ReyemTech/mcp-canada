"""Tests for installer config generation and merge logic."""

import json

import pytest


class TestBuildServerEntry:
    """Test _build_server_entry() produces correct dicts per platform format."""

    def test_standard_json_no_modules(self):
        from mcp_canada.installer import _build_server_entry

        entry = _build_server_entry(modules="")
        assert entry == {"command": "uvx", "args": ["mcp-canada"]}

    def test_standard_json_with_modules(self):
        from mcp_canada.installer import _build_server_entry

        entry = _build_server_entry(modules="bank_of_canada,weather")
        assert entry == {
            "command": "uvx",
            "args": ["mcp-canada", "--modules", "bank_of_canada,weather"],
        }

    def test_opencode_entry_no_modules(self):
        from mcp_canada.installer import _build_opencode_entry

        entry = _build_opencode_entry(modules="")
        assert entry == {
            "type": "local",
            "command": ["uvx", "mcp-canada"],
            "enabled": True,
        }

    def test_opencode_entry_with_modules(self):
        from mcp_canada.installer import _build_opencode_entry

        entry = _build_opencode_entry(modules="recalls")
        assert entry == {
            "type": "local",
            "command": ["uvx", "mcp-canada", "--modules", "recalls"],
            "enabled": True,
        }

    def test_zed_entry(self):
        from mcp_canada.installer import _build_zed_entry

        entry = _build_zed_entry(modules="")
        assert entry == {
            "command": "uvx",
            "args": ["mcp-canada"],
            "source": "custom",
            "env": {},
        }

    def test_zed_entry_with_modules(self):
        from mcp_canada.installer import _build_zed_entry

        entry = _build_zed_entry(modules="weather")
        assert entry == {
            "command": "uvx",
            "args": ["mcp-canada", "--modules", "weather"],
            "source": "custom",
            "env": {},
        }


class TestCodexToml:
    """Test TOML generation for Codex CLI."""

    def test_codex_toml_no_modules(self):
        from mcp_canada.installer import _build_codex_toml

        toml = _build_codex_toml(modules="")
        assert '[mcp_servers.mcp-canada]' in toml
        assert 'command = "uvx"' in toml
        assert 'args = ["mcp-canada"]' in toml

    def test_codex_toml_with_modules(self):
        from mcp_canada.installer import _build_codex_toml

        toml = _build_codex_toml(modules="bank_of_canada")
        assert 'args = ["mcp-canada", "--modules", "bank_of_canada"]' in toml


class TestGooseYaml:
    """Test YAML generation for Goose CLI."""

    def test_goose_yaml_no_modules(self):
        from mcp_canada.installer import _build_goose_yaml

        yaml = _build_goose_yaml(modules="")
        assert "mcp-canada:" in yaml
        assert "name: MCP Canada" in yaml
        assert "type: stdio" in yaml
        assert "cmd: uvx" in yaml
        assert 'args: ["mcp-canada"]' in yaml
        assert "enabled: true" in yaml

    def test_goose_yaml_with_modules(self):
        from mcp_canada.installer import _build_goose_yaml

        yaml = _build_goose_yaml(modules="weather,recalls")
        assert 'args: ["mcp-canada", "--modules", "weather,recalls"]' in yaml


class TestMergeJsonConfig:
    """Test JSON merge logic preserves existing config."""

    def test_merge_into_empty(self):
        from mcp_canada.installer import _merge_json_config

        existing = "{}"
        result = _merge_json_config(existing, "mcpServers", {"command": "uvx", "args": ["mcp-canada"]})
        parsed = json.loads(result)
        assert parsed["mcpServers"]["mcp-canada"] == {"command": "uvx", "args": ["mcp-canada"]}

    def test_merge_preserves_other_servers(self):
        from mcp_canada.installer import _merge_json_config

        existing = json.dumps({
            "mcpServers": {
                "other-server": {"command": "npx", "args": ["other"]}
            }
        })
        result = _merge_json_config(existing, "mcpServers", {"command": "uvx", "args": ["mcp-canada"]})
        parsed = json.loads(result)
        assert "other-server" in parsed["mcpServers"]
        assert "mcp-canada" in parsed["mcpServers"]

    def test_merge_updates_existing_entry(self):
        from mcp_canada.installer import _merge_json_config

        existing = json.dumps({
            "mcpServers": {
                "mcp-canada": {"command": "uvx", "args": ["mcp-canada"]}
            }
        })
        new_entry = {"command": "uvx", "args": ["mcp-canada", "--modules", "weather"]}
        result = _merge_json_config(existing, "mcpServers", new_entry)
        parsed = json.loads(result)
        assert parsed["mcpServers"]["mcp-canada"] == new_entry

    def test_merge_preserves_non_mcp_keys(self):
        from mcp_canada.installer import _merge_json_config

        existing = json.dumps({
            "theme": "dark",
            "mcpServers": {}
        })
        result = _merge_json_config(existing, "mcpServers", {"command": "uvx", "args": ["mcp-canada"]})
        parsed = json.loads(result)
        assert parsed["theme"] == "dark"

    def test_merge_different_root_key(self):
        from mcp_canada.installer import _merge_json_config

        existing = "{}"
        result = _merge_json_config(existing, "servers", {"command": "uvx", "args": ["mcp-canada"]})
        parsed = json.loads(result)
        assert "servers" in parsed
        assert "mcp-canada" in parsed["servers"]

    def test_merge_invalid_json_raises(self):
        from mcp_canada.installer import _merge_json_config

        with pytest.raises(json.JSONDecodeError):
            _merge_json_config("not valid json {{{", "mcpServers", {})


class TestMergeCodexToml:
    """Test TOML merge for Codex CLI."""

    def test_merge_into_empty(self):
        from mcp_canada.installer import _merge_codex_toml

        result = _merge_codex_toml("", modules="")
        assert '[mcp_servers.mcp-canada]' in result
        assert 'command = "uvx"' in result

    def test_merge_preserves_existing_content(self):
        from mcp_canada.installer import _merge_codex_toml

        existing = '[other_section]\nkey = "value"\n'
        result = _merge_codex_toml(existing, modules="")
        assert '[other_section]' in result
        assert 'key = "value"' in result
        assert '[mcp_servers.mcp-canada]' in result

    def test_merge_replaces_existing_section(self):
        from mcp_canada.installer import _merge_codex_toml

        existing = '[mcp_servers.mcp-canada]\ncommand = "old"\nargs = ["old"]\n'
        result = _merge_codex_toml(existing, modules="weather")
        assert result.count('[mcp_servers.mcp-canada]') == 1
        assert '"old"' not in result
        assert '"weather"' in result


class TestMergeGooseYaml:
    """Test YAML merge for Goose CLI."""

    def test_merge_into_empty(self):
        from mcp_canada.installer import _merge_goose_yaml

        result = _merge_goose_yaml("", modules="")
        assert "extensions:" in result
        assert "mcp-canada:" in result

    def test_merge_preserves_existing_extensions(self):
        from mcp_canada.installer import _merge_goose_yaml

        existing = "extensions:\n  other-ext:\n    name: Other\n    type: stdio\n    cmd: other\n"
        result = _merge_goose_yaml(existing, modules="")
        assert "other-ext:" in result
        assert "mcp-canada:" in result


class TestPlatformRegistry:
    """Test platform registry is complete and well-formed."""

    def test_all_14_platforms_registered(self):
        from mcp_canada.installer import PLATFORMS

        assert len(PLATFORMS) == 14

    def test_platform_names_are_unique(self):
        from mcp_canada.installer import PLATFORMS

        names = [p.name for p in PLATFORMS]
        assert len(names) == len(set(names))

    def test_all_platforms_have_required_fields(self):
        from mcp_canada.installer import PLATFORMS

        for p in PLATFORMS:
            assert p.name, "Platform missing name"
            assert p.display, f"{p.name} missing display"
            assert p.format in ("json", "toml", "yaml", "cli"), f"{p.name} bad format: {p.format}"

    def test_get_platform_by_name(self):
        from mcp_canada.installer import get_platform

        p = get_platform("claude-desktop")
        assert p is not None
        assert p.display == "Claude Desktop"

    def test_get_platform_unknown_returns_none(self):
        from mcp_canada.installer import get_platform

        assert get_platform("nonexistent") is None


class TestClaudeCodeCommand:
    """Test Claude Code CLI command generation."""

    def test_command_no_modules(self):
        from mcp_canada.installer import _build_claude_code_command

        cmd = _build_claude_code_command(modules="")
        assert cmd == ["claude", "mcp", "add", "mcp-canada", "--scope", "user", "--", "uvx", "mcp-canada"]

    def test_command_with_modules(self):
        from mcp_canada.installer import _build_claude_code_command

        cmd = _build_claude_code_command(modules="weather")
        assert cmd == [
            "claude", "mcp", "add", "mcp-canada", "--scope", "user",
            "--", "uvx", "mcp-canada", "--modules", "weather",
        ]


class TestArgparse:
    """Test that argparse changes are backward compatible."""

    def test_no_args_defaults_to_server_mode(self):
        from mcp_canada.server import _build_parser
        parser = _build_parser()
        args = parser.parse_args([])
        assert args.command is None
        assert args.transport == "stdio"

    def test_server_flags_still_work(self):
        from mcp_canada.server import _build_parser
        parser = _build_parser()
        args = parser.parse_args(["--transport", "sse", "--port", "9000"])
        assert args.command is None
        assert args.transport == "sse"
        assert args.port == 9000

    def test_install_subcommand_parsed(self):
        from mcp_canada.server import _build_parser
        parser = _build_parser()
        args = parser.parse_args(["install"])
        assert args.command == "install"
        assert args.platforms == []

    def test_install_with_platforms(self):
        from mcp_canada.server import _build_parser
        parser = _build_parser()
        args = parser.parse_args(["install", "claude-desktop", "cursor"])
        assert args.command == "install"
        assert args.platforms == ["claude-desktop", "cursor"]

    def test_install_with_modules(self):
        from mcp_canada.server import _build_parser
        parser = _build_parser()
        args = parser.parse_args(["install", "--modules", "weather,recalls"])
        assert args.command == "install"
        assert args.modules == "weather,recalls"

    def test_install_with_platforms_and_modules(self):
        from mcp_canada.server import _build_parser
        parser = _build_parser()
        args = parser.parse_args(["install", "cursor", "vscode", "--modules", "bank_of_canada"])
        assert args.command == "install"
        assert args.platforms == ["cursor", "vscode"]
        assert args.modules == "bank_of_canada"
