---
name: feature-tracer
description: >
  Traces any product feature or operation across an entire codebase — finding every file,
  function, component, route, hook, query, and config entry responsible for it. Use this skill
  whenever the user asks: "show me the code for X", "which files handle Y", "where is Z
  implemented", "trace the auth flow", "find everything related to payments", "what code runs
  when I click Submit", "show me the signup feature end to end", or any question framed around
  understanding WHERE and HOW a feature is implemented across multiple files.
  After tracing, this skill can inject bright visual highlight comments into the actual source
  files so the user can navigate to any file and instantly see the relevant lines — then clean
  them up on request. Works in Claude Code, Cursor, VS Code (via Claude/Copilot), and any
  AI tool with file system access. Trigger this skill aggressively — if the user says anything
  like "find the code for", "show me where", "trace the flow of", use it.
  IMPORTANT: Always perform the Trace Report and the Highlight Injection in a single response
  unless the user explicitly asks for "trace only".
---

# Feature Tracer Skill

You are performing **Feature Archaeology**: given a natural-language description of a feature
or operation, you will find every file in the codebase responsible for it, explain each file's
role, and optionally inject bright highlight comments so the user can visually navigate the code.

---

## Phase 0 — Understand the Request

Parse the user's query for:

| Field | Example |
|---|---|
| **Feature name** | "user authentication", "checkout flow", "dark mode toggle" |
| **Scope** | frontend only / backend only / full stack / a specific file type |
| **Mode** | `trace` (default) — report only \| `highlight` — also inject comments into files |
| **Cleanup** | If the user says "clean up" / "remove highlights" → run cleanup mode |

If the feature name is ambiguous, **make a best guess and proceed** — don't ask for clarification.
State your interpretation at the start: _"Tracing the feature: **user login flow**"_.
**Always aim to highlight specific functions/blocks (e.g. 10-50 lines) rather than entire files.**

---

## Phase 1 — Discover the Codebase

Before searching, understand the project layout:

```bash
# Get top-level structure (fast orientation)
find . -maxdepth 3 -type f \
  ! -path "*/node_modules/*" \
  ! -path "*/.git/*" \
  ! -path "*/dist/*" \
  ! -path "*/build/*" \
  ! -path "*/__pycache__/*" \
  ! -path "*/.next/*" \
  | head -80
```

Identify the tech stack from filenames:
- `package.json` → Node/JS/TS project
- `requirements.txt` / `pyproject.toml` → Python
- `go.mod` → Go
- `Cargo.toml` → Rust
- `pom.xml` / `build.gradle` → Java/Kotlin

Read the **search strategy reference** at `references/search-strategies.md` for stack-specific
search patterns before proceeding.

---

#
# ╔════════════════════════════════════════════════════════════╗
# ║  ⚡ FEATURE-TRACE: Project Core                               ║
# ║  Role: 🎼 Orchestration                                       ║
# ║  Layer: 🤖 AI Skill  │  Part 3 of 4                           ║
# ╚════════════════════════════════════════════════════════════╝
#
## Phase 2 — Multi-Signal Search

Run ALL of these search passes in parallel where possible. Every signal type can reveal
different responsible files.

### Signal 1 — Keyword Search (Broad Net)
```bash
# Replace FEATURE_TERM with the core noun from the feature name
grep -rn --include="*.{js,ts,jsx,tsx,py,go,rs,java,rb,php,vue,svelte}" \
  -i "FEATURE_TERM" \
  --exclude-dir={node_modules,.git,dist,build,__pycache__,.next,vendor} \
  . | head -60
```

### Signal 2 — Route / Endpoint Search
```bash
# Find API routes, page routes, URL handlers
grep -rn --include="*.{js,ts,py,go,rb}" \
  -iE "(route|path|endpoint|url|get|post|put|delete|patch)\s*[\(\"'\/].*FEATURE_TERM" \
  --exclude-dir={node_modules,.git,dist,build} \
  . | head -40
```

### Signal 3 — Function / Class Name Search
```bash
# Find function definitions, class names, component names
grep -rn --include="*.{js,ts,jsx,tsx,py,go,rs}" \
  -iE "(function|def|class|const|export|component)\s+\w*FEATURE_TERM\w*" \
  --exclude-dir={node_modules,.git,dist,build,__pycache__} \
  . | head -40
```

### Signal 4 — Import / Dependency Graph
```bash
# Find what imports the files already identified
# Replace FOUND_FILE with the most central file found so far
grep -rn --include="*.{js,ts,jsx,tsx,py}" \
  -iE "(import|require|from)\s+.*FOUND_FILE" \
  --exclude-dir={node_modules,.git,dist,build} \
  . | head -30
```

### Signal 5 — Config / Schema Search
```bash
# Features often have config entries, env vars, DB schemas
grep -rn \
  --include="*.{json,yaml,yml,env,toml,sql,prisma,graphql}" \
  -i "FEATURE_TERM" \
  --exclude-dir={node_modules,.git,dist} \
  . | head -30
```

### Signal 6 — Test Files
```bash
# Tests often reveal exactly what a feature does
grep -rn \
  --include="*.{test.js,spec.js,test.ts,spec.ts,test.py,_test.go}" \
  -i "FEATURE_TERM" \
  --exclude-dir={node_modules,.git} \
  . | head -20
```
# └─ END FEATURE-TRACE: Project Core ─────────────────────────

---

## Phase 3 — Rank & Deduplicate Results

After all searches, consolidate into a **ranked file list**:

### Ranking Criteria (score each file mentally)
| Criteria | Weight |
|---|---|
| File name directly matches feature term | ★★★★★ |
| Contains function/class named after feature | ★★★★ |
| Is imported by many other found files (hub file) | ★★★★ |
| Contains route/endpoint for feature | ★★★ |
| Contains business logic / core processing | ★★★ |
| Config / schema / migration for feature | ★★ |
| Test file for the feature | ★★ |
| Utility helper loosely related | ★ |

Aim for **5–15 files** in the final output. If you find 50+, focus on the most central ones.

---

## Phase 4 — Output the Trace Report

Output in this exact structure:

```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
🔍 FEATURE TRACE: [Feature Name]
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Found [N] files responsible for this feature.
[Optional: 1-sentence architectural summary]

📁 LAYER: [Frontend / Backend / API / Config / Tests]
────────────────────────────────────────────────

  📄 [folder/subfolder/filename.ext]  ← Lines [X–Y]
     Role: [What this file does for the feature in 1 sentence]
     Key code: [function name / class name / variable] at line [N]

  📄 [folder/subfolder/filename.ext]  ← Lines [X–Y]
     Role: [What this file does for the feature]
     Key code: [function name] at line [N]

📁 LAYER: [Next Layer]
────────────────────────────────────────────────

  📄 ...

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

Group files by architectural layer. Common layers:
`UI Components` → `Pages / Routes` → `API Handlers` → `Services / Business Logic`
→ `Data Access / DB` → `Config / Schema` → `Tests`

---

## Phase 5 — Instant Highlight Injection

After outputting the Trace Report, **immediately** run the `scripts/inject_highlights.py` script
to annotate the files. Use the `Role|Layer|filepath:start:end` format to ensure metadata is correct.

Example command:
```bash
python scripts/inject_highlights.py \
  --feature "feature name" \
  --files "Role|Layer|path:start:end" "Another Role|Another Layer|path:start:end"
```

Then conclude your response with:
_"✅ I have also injected bright highlight markers into these [N] files so you can see them in your editor."_

### Rules for Injecting Highlights

1. **Read the full file first** — understand the exact lines before editing
2. **One highlight block per relevant section** — don't over-annotate
3. **Inject ABOVE the function/class definition line**, not inside it
4. **Never modify the actual code** — only add/remove comment lines
5. **Track every injected file** in a local manifest file `.feature-trace-manifest.json`
   so you can cleanly remove them later

### Manifest Format
```json
{
  "feature": "user authentication",
  "timestamp": "2025-01-15T10:30:00Z",
  "files": [
    {
      "path": "src/middleware/auth.js",
      "injected_lines": [12, 34, 67]
    }
  ]
}
```

Run the highlight injector script: `scripts/inject_highlights.py`
Read its usage at the top of the file before running.

---

## Phase 6 — Cleanup Mode

If the user says: _"remove highlights"_, _"clean up"_, _"clear the trace"_:

1. Read `.feature-trace-manifest.json`
2. For each file listed, remove all lines matching this pattern:
   ```
   // ╔══ or // ║ or // ╚══ or // └─ END FEATURE-TRACE
   ```
3. Delete the manifest file
4. Confirm: _"✅ Removed all highlight comments from [N] files."_

Run the cleanup script: `scripts/cleanup_highlights.py`

---

## Behavior Across Different Tools

| Tool | File Read | File Write (Highlights) | Clickable Paths |
|---|---|---|---|
| **Claude Code** | ✅ Full | ✅ Full | ✅ Terminal links |
| **Cursor** | ✅ Full | ✅ Full | ✅ Native |
| **VS Code + Claude** | ✅ If workspace open | ✅ If workspace open | ✅ Native |
| **Claude.ai (web)** | ✅ If uploaded | ❌ Cannot write | ❌ |
| **Gemini Code Assist** | ✅ | ✅ | ✅ |

In **Claude.ai (web)** — skip highlight injection, just provide the trace report.
Tell the user: _"Open each file and search for [function name] to find the relevant code."_

---

## Common Pitfalls to Avoid

- **Don't report `node_modules`** — never. Always exclude it.
- **Don't list 40 files** — be ruthless, keep it to the most responsible files.
- **Don't just grep keywords** — think about the DATA FLOW, not just text matches.
- **Don't modify code logic** — highlights are comment-only, always reversible.
- **Do check for framework-specific patterns** — Next.js pages, Django views, Rails controllers
  have conventions that make some files obvious candidates.

---

## Quick Examples

**User:** _"show me the code responsible for the dark mode toggle"_
→ Trace: CSS variables file, ThemeContext/Provider, toggle component, localStorage call, 
  any SSR hydration logic, Tailwind config.

**User:** _"which files handle file uploads"_
→ Trace: Upload component (UI), presigned URL endpoint (API), S3/storage service, 
  file size validator, DB record creator for file metadata.

**User:** _"trace the checkout flow"_
→ Trace: Cart component → Checkout page → Payment form → Stripe/payment API route
  → Order service → DB transaction → Email confirmation trigger.

---

## Reference Files

- `references/search-strategies.md` — Stack-specific grep patterns (React, Django, Rails, Go, etc.)
- `scripts/inject_highlights.py` — Injects bright comments into source files
- `scripts/cleanup_highlights.py` — Removes all injected comments
