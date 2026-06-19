#!/usr/bin/env python3
"""Install Claude Code global config from this repo into ~/.claude.

Design (why this is not a plain copy):
  ~/.claude mixes two kinds of content with opposite needs.

  1. Static, repo-owned dirs (agents/commands/rules/skills/hooks/workflows).
     Never written by Claude at runtime -> linked as SYMLINKS to this repo, so a
     repo edit goes live immediately and `git pull` updates every machine. No
     `rm -rf` of real content, no copy drift.

  2. settings.json. Written by Claude AT RUNTIME (/effort, /model, plugin toggles,
     "always allow" permissions). A blind overwrite destroys that state -- this is
     what wiped the notification settings before. So it is MERGED, never replaced,
     using just two rules:
       FORCE   (repo wins, so wiring propagates): hooks.PreToolUse / PostToolUse,
               permissions.allow (union), env (per key), enabledPlugins,
               extraKnownMarketplaces. The live value takes the template's; to
               remove forced wiring, set it empty in the template (its absence
               leaves live untouched rather than deleting it).
       DEFAULT (fill only when the key is absent in live; a present live value
               always wins -- this is how notifications survive): everything else,
               e.g. hooks.Stop / PermissionRequest / Notification, model, effortLevel.
     A live key is never deleted, and the file is backed up before writing.

  3. mcp.json -> additive merge into ~/.claude.json (only adds missing servers).

Usage:
  python3 install.py            apply
  python3 install.py --dry-run  show what would change, write nothing
"""

import json
import os
import shutil
import subprocess
import sys
from datetime import datetime
from pathlib import Path

REPO = Path(__file__).resolve().parent
CLAUDE_DIR = Path.home() / ".claude"

STATIC_DIRS = ["agents", "commands", "rules", "skills", "hooks", "workflows"]

# settings.json merge policy (see module docstring)
FORCE_HOOK_EVENTS = ["PreToolUse", "PostToolUse"]
FORCE_DICT_KEYS = ["env", "enabledPlugins", "extraKnownMarketplaces"]


# ─────────────────────────────────────────────────────────────
# output helpers
# ─────────────────────────────────────────────────────────────
def ok(msg):
    print(f"  ✓ {msg}")


def warn(msg):
    print(f"  ⚠ {msg}")


def info(msg):
    print(f"    {msg}")


def step(msg):
    print(f"\n{msg}")


def fail(msg):
    print(f"  ✗ {msg}", file=sys.stderr)
    sys.exit(1)


# ─────────────────────────────────────────────────────────────
# backup (created lazily, only when something is actually backed up)
# ─────────────────────────────────────────────────────────────
class Backup:
    """Timestamped backup dir under ~/.claude/.backup, created on first use."""

    def __init__(self, dry_run, stamp):
        self.dry_run = dry_run
        self.root = CLAUDE_DIR / ".backup" / stamp
        self.used = False

    def save(self, path):
        """Copy a file or directory into the backup, mirroring its path under ~/.claude."""
        if not path.exists() and not path.is_symlink():
            return
        try:
            rel = path.relative_to(CLAUDE_DIR)
        except ValueError:
            rel = Path(path.name)
        dest = self.root / rel
        if self.dry_run:
            info(f"would back up {path} -> {dest}")
            self.used = True
            return
        dest.parent.mkdir(parents=True, exist_ok=True)
        if path.is_dir() and not path.is_symlink():
            shutil.copytree(path, dest, symlinks=True)
        else:
            shutil.copy2(path, dest)
        self.used = True


# ─────────────────────────────────────────────────────────────
# Step 1: preflight
# ─────────────────────────────────────────────────────────────
def preflight():
    step("[1/4] preflight check")

    if sys.version_info < (3, 8):
        fail(f"python {sys.version_info.major}.{sys.version_info.minor} too old (>= 3.8 required)")
    ok(f"python {sys.version_info.major}.{sys.version_info.minor}")

    if shutil.which("git"):
        ok("git found")
    else:
        fail("git not found (>= 2.0 required)")

    if shutil.which("docker"):
        ok("docker found")
    else:
        warn("docker not found. GitHub MCP requires Docker (brew install --cask docker on macOS).")


# ─────────────────────────────────────────────────────────────
# Step 2: symlink static dirs
# ─────────────────────────────────────────────────────────────
def link_dirs(dry_run, backup):
    step("[2/4] linking config directories")

    for name in STATIC_DIRS:
        src = REPO / name
        if not src.is_dir():
            continue
        dst = CLAUDE_DIR / name

        if dst.is_symlink() and dst.exists() and dst.resolve() == src.resolve():
            ok(f"{name}/ (already linked)")
            continue

        # Replace whatever is there, backing up real dirs first.
        if dst.is_symlink():
            if not dry_run:
                dst.unlink()
            info(f"{name}/ (replacing stale symlink)")
        elif dst.is_dir():
            backup.save(dst)
            if not dry_run:
                shutil.rmtree(dst)
            info(f"{name}/ (was a real dir, backed up then linked)")
        elif dst.exists():
            backup.save(dst)
            if not dry_run:
                dst.unlink()

        if dry_run:
            ok(f"{name}/ -> would link to {src}")
        else:
            CLAUDE_DIR.mkdir(parents=True, exist_ok=True)
            dst.symlink_to(src, target_is_directory=True)
            ok(f"{name}/ -> {src}")


# ─────────────────────────────────────────────────────────────
# Step 3: merge settings.json
# ─────────────────────────────────────────────────────────────
def _union(a, b):
    """Order-preserving union of two lists."""
    return list(dict.fromkeys(list(a) + list(b)))


def merge_settings_data(template, live):
    """Pure merge per the policy in the module docstring. Never deletes a live key."""
    result = dict(live)  # start from live so every live key survives

    # FORCE per-key dicts: template wins on its own keys, live extras kept
    for key in FORCE_DICT_KEYS:
        if key in template or key in live:
            result[key] = {**live.get(key, {}), **template.get(key, {})}

    # permissions: template defaults < live, but allow lists are unioned
    if "permissions" in template or "permissions" in live:
        perms = {**template.get("permissions", {}), **live.get("permissions", {})}
        t_allow = template.get("permissions", {}).get("allow", [])
        l_allow = live.get("permissions", {}).get("allow", [])
        if t_allow or l_allow:
            perms["allow"] = _union(t_allow, l_allow)
        result["permissions"] = perms

    # hooks: FORCE the blocker events from template, PRESERVE the rest of live,
    # DEFAULT-fill any template-only events.
    t_hooks = template.get("hooks", {})
    l_hooks = live.get("hooks", {})
    if t_hooks or l_hooks:
        hooks = dict(l_hooks)
        for event in FORCE_HOOK_EVENTS:
            if event in t_hooks:
                hooks[event] = t_hooks[event]  # template authoritative; [] clears it
            # template silent on this event -> leave live untouched (never delete)
        for event, value in t_hooks.items():
            if event not in FORCE_HOOK_EVENTS and event not in hooks:
                hooks[event] = value
        result["hooks"] = hooks

    # DEFAULT: any remaining template top-level key fills only when absent in live
    for key, value in template.items():
        if key not in result:
            result[key] = value

    return result


def load_template():
    raw = (REPO / "settings.json.template").read_text()
    raw = raw.replace("__HOME__", str(Path.home()))
    try:
        return json.loads(raw)
    except json.JSONDecodeError as exc:
        fail(f"settings.json.template is not valid JSON: {exc}")


def merge_settings(dry_run, backup):
    step("[3/4] merging settings.json")

    tmpl_path = REPO / "settings.json.template"
    if not tmpl_path.exists():
        fail("settings.json.template not found")

    template = load_template()
    settings_path = CLAUDE_DIR / "settings.json"
    live = {}
    if settings_path.exists():
        try:
            live = json.loads(settings_path.read_text())
        except json.JSONDecodeError as exc:
            fail(f"existing settings.json is not valid JSON: {exc}")

    merged = merge_settings_data(template, live)

    if merged == live:
        ok("settings.json (already up to date)")
        return

    backup.save(settings_path)
    text = json.dumps(merged, indent=2, ensure_ascii=False) + "\n"

    if dry_run:
        ok("settings.json (would merge; live keys preserved)")
        info(f"keys after merge: {', '.join(merged.keys())}")
        added = [k for k in merged if k not in live]
        if added:
            info(f"added from template: {', '.join(added)}")
        hooks = merged.get("hooks", {})
        if hooks:
            info(f"hook events: {', '.join(hooks.keys())}")
        return

    settings_path.write_text(text)
    ok("settings.json (merged)")


# ─────────────────────────────────────────────────────────────
# Step 4: merge mcp.json into ~/.claude.json (additive)
# ─────────────────────────────────────────────────────────────
def merge_mcp(dry_run):
    step("[4/4] merging mcpServers into ~/.claude.json")

    mcp_path = REPO / "mcp.json"
    if not mcp_path.exists():
        warn("mcp.json not found, skipping")
        return

    try:
        mcp = json.loads(mcp_path.read_text())
    except json.JSONDecodeError as exc:
        fail(f"mcp.json is not valid JSON: {exc}")

    claude_path = Path.home() / ".claude.json"
    claude = {}
    if claude_path.exists():
        try:
            claude = json.loads(claude_path.read_text())
        except json.JSONDecodeError as exc:
            fail(f"existing ~/.claude.json is not valid JSON: {exc}")

    existing = claude.get("mcpServers", {})
    added = [k for k in mcp.get("mcpServers", {}) if k not in existing]

    if not added:
        ok("already up to date")
        return

    if dry_run:
        ok(f"would add: {', '.join(added)}")
        return

    for key in added:
        existing[key] = mcp["mcpServers"][key]
    claude["mcpServers"] = existing
    claude_path.write_text(json.dumps(claude, indent=2) + "\n")
    ok(f"added: {', '.join(added)}")


# ─────────────────────────────────────────────────────────────
def main():
    dry_run = "--dry-run" in sys.argv[1:]
    stamp = datetime.now().strftime("%Y%m%d-%H%M%S")
    backup = Backup(dry_run, stamp)

    if dry_run:
        print("DRY RUN — no files will be written.\n")

    preflight()
    CLAUDE_DIR.mkdir(parents=True, exist_ok=True)
    link_dirs(dry_run, backup)
    merge_settings(dry_run, backup)
    merge_mcp(dry_run)

    print("")
    if dry_run:
        print("Dry run complete. Re-run without --dry-run to apply.")
    else:
        if backup.used:
            print(f"Backup of replaced files: {backup.root}")
        print(f"Done. Config installed to {CLAUDE_DIR}")


if __name__ == "__main__":
    main()
