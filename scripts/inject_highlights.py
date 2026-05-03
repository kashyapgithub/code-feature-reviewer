#!/usr/bin/env python3
# ─────────────────────────────────────────────────────────────
#     ┌────────────────┐          ┌───────────────────┐
#     │  🚦 CLI LOG    ├─────────►│  🧠 print_alert  │
#     └───────┬────────┘          └─────────┬─────────┘
#             │                             │
#             ▼                             ▼
#     ┌────────────────┐          ┌───────────────────┐
#     │  🎨 COLOR UI   ├─────────►│  📜 TERMINAL     │
#     └────────────────┘          └───────────────────┘
# ─────────────────────────────────────────────────────────────
# ─────────────────────────────────────────────────────────────
#     ┌────────────────┐          ┌───────────────────┐
#     │  🚦 DASHBOARD   ├─────────►│  🎨 GITHUB ALERTS │
#     └───────┬────────┘          └─────────┬─────────┘
#             │                             │
#             ▼                             ▼
#     ┌────────────────┐          ┌───────────────────┐
#     │  🧩 UI RENDERING◄─────────┤  📄 MISSION LOG   │
#     └────────────────┘          └───────────────────┘
# ─────────────────────────────────────────────────────────────
# ─────────────────────────────────────────────────────────────
#     ┌────────────────┐          ┌───────────────────┐
#     │  🚦 TRACE RUN   ├─────────►│  🧠 UPDATE DASH  │
#     └───────┬────────┘          └─────────┬─────────┘
#             │                             │
#             ▼                             ▼
#     ┌────────────────┐          ┌───────────────────┐
#     │  📜 DASHBOARD   ◄─────────┤  🗑️ CLEANUP DASH  │
#     └────────────────┘          └───────────────────┘
# ─────────────────────────────────────────────────────────────
# ─────────────────────────────────────────────────────────────
#     ┌────────────────┐          ┌───────────────────┐
#     │  🚦 CLI ENTRY  ├─────────►│  📜 STRING PARSE  │
#     └───────┬────────┘          └─────────┬─────────┘
#             │                             │
#             ▼                             ▼
#     ┌────────────────┐          ┌───────────────────┐
#     │  💾 PERSISTENCE ◄─────────┤  🗺️ MAP BUILDER   │
#     └────────────────┘          └───────────────────┘
# ─────────────────────────────────────────────────────────────
"""
inject_highlights.py
────────────────────
Injects bright visual highlight comments into source files to mark
code responsible for a specific feature. Called by the feature-tracer skill.

Usage:
    python inject_highlights.py \
        --feature "user authentication" \
        --files  "src/middleware/auth.js:12:34" "src/routes/login.ts:5:18" \
        --manifest .feature-trace-manifest.json

Arguments:
    --feature   Human-readable feature name (used in comment text)
    --files     Space-separated list of "filepath:start_line:end_line" entries
                You can pass multiple --files arguments or space-separate them.
    --manifest  Path to write the manifest JSON (default: .feature-trace-manifest.json)
    --dry-run   Print what would be injected without writing any files

Each "filepath:start_line:end_line" entry tells the script:
    - Which file to annotate
    - Which line range contains the relevant code block
"""

import argparse
import json
import os
import re
import sys
from datetime import datetime, timezone


# ─────────────────────────────────────────────────────────────
# Comment templates per language (detected from file extension)
# ─────────────────────────────────────────────────────────────

# Maps file extension → (line_comment_prefix, block_open, block_line, block_close)
LANG_COMMENT_STYLES = {
    # JavaScript / TypeScript family
    ".js":    ("//", "//", "//", "//"),
    ".ts":    ("//", "//", "//", "//"),
    ".jsx":   ("//", "//", "//", "//"),
    ".tsx":   ("//", "//", "//", "//"),
    ".mjs":   ("//", "//", "//", "//"),
    ".cjs":   ("//", "//", "//", "//"),
    # Python
    ".py":    ("#",  "#",  "#",  "#"),
    # Go
    ".go":    ("//", "//", "//", "//"),
    # Rust
    ".rs":    ("//", "//", "//", "//"),
    # Ruby
    ".rb":    ("#",  "#",  "#",  "#"),
    # Java / Kotlin
    ".java":  ("//", "//", "//", "//"),
    ".kt":    ("//", "//", "//", "//"),
    # PHP
    ".php":   ("//", "//", "//", "//"),
    # Swift
    ".swift": ("//", "//", "//", "//"),
    # C / C++
    ".c":     ("//", "//", "//", "//"),
    ".cpp":   ("//", "//", "//", "//"),
    ".h":     ("//", "//", "//", "//"),
    # Vue / Svelte (JS-style comments in script blocks)
    ".vue":   ("//", "//", "//", "//"),
    ".svelte":("//", "//", "//", "//"),
    # Shell
    ".sh":    ("#",  "#",  "#",  "#"),
    ".bash":  ("#",  "#",  "#",  "#"),
    # Markdown
    ".md":    ("#",  "#",  "#",  "#"),
}

# Default fallback for unknown extensions (using # as it is safe for many shell/config formats)
DEFAULT_COMMENT = ("#", "#", "#", "#")

# Width of the highlight box
BOX_WIDTH = 62

ROLE_EMOJIS = {
    "workflow":      "🛠️",
    "scripts":       "📜",
    "ui":            "🎨",
    "api":           "🔌",
    "backend":       "⚙️",
    "frontend":      "💻",
    "database":      "🗄️",
    "config":        "⚙️",
    "test":          "🧪",
    "docs":          "📄",
    "persistence":   "💾",
    "orchestration": "🎼",
    "logic":         "🧠",
    "routing":       "🚦",
}

LAYER_EMOJIS = {
    "core":          "🧠",
    "shell":         "🐚",
    "service":       "🏗️",
    "page":          "📄",
    "component":     "🧩",
    "style":         "💅",
    "scripts":       "📜",
    "ai skill":      "🤖",
    "references":    "📚",
    "general":       "📦",
}


def get_emoji(text: str, mapping: dict, default: str = "🔹") -> str:
    """Return an emoji for the given text if a mapping exists, else default."""
    return mapping.get(text.lower().strip(), default)


# Patterns that identify injected highlight comment lines
HIGHLIGHT_PATTERNS = [
    re.compile(r"^\s*(//|#)\s*╔[═]+╗\s*$"),          # top border
    re.compile(r"^\s*(//|#)\s*║\s+"),                  # content rows
    re.compile(r"^\s*(//|#)\s*╚[═]+╝\s*$"),           # bottom border
    re.compile(r"^\s*(//|#)\s*└─\s*END FEATURE-TRACE"),# footer
    re.compile(r"^\s*(//|#)\s*🗺️ FEATURE MAP:"),       # feature map header
    re.compile(r"^\s*(//|#)\s*$"),                     # spacer line (just the prefix)
]


def is_highlight_line(line: str, feature: str = None) -> bool:
    """
    Return True if this line is an injected highlight comment.
    If 'feature' is provided, only returns True if the line belongs to THAT feature.
    """
    is_any_highlight = any(pattern.match(line) for pattern in HIGHLIGHT_PATTERNS)
    
    if not is_any_highlight:
        return False
        
    if feature:
        # Check if the line contains the feature name (header/footer rows)
        # Note: Border and spacer lines don't have the name, so we only strip them
        # if they are part of a block we've identified as belonging to this feature.
        # For simplicity, we match the name in content/footer rows.
        if "FEATURE-TRACE:" in line and feature.lower() in line.lower():
            return True
        # If it's a border/spacer, we return True if we want a broad sweep (feature=None)
        # but for surgical stripping, we'll handle borders differently.
        return False 

    return True


def strip_specific_highlights(lines: list[str], feature: str) -> list[str]:
    """
    Surgically remove a specific feature block (header, content, footer, spacers).
    """
    new_lines = []
    in_target_block = False
    
    # We look for the start marker for THIS feature
    # Header row 2 looks like: // ║  ⚡ FEATURE-TRACE: [Feature Name]
    header_pattern = re.compile(rf"FEATURE-TRACE:.*{re.escape(feature)}", re.IGNORECASE)

    # First pass: identify which lines belong to THIS feature
    # We use a simple state machine: if we see the header, we start stripping until the footer.
    i = 0
    while i < len(lines):
        line = lines[i]
        if is_highlight_line(line) and header_pattern.search(line):
            # We found the start of our target feature block!
            # Backtrack to find the preceding spacer and top border
            # Then skip until we find the footer.
            
            # This is complex, so let's use a simpler heuristic:
            # Just strip lines that match the feature name directly for now.
            pass
        
        # Actually, let's keep it robust:
        if feature.lower() in line.lower() and is_highlight_line(line):
            # Strip this specific line
            pass
        elif is_highlight_line(line) and not feature:
            # Strip all if no feature provided
            pass
        else:
            new_lines.append(line)
        i += 1
    return new_lines


def get_comment_style(filepath: str) -> tuple:
    """Return the comment prefix tuple for the given file extension."""
    _, ext = os.path.splitext(filepath)
    return LANG_COMMENT_STYLES.get(ext.lower(), DEFAULT_COMMENT)


def build_highlight_header(
    feature: str,
    role: str,
    part_index: int,
    part_total: int,
    layer: str,
    prefix: str,
) -> list[str]:
    """
    Build the bright top-of-block highlight comment lines.

    Returns a list of strings (each is one source line, no trailing newline).

    Example output (JS):
    """
    inner_width = BOX_WIDTH - 4  # accounts for "// ║  " and "  ║"

    def pad(text: str) -> str:
        """Right-pad text to fill inner box width."""
        return text + " " * max(0, inner_width - len(text))

    top    = f"{prefix} ╔{'═' * (BOX_WIDTH - 2)}╗"
    title  = f"{prefix} ║  ⚡ FEATURE-TRACE: {pad('FEATURE-TRACE: ' + feature)[len('FEATURE-TRACE: '):]}  ║"
    
    # Manually pad each content row
    title_text  = f"⚡ FEATURE-TRACE: {feature}"
    r_emoji = get_emoji(role, ROLE_EMOJIS)
    l_emoji = get_emoji(layer, LAYER_EMOJIS)

    role_text   = f"Role: {r_emoji + ' ' if r_emoji else ''}{role}" if role else ""
    layer_text  = f"Layer: {l_emoji + ' ' if l_emoji else ''}{layer}  │  Part {part_index} of {part_total}"

    def box_line(text: str) -> str:
        # Handle emoji width (most emojis are double-width in display but single char in string)
        # This is a simple approximation; true terminal width is hard.
        padded = text + " " * max(0, inner_width - len(text))
        return f"{prefix} ║  {padded}  ║"

    bottom = f"{prefix} ╚{'═' * (BOX_WIDTH - 2)}╝"
    spacer = f"{prefix}"

    lines = [spacer, top, box_line(title_text)]
    if role_text:
        lines.append(box_line(role_text))
    lines.append(box_line(layer_text))
    lines.append(bottom)
    lines.append(spacer)

    return lines


def build_highlight_footer(feature: str, prefix: str) -> str:
    """Build the small end-of-block marker line."""
    label = f"└─ END FEATURE-TRACE: {feature} "
    dashes = "─" * max(0, BOX_WIDTH - len(label) - 2)
    return f"{prefix} {label}{dashes}"


def build_feature_map(feature: str, diagram: str, prefix: str) -> list[str]:
    """
    Build a beautiful 'FEATURE MAP' block from the provided ASCII diagram.
    Handles both literal newlines and escaped '\\n' strings.
    """
    # Handle escaped newlines if passed from certain CLI environments
    diagram = diagram.replace("\\n", "\n")
    
    lines = [
        f"{prefix} ",
        f"{prefix} 🗺️ FEATURE MAP: {feature}",
        f"{prefix} ─────────────────────────────────────────────────────────────",
    ]
    for line in diagram.split("\n"):
        if line.strip():
            lines.append(f"{prefix} {line}")
    lines.append(f"{prefix} ─────────────────────────────────────────────────────────────")
    lines.append(f"{prefix} ")
    return lines


def inject_into_file(
    filepath: str,
    start_line: int,   # 1-based line number where the relevant block starts
    end_line: int,     # 1-based line number where the relevant block ends
    feature: str,
    role: str,
    part_index: int,
    part_total: int,
    layer: str,
    dry_run: bool = False,
) -> list[int]:
    """
    Inject highlight header before `start_line` and footer after `end_line`.

    Returns the list of line numbers (in the MODIFIED file) where comments
    were injected — used for the manifest.
    """
    prefix, _, _, _ = get_comment_style(filepath)

    # Read original file
    with open(filepath, "r", encoding="utf-8") as f:
        raw_lines = f.readlines()

    # IDEMPOTENCY: Strip existing highlights for THIS SPECIFIC feature first.
    # This allows multiple features to coexist in the same file.
    original_lines = [l for l in raw_lines if not (is_highlight_line(l) and feature.lower() in l.lower())]
    
    # Also strip the generic borders/spacers if they were left orphaned (optional, but keep it clean)
    # For now, this is enough to prevent "Feature B" from wiping "Feature A".
    
    if len(original_lines) < len(raw_lines):
        # If we stripped lines, the user's start/end line numbers might be off
        # if they were calculated based on a file that ALREADY had highlights.
        # We assume the AI provides line numbers for the CLEAN version of the file.
        pass

    total_original = len(original_lines)

    # Clamp line numbers to valid range
    start_idx = max(0, min(start_line - 1, total_original))  # 0-based index
    end_idx   = max(start_idx, min(end_line - 1, total_original - 1))

    # Build header and footer comment lines
    header_lines = build_highlight_header(
        feature, role, part_index, part_total, layer, prefix
    )
    footer_line  = build_highlight_footer(feature, prefix)

    # Convert to file lines (add newlines)
    header_content = [line + "\n" for line in header_lines]
    footer_content = [footer_line + "\n"]

    # Splice into original content
    new_lines = (
        original_lines[:start_idx]    # lines before the block
        + header_content              # ← header injected here
        + original_lines[start_idx:end_idx + 1]  # the original block
        + footer_content              # ← footer injected here
        + original_lines[end_idx + 1:]  # lines after the block
    )

    if dry_run:
        print(f"\n[DRY RUN] Would inject into: {filepath}")
        print(f"  Header at line {start_line}, footer after line {end_line}")
        for line in header_lines:
            print(f"  {line}")
        print(f"  {footer_line}")
        return []

    # Write modified file
    with open(filepath, "w", encoding="utf-8") as f:
        f.writelines(new_lines)

    # Calculate the actual injected line numbers in the new file
    injected_line_numbers = (
        list(range(start_idx + 1, start_idx + 1 + len(header_lines)))  # header lines
        + [start_idx + 1 + len(header_lines) + (end_idx - start_idx) + 1]  # footer line
    )

    print(f"✅ Injected highlights into: {filepath}:{start_line}")
    return injected_line_numbers


def load_manifest(manifest_path: str) -> dict:
    """Load existing manifest or return empty structure."""
    if os.path.exists(manifest_path):
        with open(manifest_path, "r") as f:
            try:
                data = json.load(f)
                # Migration: if old format (list), convert to new format (dict)
                if isinstance(data, dict) and "features" in data:
                    return data
                return {"features": {}}
            except json.JSONDecodeError:
                return {"features": {}}
    return {"features": {}}


def save_manifest(manifest_path: str, manifest: dict) -> None:
    """Persist manifest to disk."""
    with open(manifest_path, "w") as f:
        json.dump(manifest, f, indent=2)
    print(f"📋 Manifest saved: {manifest_path}:1")


def update_dashboard(dashboard_path: str, manifest: dict) -> None:
    """Generate a beautiful PLUTO_DASHBOARD.md from the manifest."""
    lines = [
        "# 🔍 PLUTO MISSION DASHBOARD",
        f"*Last Updated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}*",
        "",
        "> [!NOTE]",
        "> This dashboard tracks all active feature traces. Keep this open in your editor for quick architectural navigation.",
        "",
        "---",
        ""
    ]
    
    features = manifest.get("features", {})
    if not features:
        lines.append("> [!TIP]")
        lines.append("> No active traces. Use `Pluto, trace [feature]` to begin.")
    else:
        for f_name, data in features.items():
            lines.append(f"## 🚀 Feature: {f_name}")
            lines.append(f"> [!IMPORTANT]")
            lines.append(f"> **Mission Active**: Trace recorded at {data.get('timestamp', 'Unknown')}")
            lines.append("")
            
            lines.append("### 📁 Mission Assets")
            for f_entry in data.get("files", []):
                p = f_entry.get("path", "")
                # Use absolute path for clickable link
                abs_p = os.path.abspath(p)
                lines.append(f"- [ ] [{p}](file://{abs_p})")
            lines.append("")
            lines.append("---")
            lines.append("")

    with open(dashboard_path, "w", encoding="utf-8") as f:
        f.write("\n".join(lines))
    print_alert("NOTE", f"Dashboard updated: {dashboard_path}")


def print_alert(alert_type: str, message: str) -> None:
    """Print a beautiful, color-coded alert to the CLI."""
    # ANSI Color Codes
    COLORS = {
        "IMPORTANT": "\033[91m", # Red
        "TIP":       "\033[92m", # Green
        "NOTE":      "\033[94m", # Blue
        "RESET":     "\033[0m",
        "BOLD":      "\033[1m",
    }
    
    icon = "⚡" if alert_type == "IMPORTANT" else "💡" if alert_type == "TIP" else "ℹ️"
    color = COLORS.get(alert_type, COLORS["RESET"])
    reset = COLORS["RESET"]
    bold  = COLORS["BOLD"]
    
    width = 70
    border = f"{color}╔{'═' * (width - 2)}╗{reset}"
    footer = f"{color}╚{'═' * (width - 2)}╝{reset}"
    
    print(f"\n{border}")
    print(f"{color}║  {bold}[!{alert_type}]{reset} {icon} {message}")
    print(f"{footer}")


def parse_file_arg(file_arg: str) -> tuple[str, int, int]:
    """
    Parse a file argument in the format "filepath:start_line:end_line".
    Returns (filepath, start_line, end_line).
    Falls back to (filepath, 1, 10) if line numbers are missing.
    """
    parts = file_arg.rsplit(":", 2)
    if len(parts) == 3:
        filepath, start, end = parts
        try:
            return filepath.strip(), int(start), int(end)
        except ValueError:
            pass
    elif len(parts) == 1:
        return parts[0].strip(), 1, 10
    # Fallback
    return file_arg.strip(), 1, 10


# ─────────────────────────────────────────────────────────────
# CLI entrypoint
# ─────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(
        description="Inject feature-trace highlight comments into source files."
    )
    parser.add_argument(
        "--feature",
        required=True,
        help='Feature name (e.g. "user authentication")',
    )
    parser.add_argument(
        "--files",
        nargs="+",
        required=True,
        help='Files to annotate: "path/to/file.ts:start_line:end_line". '
             'Role and layer are optional: prepend them as "role|layer|path:start:end"',
    )
    parser.add_argument(
        "--manifest",
        default=".feature-trace-manifest.json",
        help="Path for the manifest JSON (default: .feature-trace-manifest.json)",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Print what would happen without modifying any files",
    )
    parser.add_argument(
        "--diagram",
        help="Optional: ASCII flow diagram to inject as a 'Feature Map' at the top of the first file",
    )

    args = parser.parse_args()

    feature    = args.feature
    total      = len(args.files)
    manifest   = load_manifest(args.manifest)

    # Initialize or update the specific feature entry
    manifest["features"][feature] = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "files": []
    }

    print(f"\n🔍 Injecting highlights for feature: '{feature}'")
    print(f"   Files to annotate: {total}\n")

    # If a diagram is provided, inject the Feature Map at the top of the FIRST file
    if args.diagram:
        first_file_arg = args.files[0]
        # Supporting role|layer|path format
        if "|" in first_file_arg:
             _, _, first_file_arg = first_file_arg.rsplit("|", 2)
        
        filepath, _, _ = parse_file_arg(first_file_arg)
        prefix, _, _, _ = get_comment_style(filepath)
        map_lines = build_feature_map(feature, args.diagram, prefix)
        
        if not args.dry_run:
            with open(filepath, "r", encoding="utf-8") as f:
                content = f.readlines()
            
            # Insert at top, but skip shebang if present
            insert_idx = 1 if content and content[0].startswith("#!") else 0
            new_content = content[:insert_idx] + [l + "\n" for l in map_lines] + content[insert_idx:]
            
            with open(filepath, "w", encoding="utf-8") as f:
                f.writelines(new_content)
            print(f"🗺️  Injected Feature Map into: {filepath}:1")

    for idx, file_arg in enumerate(args.files, start=1):
        # Support optional "role|layer|filepath:start:end" format
        role  = ""
        layer = "Unknown Layer"

        role = "Responsible Code"
        layer = "General"

        if "|" in file_arg:
            parts = file_arg.split("|")
            if len(parts) == 3:
                role, layer, file_arg = parts
            elif len(parts) == 2:
                role, file_arg = parts
                layer = "General"

        filepath, start_line, end_line = parse_file_arg(file_arg)

        if not os.path.exists(filepath):
            print(f"⚠️  Skipping (file not found): {filepath}")
            continue

        injected_lines = inject_into_file(
            filepath    = filepath,
            start_line  = start_line,
            end_line    = end_line,
            feature     = feature,
            role        = role,
            part_index  = idx,
            part_total  = total,
            layer       = layer,
            dry_run     = args.dry_run,
        )

        if injected_lines and not args.dry_run:
            # Add to the specific feature's file list
            manifest["features"][feature]["files"].append({
                "path":           filepath,
                "injected_lines": injected_lines,
            })
    
    if not args.dry_run:
        save_manifest(args.manifest, manifest)
        update_dashboard("PLUTO_DASHBOARD.md", manifest)
        inject_vscode_settings(dry_run=False)
        print_alert("TIP", f"Highlighted {total} file(s) for feature: '{feature}'")
        print(f"   To remove highlights: python3 scripts/cleanup_highlights.py")
    else:
        print_alert("NOTE", "Dry run complete — no files were modified")


def inject_vscode_settings(dry_run: bool = False) -> None:
    """
    Write (or merge) the .vscode/settings.json color config so that
    FEATURE-TRACE comments glow in the editor immediately — no manual setup.

    Strategy:
    - If .vscode/settings.json doesn't exist → write the full snippet.
    - If it exists but has no better-comments.tags → merge our tags in.
    - If better-comments.tags already exists → skip (don't overwrite user config).
    """
    settings_dir  = ".vscode"
    settings_path = os.path.join(settings_dir, "settings.json")

    # Locate the snippet bundled alongside this script
    skill_root    = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    snippet_path  = os.path.join(skill_root, "assets", "vscode-settings-snippet.json")

    if not os.path.exists(snippet_path):
        print("⚠️  VS Code color snippet not found — skipping editor color setup.")
        return

    # Load our snippet (strip JS-style // comments so json.loads works)
    with open(snippet_path, "r", encoding="utf-8") as f:
        raw = f.read()
    # Remove single-line comments (// ...) before parsing
    clean = re.sub(r"^\s*//.*$", "", raw, flags=re.MULTILINE)
    snippet = json.loads(clean)

    if dry_run:
        print(f"[DRY RUN] Would write VS Code color settings to: {settings_path}")
        return

    os.makedirs(settings_dir, exist_ok=True)

    if os.path.exists(settings_path):
        with open(settings_path, "r", encoding="utf-8") as f:
            try:
                existing = json.load(f)
            except json.JSONDecodeError:
                existing = {}

        # Only merge if better-comments.tags is not already set
        if "better-comments.tags" not in existing:
            existing.update(snippet)
            with open(settings_path, "w", encoding="utf-8") as f:
                json.dump(existing, f, indent=2)
            print(f"🎨 Merged color settings into: {settings_path}")
        else:
            print(f"ℹ️  Skipped VS Code settings (better-comments.tags already configured)")
    else:
        with open(settings_path, "w", encoding="utf-8") as f:
            json.dump(snippet, f, indent=2)
        print(f"🎨 Created VS Code color settings: {settings_path}")

    print("   Install 'Better Comments' or 'Todo Tree' extension to see colors.")


if __name__ == "__main__":
    main()
