#!/usr/bin/env python3
"""
cleanup_highlights.py
─────────────────────
Removes all feature-trace highlight comments previously injected by
inject_highlights.py. Uses the manifest file to find affected files,
then strips out every injected comment line.

Usage:
    python cleanup_highlights.py
    python cleanup_highlights.py --manifest .feature-trace-manifest.json
    python cleanup_highlights.py --dry-run

Arguments:
    --manifest  Path to the manifest JSON file (default: .feature-trace-manifest.json)
    --dry-run   Show what would be removed without modifying any files
    --force     Remove highlight comments even if manifest is missing
                (scans all source files in current directory)
"""

import argparse
import json
import os
import re
import sys


# ─────────────────────────────────────────────────────────────
# Patterns that identify injected highlight comment lines
# These must match EXACTLY what inject_highlights.py generates.
# ─────────────────────────────────────────────────────────────

# Matches box-drawing characters used in header/footer
HIGHLIGHT_PATTERNS = [
    re.compile(r"^\s*(//|#)\s*╔[═]+╗\s*$"),          # top border:    // ╔════╗
    re.compile(r"^\s*(//|#)\s*║\s+"),                  # content rows:  // ║  text  ║
    re.compile(r"^\s*(//|#)\s*╚[═]+╝\s*$"),           # bottom border: // ╚════╝
    re.compile(r"^\s*(//|#)\s*└─\s*END FEATURE-TRACE"),# footer:        // └─ END FEATURE-TRACE...
]

# Source file extensions to scan in --force mode
SOURCE_EXTENSIONS = {
    ".js", ".ts", ".jsx", ".tsx", ".mjs", ".cjs",
    ".py", ".go", ".rs", ".rb",
    ".java", ".kt", ".php", ".swift",
    ".c", ".cpp", ".h",
    ".vue", ".svelte", ".sh", ".bash",
}

# Directories to always skip
SKIP_DIRS = {
    "node_modules", ".git", "dist", "build",
    "__pycache__", ".next", "vendor", "venv", ".venv",
}


def is_highlight_line(line: str) -> bool:
    """Return True if this line is an injected highlight comment."""
    return any(pattern.match(line) for pattern in HIGHLIGHT_PATTERNS)


def clean_file(filepath: str, dry_run: bool = False) -> int:
    """
    Remove all highlight comment lines from the given file.

    Returns the number of lines removed.
    """
    try:
        with open(filepath, "r", encoding="utf-8") as f:
            original_lines = f.readlines()
    except (UnicodeDecodeError, PermissionError) as e:
        print(f"⚠️  Could not read {filepath}: {e}")
        return 0

    cleaned_lines   = [line for line in original_lines if not is_highlight_line(line)]
    removed_count   = len(original_lines) - len(cleaned_lines)

    if removed_count == 0:
        return 0  # Nothing to clean in this file

    if dry_run:
        print(f"[DRY RUN] Would remove {removed_count} highlight line(s) from: {filepath}")
        return removed_count

    with open(filepath, "w", encoding="utf-8") as f:
        f.writelines(cleaned_lines)

    print(f"🧹 Cleaned {removed_count} line(s) from: {filepath}")
    return removed_count


def load_manifest(manifest_path: str) -> dict | None:
    """Load manifest JSON. Returns None if the file does not exist."""
    if not os.path.exists(manifest_path):
        return None
    with open(manifest_path, "r") as f:
        return json.load(f)


def delete_manifest(manifest_path: str, dry_run: bool = False) -> None:
    """Remove the manifest file after cleanup."""
    if dry_run:
        print(f"[DRY RUN] Would delete manifest: {manifest_path}")
        return
    os.remove(manifest_path)
    print(f"🗑️  Deleted manifest: {manifest_path}")


def collect_source_files(root: str = ".") -> list[str]:
    """
    Walk the directory tree and collect all source files
    (used in --force mode when there's no manifest).
    """
    found = []
    for dirpath, dirnames, filenames in os.walk(root):
        # Prune ignored directories in-place so os.walk skips them
        dirnames[:] = [d for d in dirnames if d not in SKIP_DIRS]
        for filename in filenames:
            _, ext = os.path.splitext(filename)
            if ext.lower() in SOURCE_EXTENSIONS:
                found.append(os.path.join(dirpath, filename))
    return found


# ─────────────────────────────────────────────────────────────
# CLI entrypoint
# ─────────────────────────────────────────────────────────────

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

    args       = parser.parse_args()
    manifest   = load_manifest(args.manifest)

    # ── Mode 1: Use manifest (fast, targeted) ────────────────
    if manifest and not args.force:
        feature = manifest.get("feature", "unknown feature")
        files   = manifest.get("files", [])

        print(f"\n🔍 Cleaning highlights for feature: '{feature}'")
        print(f"   Files in manifest: {len(files)}\n")

        total_removed = 0
        cleaned_count = 0

        for entry in files:
            filepath = entry.get("path", "")
            if not filepath:
                continue
            if not os.path.exists(filepath):
                print(f"⚠️  Skipping (not found): {filepath}")
                continue

            removed = clean_file(filepath, dry_run=args.dry_run)
            if removed > 0:
                total_removed += removed
                cleaned_count += 1

        if not args.dry_run:
            delete_manifest(args.manifest, dry_run=False)
            print(f"\n✅ Cleanup complete!")
            print(f"   Files cleaned:    {cleaned_count}")
            print(f"   Lines removed:    {total_removed}")
        else:
            print(f"\n[DRY RUN] Would remove ~{total_removed} line(s) from {cleaned_count} file(s)")

    # ── Mode 2: No manifest — scan everything (--force) ──────
    elif args.force or manifest is None:
        if not args.force and manifest is None:
            print(f"⚠️  No manifest found at '{args.manifest}'.")
            print("   Run with --force to scan all source files for highlight comments.")
            sys.exit(1)

        print(f"\n🔍 Force mode: scanning all source files for highlight comments...")
        source_files  = collect_source_files(".")
        total_removed = 0
        cleaned_count = 0

        for filepath in source_files:
            removed = clean_file(filepath, dry_run=args.dry_run)
            if removed > 0:
                total_removed += removed
                cleaned_count += 1

        # Also remove manifest if it exists
        if os.path.exists(args.manifest) and not args.dry_run:
            delete_manifest(args.manifest, dry_run=False)

        if not args.dry_run:
            print(f"\n✅ Force cleanup complete!")
            print(f"   Source files scanned: {len(source_files)}")
            print(f"   Files cleaned:        {cleaned_count}")
            print(f"   Lines removed:        {total_removed}")
        else:
            print(f"\n[DRY RUN] Scanned {len(source_files)} files.")
            print(f"   Would clean {cleaned_count} file(s), removing ~{total_removed} line(s)")


if __name__ == "__main__":
    main()
