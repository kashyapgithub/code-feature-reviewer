# 🔍 PLUTO — Product-Level Universal Trace & Orchestrator

> [!TIP]
> **Token Efficient**: PLUTO uses a "Grep-First" strategy and local script execution to minimize context window usage.

> **"Pluto, trace the checkout flow."**  
> → Finds every file, explains the logic, and **highlights the code in your editor.**


---

### ⏱️ PLUTO in 60 Seconds
**PLUTO** turns AI "hallucinations" into **Visual Code Archaeology**. It solves the problem of "where is this feature implemented?" across complex, multi-file codebases.

1. **ARCHAEOLOGY**: Pluto performs a 6-pass search (Keyword, Route, Dependency, etc.) to find every scrap of code responsible for a feature.
2. **ILLUMINATION**: Pluto injects bright, non-destructive **box-art markers** (╔══ ⚡ ══╗) directly into your source files.
3. **NAVIGATION**: You open any file and follow the "golden trail" to see the execution flow with emojis (💾, 🧠, 🎼) guiding you.
4. **RECOVERY**: One command to strip all markers, leaving your codebase 100% untouched and original.

---

### 💡 Troubleshooting: Hidden Reports
In some terminal environments (like **Claude Code**), long reports or trace results may be automatically collapsed to keep the UI tidy. 

*   **To Unhide**: Look for a button that says `Worked for [X] min >` and **click it** to expand the full PLUTO report.
*   **Mission Dashboard**: If the CLI keeps hiding your reports, open **`PLUTO_DASHBOARD.md`** in your editor. This file is automatically updated with every trace and will **never** be hidden!

---

**PLUTO** is a Claude skill that performs **Feature Archaeology** — trace any product feature or operation across your entire codebase, then inject bright visual markers so you can navigate the code instantly.

---

## ✨ What It Does

| Step | What Happens |
|------|-------------|
| **Trace** | You describe a feature in plain English. Claude searches your codebase across 6 signal types and returns a ranked, layered file report. |
| **Highlight** | Claude injects bright box-art comments above every relevant code block in the actual source files. |
| **Cleanup** | Say "remove highlights" — every injected comment is stripped cleanly. Your code is untouched. |

---

## 🖥️ Compatible Tools

| Tool | Trace Report | File Highlights | Clickable Paths |
|------|-------------|-----------------|-----------------|
| **Claude Code** | ✅ | ✅ | ✅ Terminal links |
| **Cursor** | ✅ | ✅ | ✅ Native |
| **VS Code + Claude/Copilot** | ✅ | ✅ | ✅ Native |
| **Gemini Code Assist** | ✅ | ✅ | ✅ |
| **Claude.ai (web)** | ✅ | ❌ | ❌ |

---

## 🚀 Key Features

- **Multi-Signal Search** — Traces features across keywords, routes, dependencies, and logic using 6 search passes.
- **Visual Highlight Injection** — Injects non-destructive, high-visibility box-art comments into your source files.
- **Feature Flow Visualization** — Generates ASCII flow diagrams (e.g., `[Route] ──► [Logic] ──► [DB]`) to show how files connect.
- **Interactive CLI** — Prints `filepath:line` formatted output so you can **Cmd/Ctrl + Click** to jump straight to the code.
- **Automatic Emoji Mapping** — Smartly detects roles and layers to add context-aware icons (💾, 🧠, 🎼, 🤖).
- **Multi-Feature Support** — Can trace and highlight multiple distinct features in a single sequential session.
- **Idempotent Workflow** — Safely run traces or cleanups multiple times; the tool automatically manages old markers.
- **Zero Code modification** — Only comments are added or removed; your application logic remains 100% original.

---

## 💬 Example Prompts

```
"Show me all the code responsible for user authentication"
"Which files handle file uploads?"
"Trace the dark mode toggle end to end"
"Find everything related to the payment flow"
"What code runs when I click the Submit button?"
"highlight the signup feature"
"remove highlights"
```

---

## 📦 What's Inside

```
feature-tracer/
├── SKILL.md                          # Main skill — Claude reads this
├── README.md                         # This file
├── references/
│   └── search-strategies.md          # Stack-specific grep patterns
└── scripts/
    ├── inject_highlights.py          # Injects bright comments into source files
    └── cleanup_highlights.py         # Removes all injected comments cleanly
```

---

## 🔦 What a Highlight Looks Like

When you say **"highlight the auth flow"**, Claude injects this **above** your code:

```ts
export function authMiddleware(req, res, next) {
  // ... your original code, completely untouched
}
```

- Every file is tagged with its part number (`Part 3 of 8`) so you see the full scope
- **Never modifies your actual code** — comment-only, fully reversible

---

## 🎨 Actual Editor Colors

The inject script automatically writes `.vscode/settings.json` into your project so the comments **glow with real color** — no manual setup.

| Comment Part | Color |
|---|---|
| `╔══╗` / `╚══╝` borders | Dark amber background `#3D2E00`, amber text |
| `║` content rows | Dim amber background `#2A1F00`, gold text |
| `└─ END` footer | Very dark background, orange text |

**Requires one free extension** (install either one):

- [Better Comments](https://marketplace.visualstudio.com/items?itemName=aaron-bond.better-comments) — colors by comment prefix pattern
- [Todo Tree](https://marketplace.visualstudio.com/items?itemName=Gruntfunn.todo-tree) — also shows all traces in the sidebar tree view

**For Cursor** — paste the contents of `assets/vscode-settings-snippet.json` into your Cursor settings. Cursor respects the same `better-comments` config.

If you'd rather pick your own colors, edit `assets/vscode-settings-snippet.json` before running the inject script.

---

## 🧠 How the Trace Works

Claude runs **6 parallel search signals** across your codebase:

1. **Keyword search** — broad net across all source files
2. **Route / endpoint search** — finds API handlers and page routes
3. **Function / class name search** — finds named owners of the feature
4. **Import graph** — finds what imports the already-discovered files
5. **Config / schema search** — finds env vars, DB schema, feature flags
6. **Test files** — tests often reveal exactly what a feature does

Results are ranked by centrality (hub files score higher), deduplicated, and grouped by architectural layer:

```
📁 UI Components
   📄 src/components/LoginForm.tsx  ← Lines 1–120
      Role: Renders the login form and dispatches auth action
      Key code: LoginForm component at line 12

📁 Pages / Routes
   📄 src/pages/login.tsx  ← Lines 1–45
      Role: Next.js page wrapping LoginForm, handles redirects

📁 API Handlers
   📄 src/app/api/auth/route.ts  ← Lines 1–60
      Role: POST /api/auth — validates credentials, issues JWT

📁 Services / Business Logic
   📄 src/services/authService.ts  ← Lines 12–89
      Role: Core auth logic — bcrypt comparison, token generation

📁 Config / Schema
   📄 prisma/schema.prisma  ← Lines 34–52
      Role: User model definition with password hash field
```

---

## 🛠️ Supported Stacks

The `references/search-strategies.md` file contains framework-specific patterns for:

- **React / Next.js** — components, hooks, App Router API routes, tRPC
- **Node.js / Express** — routes, middleware, controllers, services
- **Python / Django** — views, URLs, models, serializers, admin
- **Python / FastAPI** — route decorators, Pydantic schemas, dependencies
- **Go** — HTTP handlers, router registrations, structs, interfaces
- **Ruby on Rails** — controllers, routes, models, views, jobs
- **Vue.js / Nuxt** — SFCs, composables, Pinia stores, server routes
- **GraphQL** — schema definitions, resolvers, type definitions
- **Database** — SQL migrations, Prisma, Drizzle, Mongoose models
- **Monorepos** — multi-package workspace traversal

---

## ⚙️ Scripts Reference

### `inject_highlights.py`

Injects highlight comments into source files and tracks them in a manifest.

```bash
python scripts/inject_highlights.py \
  --feature "user authentication" \
  --files "src/middleware/auth.ts:12:34" "src/services/authService.ts:5:89" \
  --manifest .feature-trace-manifest.json

# Dry run (preview without writing)
python scripts/inject_highlights.py --feature "auth" --files "src/auth.ts:1:50" --dry-run
```

**File format:** `"filepath:start_line:end_line"` — with optional `"role|layer|filepath:start:end"`

### `cleanup_highlights.py`

Removes all injected highlight comments cleanly.

```bash
# Uses manifest (fast, targeted)
python scripts/cleanup_highlights.py

# Force scan entire project (no manifest needed)
python scripts/cleanup_highlights.py --force

# Preview without modifying files
python scripts/cleanup_highlights.py --dry-run
```

---

## 🔒 Safety Guarantees

- **Zero code modification** — only comment lines are ever added or removed
- **Manifest tracking** — every injected line is recorded so cleanup is precise
- **Idempotent injection** — running highlights twice is safe; old markers are automatically replaced
- **Idempotent cleanup** — running cleanup twice is safe, no double-removal
- **Force mode** — even without a manifest, cleanup can scan and strip all markers
- **Encoding safe** — reads/writes files as UTF-8 with graceful error handling

---

## 📥 Installation

### The Quickest Way (npx)
In any project directory, run:
```bash
npx pluto-tracer setup
```
This will instantly drop the **PLUTO** skill, scripts, and search references into your project.

### Claude Code
```bash
# Drop the skill folder into your Claude skills directory
cp -r feature-tracer ~/.claude/skills/
```

### Cursor / VS Code
Point your AI assistant's skill/context path to the `feature-tracer/` folder, or paste the contents of `SKILL.md` into your system prompt / rules file.

### Claude.ai (web)
Upload `SKILL.md` as a file at the start of your conversation. Trace reports work fully; file highlights require local script execution.

## 🚀 Using in a New Project

To use **PLUTO** in a different codebase, simply ensure your AI assistant has access to the `SKILL.md` file and the `scripts/` directory.

### Method 1: The npx Shot (Recommended)
Run this in your new project's root:
```bash
npx pluto-tracer setup
```

### Method 2: Manual Drop-in
Copy the `feature-tracer/` folder into your new project. Tell your AI: *"Read SKILL.md and use it to trace features."*

### Method 3: Global Rules (Cursor / VS Code)
1. Copy the contents of `SKILL.md` into your project's `.cursorrules` or `.clauderules` file.
2. Keep the `scripts/` folder in your project root so the AI can execute them.

### Method 4: Claude Code CLI
Copy the folder to your global skills directory:
```bash
cp -r feature-tracer ~/.claude/skills/
```

---

## 📄 License

MIT — use it, fork it, build on it.
