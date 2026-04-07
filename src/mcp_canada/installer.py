"""Installer for configuring mcp-canada on MCP client platforms."""

from __future__ import annotations

import json
import re
import shutil
import subprocess
import sys
from dataclasses import dataclass, field
from pathlib import Path
from typing import Callable


# ---------------------------------------------------------------------------
# Config generation — pure functions
# ---------------------------------------------------------------------------

def _build_server_entry(modules: str) -> dict:
    """Build standard JSON server entry (Claude Desktop, Cursor, etc.)."""
    entry: dict = {"command": "uvx", "args": ["mcp-canada"]}
    if modules:
        entry["args"].extend(["--modules", modules])
    return entry


def _build_opencode_entry(modules: str) -> dict:
    """Build OpenCode entry (flat command array, type: local)."""
    cmd = ["uvx", "mcp-canada"]
    if modules:
        cmd.extend(["--modules", modules])
    return {"type": "local", "command": cmd, "enabled": True}


def _build_zed_entry(modules: str) -> dict:
    """Build Zed entry (adds source: custom, env: {})."""
    entry = _build_server_entry(modules)
    entry["source"] = "custom"
    entry["env"] = {}
    return entry


def _build_codex_toml(modules: str) -> str:
    """Build TOML section for Codex CLI."""
    args = '["mcp-canada"]' if not modules else f'["mcp-canada", "--modules", "{modules}"]'
    return f'[mcp_servers.mcp-canada]\ncommand = "uvx"\nargs = {args}\n'


def _build_goose_yaml(modules: str) -> str:
    """Build YAML block for Goose CLI mcp-canada entry."""
    args = '["mcp-canada"]' if not modules else f'["mcp-canada", "--modules", "{modules}"]'
    return (
        f"  mcp-canada:\n"
        f"    name: MCP Canada\n"
        f"    type: stdio\n"
        f"    cmd: uvx\n"
        f"    args: {args}\n"
        f"    enabled: true\n"
    )


def _build_claude_code_command(modules: str) -> list[str]:
    """Build the `claude mcp add` command list."""
    cmd = ["claude", "mcp", "add", "mcp-canada", "--scope", "user", "--", "uvx", "mcp-canada"]
    if modules:
        cmd.extend(["--modules", modules])
    return cmd


# ---------------------------------------------------------------------------
# Merge logic
# ---------------------------------------------------------------------------

def _merge_json_config(existing_text: str, root_key: str, entry: dict) -> str:
    """Merge mcp-canada entry into an existing JSON config string.

    Raises json.JSONDecodeError if existing_text is invalid JSON.
    """
    config = json.loads(existing_text) if existing_text.strip() else {}
    if root_key not in config:
        config[root_key] = {}
    config[root_key]["mcp-canada"] = entry
    return json.dumps(config, indent=2) + "\n"


def _merge_codex_toml(existing_text: str, modules: str) -> str:
    """Merge mcp-canada section into existing TOML content for Codex."""
    new_section = _build_codex_toml(modules)

    # Remove existing [mcp_servers.mcp-canada] section if present
    # Match from the section header to the next top-level section header or end of string
    pattern = r'\[mcp_servers\.mcp-canada\].*?(?=\n\[|\Z)'
    cleaned = re.sub(pattern, '', existing_text, flags=re.DOTALL).rstrip()

    if cleaned:
        return cleaned + "\n\n" + new_section
    return new_section


def _merge_goose_yaml(existing_text: str, modules: str) -> str:
    """Merge mcp-canada entry into existing Goose YAML."""
    new_entry = _build_goose_yaml(modules)

    # Remove existing mcp-canada block if present (indented under extensions:)
    pattern = r'  mcp-canada:\n(?:    [^\n]*\n)*'
    cleaned = re.sub(pattern, '', existing_text)

    if "extensions:" not in cleaned:
        # No extensions key — add it
        if cleaned.strip():
            return cleaned.rstrip() + "\n\nextensions:\n" + new_entry
        return "extensions:\n" + new_entry

    # Insert after extensions: line
    return cleaned.rstrip() + "\n" + new_entry


# ---------------------------------------------------------------------------
# Platform registry
# ---------------------------------------------------------------------------

def _home() -> Path:
    return Path.home()


def _is_mac() -> bool:
    return sys.platform == "darwin"


def _is_windows() -> bool:
    return sys.platform == "win32"


def _vscode_globalstore() -> Path:
    """Return VS Code globalStorage base path."""
    if _is_mac():
        return _home() / "Library" / "Application Support" / "Code" / "User" / "globalStorage"
    elif _is_windows():
        return Path.home() / "AppData" / "Roaming" / "Code" / "User" / "globalStorage"
    return _home() / ".config" / "Code" / "User" / "globalStorage"


@dataclass
class Platform:
    name: str
    display: str
    format: str  # "json" | "toml" | "yaml" | "cli"
    root_key: str
    config_path: Callable[[], Path | None]
    detect_path: Callable[[], Path]
    extra_fields: dict = field(default_factory=dict)

    def detect(self) -> bool:
        """Check if this platform appears to be installed."""
        try:
            path = self.detect_path()
            return path.exists()
        except Exception:
            return False


def _claude_desktop_config() -> Path:
    if _is_mac():
        return _home() / "Library" / "Application Support" / "Claude" / "claude_desktop_config.json"
    elif _is_windows():
        return Path.home() / "AppData" / "Roaming" / "Claude" / "claude_desktop_config.json"
    return _home() / ".config" / "Claude" / "claude_desktop_config.json"


def _claude_desktop_detect() -> Path:
    if _is_mac():
        return _home() / "Library" / "Application Support" / "Claude"
    elif _is_windows():
        return Path.home() / "AppData" / "Roaming" / "Claude"
    return _home() / ".config" / "Claude"


def _claude_code_detect() -> Path:
    """Detect Claude Code by checking if `claude` binary exists."""
    which = shutil.which("claude")
    if which:
        return Path(which)
    return Path("/nonexistent")  # will fail .exists() check


PLATFORMS: list[Platform] = [
    Platform(
        name="claude-desktop",
        display="Claude Desktop",
        format="json",
        root_key="mcpServers",
        config_path=_claude_desktop_config,
        detect_path=_claude_desktop_detect,
    ),
    Platform(
        name="claude-code",
        display="Claude Code",
        format="cli",
        root_key="",
        config_path=lambda: None,
        detect_path=_claude_code_detect,
    ),
    Platform(
        name="cursor",
        display="Cursor",
        format="json",
        root_key="mcpServers",
        config_path=lambda: _home() / ".cursor" / "mcp.json",
        detect_path=lambda: _home() / ".cursor",
    ),
    Platform(
        name="vscode",
        display="VS Code (Copilot)",
        format="json",
        root_key="servers",
        config_path=lambda: Path.cwd() / ".vscode" / "mcp.json",
        detect_path=lambda: Path.cwd() / ".vscode",
    ),
    Platform(
        name="windsurf",
        display="Windsurf",
        format="json",
        root_key="mcpServers",
        config_path=lambda: _home() / ".codeium" / "windsurf" / "mcp_config.json",
        detect_path=lambda: _home() / ".codeium" / "windsurf",
    ),
    Platform(
        name="zed",
        display="Zed",
        format="json",
        root_key="context_servers",
        config_path=lambda: (_home() / ".zed" / "settings.json" if _is_mac()
                             else _home() / ".config" / "zed" / "settings.json"),
        detect_path=lambda: (_home() / ".zed" if _is_mac()
                             else _home() / ".config" / "zed"),
    ),
    Platform(
        name="codex",
        display="Codex CLI",
        format="toml",
        root_key="mcp_servers",
        config_path=lambda: _home() / ".codex" / "config.toml",
        detect_path=lambda: _home() / ".codex",
    ),
    Platform(
        name="gemini",
        display="Gemini CLI",
        format="json",
        root_key="mcpServers",
        config_path=lambda: _home() / ".gemini" / "settings.json",
        detect_path=lambda: _home() / ".gemini",
    ),
    Platform(
        name="amazon-q",
        display="Amazon Q",
        format="json",
        root_key="mcpServers",
        config_path=lambda: _home() / ".aws" / "amazonq" / "mcp.json",
        detect_path=lambda: _home() / ".aws" / "amazonq",
    ),
    Platform(
        name="opencode",
        display="OpenCode",
        format="json",
        root_key="mcp",
        config_path=lambda: _home() / ".config" / "opencode" / "opencode.json",
        detect_path=lambda: _home() / ".config" / "opencode",
    ),
    Platform(
        name="cline",
        display="Cline",
        format="json",
        root_key="mcpServers",
        config_path=lambda: (
            _vscode_globalstore() / "saoudrizwan.claude-dev" / "settings" / "cline_mcp_settings.json"
        ),
        detect_path=lambda: _vscode_globalstore() / "saoudrizwan.claude-dev",
    ),
    Platform(
        name="roo-code",
        display="Roo Code",
        format="json",
        root_key="mcpServers",
        config_path=lambda: (
            _vscode_globalstore() / "rooveterinaryinc.roo-cline" / "settings" / "cline_mcp_settings.json"
        ),
        detect_path=lambda: _vscode_globalstore() / "rooveterinaryinc.roo-cline",
    ),
    Platform(
        name="goose",
        display="Goose CLI",
        format="yaml",
        root_key="extensions",
        config_path=lambda: _home() / ".config" / "goose" / "config.yaml",
        detect_path=lambda: _home() / ".config" / "goose",
    ),
    Platform(
        name="junie",
        display="Junie CLI",
        format="json",
        root_key="mcpServers",
        config_path=lambda: _home() / ".junie" / "mcp" / "mcp.json",
        detect_path=lambda: _home() / ".junie",
    ),
]


def get_platform(name: str) -> Platform | None:
    """Look up a platform by CLI name."""
    for p in PLATFORMS:
        if p.name == name:
            return p
    return None


# ---------------------------------------------------------------------------
# Install logic per platform
# ---------------------------------------------------------------------------

def _install_json_platform(platform: Platform, modules: str) -> str:
    """Install mcp-canada into a JSON-config platform. Returns status message."""
    config_path = platform.config_path()
    if config_path is None:
        return f"no config path for {platform.display}"

    # Build entry based on platform
    if platform.name == "opencode":
        entry = _build_opencode_entry(modules)
    elif platform.name == "zed":
        entry = _build_zed_entry(modules)
    else:
        entry = _build_server_entry(modules)

    # Read existing or start fresh
    config_path.parent.mkdir(parents=True, exist_ok=True)
    existing = config_path.read_text() if config_path.exists() else "{}"

    try:
        merged = _merge_json_config(existing, platform.root_key, entry)
    except json.JSONDecodeError as e:
        return f"invalid JSON in {config_path}: {e}"

    config_path.write_text(merged)
    return f"wrote {config_path}"


def _install_codex(modules: str) -> str:
    """Install mcp-canada into Codex CLI TOML config."""
    config_path = _home() / ".codex" / "config.toml"
    config_path.parent.mkdir(parents=True, exist_ok=True)
    existing = config_path.read_text() if config_path.exists() else ""

    merged = _merge_codex_toml(existing, modules)
    config_path.write_text(merged)
    return f"wrote {config_path}"


def _install_goose(modules: str) -> str:
    """Install mcp-canada into Goose CLI YAML config."""
    config_path = _home() / ".config" / "goose" / "config.yaml"
    config_path.parent.mkdir(parents=True, exist_ok=True)
    existing = config_path.read_text() if config_path.exists() else ""

    merged = _merge_goose_yaml(existing, modules)
    config_path.write_text(merged)
    return f"wrote {config_path}"


def _install_claude_code(modules: str) -> str:
    """Install mcp-canada via Claude Code CLI."""
    cmd = _build_claude_code_command(modules)
    if not shutil.which("claude"):
        # Fallback: write to ~/.claude.json
        config_path = _home() / ".claude.json"
        existing = config_path.read_text() if config_path.exists() else "{}"
        entry = _build_server_entry(modules)
        try:
            merged = _merge_json_config(existing, "mcpServers", entry)
        except json.JSONDecodeError as e:
            return f"invalid JSON in {config_path}: {e}"
        config_path.write_text(merged)
        return f"claude CLI not found, wrote {config_path} instead"

    try:
        subprocess.run(cmd, check=True, capture_output=True, text=True)
        return f"ran: {' '.join(cmd)}"
    except subprocess.CalledProcessError as e:
        return f"command failed: {e.stderr.strip()}"


def install_platform(platform: Platform, modules: str) -> str:
    """Install mcp-canada on a single platform. Returns status message."""
    if platform.format == "cli":
        return _install_claude_code(modules)
    elif platform.format == "toml":
        return _install_codex(modules)
    elif platform.format == "yaml":
        return _install_goose(modules)
    else:
        return _install_json_platform(platform, modules)


# ---------------------------------------------------------------------------
# TUI and entry point
# ---------------------------------------------------------------------------

def _run_tui(modules: str) -> None:
    """Run interactive TUI for platform selection."""
    try:
        from InquirerPy import inquirer
    except ImportError:
        print("InquirerPy is required for interactive mode. Install with: pip install InquirerPy")
        sys.exit(1)

    choices = []
    for p in PLATFORMS:
        detected = p.detect()
        label = f"{p.display} (detected)" if detected else p.display
        choices.append({"name": label, "value": p.name, "enabled": detected})

    selected = inquirer.checkbox(  # type: ignore[attr-defined]
        message="Select platforms (space to toggle, enter to confirm):",
        choices=choices,
    ).execute()

    if not selected:
        print("No platforms selected.")
        return

    _install_selected(selected, modules)


def _install_selected(platform_names: list[str], modules: str) -> None:
    """Install mcp-canada on the given platforms and print results."""
    success_count = 0
    for name in platform_names:
        platform = get_platform(name)
        if platform is None:
            print(f"  \u2717 Unknown platform: {name}")
            continue
        try:
            result = install_platform(platform, modules)
            print(f"  \u2713 {platform.display:20s} \u2014 {result}")
            success_count += 1
        except PermissionError:
            print(f"  \u2717 {platform.display:20s} \u2014 permission denied")
        except Exception as e:
            print(f"  \u2717 {platform.display:20s} \u2014 {e}")

    print(f"\nConfigured mcp-canada on {success_count} platform(s). "
          "Restart any running clients to pick up changes.")


def run_install(args: object) -> None:
    """Entry point called from server.py when `install` subcommand is used."""
    platforms = getattr(args, "platforms", [])
    modules = getattr(args, "modules", "")

    print("\n  \U0001f341 mcp-canada installer\n")

    if platforms:
        _install_selected(platforms, modules)
    else:
        _run_tui(modules)
