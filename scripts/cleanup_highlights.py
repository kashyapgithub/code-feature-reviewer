#!/usr/bin/env python3
# ─────────────────────────────────────────────────────────────
# 🚦 CLI ──► 🧠 Logic ──► 🗑️ Cleanup
# ─────────────────────────────────────────────────────────────
#
# ╔════════════════════════════════════════════════════════════╗
# ║  ⚡ FEATURE-TRACE: Feature Tracing                            ║
# ║  Role: 🧠 logic                                               ║
# ║  Layer: 📜 scripts  │  Part 4 of 5                            ║
# ╚════════════════════════════════════════════════════════════╝
#
"""
cleanup_highlights.py
─────────────────────
Removes all feature-trace highlight comments previously injected by
inject_highlights.py. Supports surgical removal of specific features.
"""

import argparse
import json
import os
import re
import sys
from datetime import datetime


# ─────────────────────────────────────────────────────────────
# Patterns that identify injected highlight comment lines
# These must match EXACTLY what inject_highlights.py generates.
# ─────────────────────────────────────────────────────────────

# Matches box-drawing characters used in header/footer
HIGHLIGHT_PATTERNS = [
    re.compile(r"^\s*(//|#)\s*╔[═]+╗\s*$"),          # top border
    re.compile(r"^\s*(//|#)\s*║\s+"),                  # content rows
    re.compile(r"^\s*(//|#)\s*╚[═]+╝\s*$"),           # bottom border
    re.compile(r"^\s*(//|#)\s*└─\s*END FEATURE-TRACE"),# footer
    re.compile(r"^\s*(//|#)\s*$"),                     # spacer line
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
        # For simplicity, we match the name in content/footer rows.
        if "FEATURE-TRACE:" in line and feature.lower() in line.lower():
            return True
        return False 

    return True


def clean_file(filepath: str, dry_run: bool = False, feature: str = None) -> int:
    """
    Remove highlight comment lines from a file.
    If 'feature' is provided, ONLY removes lines belonging to that feature.
    """
    try:
        with open(filepath, "r", encoding="utf-8") as f:
            original_lines = f.readlines()
    except (UnicodeDecodeError, PermissionError) as e:
        print(f"⚠️  Could not read {filepath}: {e}")
        return 0

    # Filter out highlight lines
    if feature:
        # Surgical strip: only remove lines that are highlight lines AND match the feature
        cleaned_lines = [l for l in original_lines if not (is_highlight_line(l, feature=feature))]
    else:
        # Broad strip: remove ALL highlight lines
        cleaned_lines = [l for l in original_lines if not is_highlight_line(l)]

    removed_count = len(original_lines) - len(cleaned_lines)

    if removed_count == 0:
        return 0

    if dry_run:
        print(f"[DRY RUN] Would remove {removed_count} highlight line(s) from: {filepath}")
        return removed_count

    with open(filepath, "w", encoding="utf-8") as f:
        f.writelines(cleaned_lines)

    print(f"🧹 Cleaned {removed_count} line(s) from: {filepath}:1")
    return removed_count


def load_manifest(manifest_path: str) -> dict:
    """Load existing manifest or return empty structure."""
    if os.path.exists(manifest_path):
        with open(manifest_path, "r") as f:
            try:
                data = json.load(f)
                if isinstance(data, dict) and "features" in data:
                    return data
                return {"features": {}}
            except json.JSONDecodeError:
                return {"features": {}}
# └─ END FEATURE-TRACE: Feature Tracing ──────────────────────
    return {"features": {}}


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
                abs_p = os.path.abspath(p)
                lines.append(f"- [ ] [{p}](file://{abs_p})")
            lines.append("")
            lines.append("---")
            lines.append("")

    with open(dashboard_path, "w", encoding="utf-8") as f:
        f.write("\n".join(lines))
    print(f"🖥️  Dashboard updated: {dashboard_path}:1")


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


def delete_manifest(manifest_path: str, dry_run: bool = False) -> None:
    """Remove the manifest file after cleanup."""
    if dry_run:
        print(f"[DRY RUN] Would delete manifest: {manifest_path}")
        return
    if os.path.exists(manifest_path):
        os.remove(manifest_path)
        print(f"🗑️  Deleted manifest: {manifest_path}:1")


def collect_source_files(root: str = ".") -> list[str]:
    """Find all source files in the current directory tree."""
    SOURCE_EXTENSIONS = {
        ".js", ".ts", ".jsx", ".tsx", ".mjs", ".cjs",
        ".py", ".go", ".rs", ".rb",
        ".java", ".kt", ".php", ".swift",
        ".c", ".cpp", ".h",
        ".vue", ".svelte", ".sh", ".bash",
    }
    SKIP_DIRS = {
        "node_modules", ".git", "dist", "build",
        "__pycache__", ".next", "vendor", "venv", ".venv",
    }

    found_files = []
    for dirpath, dirnames, filenames in os.walk(root):
        dirnames[:] = [d for d in dirnames if d not in SKIP_DIRS]
        for f in filenames:
            _, ext = os.path.splitext(f)
            if ext.lower() in SOURCE_EXTENSIONS:
                found_files.append(os.path.join(dirpath, f))
    return found_files


def main():
    parser = argparse.ArgumentParser(
        description="Remove feature-trace highlight comments from source files."
    )
    parser.add_argument(
        "--manifest",
        default=".feature-trace-manifest.json",
        help="Path to the manifest JSON (default: .feature-trace-manifest.json)",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Show what would be cleaned without modifying any files",
    )
    parser.add_argument(
        "--force",
        action="store_true",
        help="Scan all source files even without a manifest (slower, but thorough)",
    )
    parser.add_argument(
        "--feature",
        help="Optional: Only clean highlights for a specific feature",
    )

    args = parser.parse_args()
    manifest = load_manifest(args.manifest)

    # ── Mode 1: Use manifest (fast, targeted) ────────────────
    if manifest.get("features") and not args.force:
        features_data = manifest["features"]
        
        target_features = []
        if args.feature:
            if args.feature in features_data:
                target_features = [args.feature]
            else:
                print(f"⚠️  Feature '{args.feature}' not found in manifest.")
                sys.exit(1)
        else:
            target_features = list(features_data.keys())

        total_removed = 0
        cleaned_count = 0

        for f_name in target_features:
            print(f"\n🔍 Cleaning highlights for feature: '{f_name}'")
            files = features_data[f_name].get("files", [])
            
            for entry in files:
                filepath = entry.get("path", "")
                if not filepath or not os.path.exists(filepath):
                    continue

                removed = clean_file(filepath, dry_run=args.dry_run, feature=f_name)
                if removed > 0:
                    total_removed += removed
                    cleaned_count += 1
            
            if not args.dry_run:
                del features_data[f_name]

        if not args.dry_run:
            if not features_data:
                delete_manifest(args.manifest, dry_run=False)
                if os.path.exists("PLUTO_DASHBOARD.md"):
                    os.remove("PLUTO_DASHBOARD.md")
                    print_alert("IMPORTANT", "Deleted dashboard: PLUTO_DASHBOARD.md")
            else:
                with open(args.manifest, "w") as f:
                    json.dump(manifest, f, indent=2)
                update_dashboard("PLUTO_DASHBOARD.md", manifest)
                
            print_alert("TIP", f"Cleanup complete! Removed {total_removed} lines.")
        else:
            print_alert("NOTE", f"Dry run: would remove ~{total_removed} line(s) from {cleaned_count} file(s)")

    # ── Mode 2: No manifest — scan everything (--force) ──────
    else:
        if not args.force and not manifest.get("features"):
            print(f"⚠️  No active features found in manifest '{args.manifest}'.")
            print("   Run with --force to scan all source files for highlight comments.")
            sys.exit(1)

        print(f"\n🔍 Force mode: scanning all source files for highlight comments...")
        source_files = collect_source_files(".")
        total_removed = 0
        cleaned_count = 0

        for filepath in source_files:
            removed = clean_file(filepath, dry_run=args.dry_run, feature=args.feature)
            if removed > 0:
                total_removed += removed
                cleaned_count += 1

        if os.path.exists(args.manifest) and not args.dry_run and not args.feature:
            delete_manifest(args.manifest, dry_run=False)

        if not args.dry_run:
            print_alert("TIP", f"Force cleanup complete! Removed {total_removed} lines.")
            print(f"   Source files scanned: {len(source_files)}")
        else:
            print_alert("NOTE", f"Dry run: scanned {len(source_files)} files. Would remove ~{total_removed} lines.")


if __name__ == "__main__":
    main()
