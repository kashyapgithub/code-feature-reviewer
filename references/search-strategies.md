#
# ╔════════════════════════════════════════════════════════════╗
# ║  ⚡ FEATURE-TRACE: Project Core                               ║
# ║  Role: 🔹 Strategies                                          ║
# ║  Layer: 📚 References  │  Part 4 of 4                         ║
# ╚════════════════════════════════════════════════════════════╝
#
# Search Strategies by Tech Stack

Reference this file when you've identified the tech stack in Phase 1.
Use the patterns below to supplement the generic searches in the main skill.

---

## React / Next.js (TypeScript or JavaScript)

### Find the component responsible for a feature:
```bash
# React components (functional + class)
grep -rn --include="*.{jsx,tsx}" \
  -iE "(const|function|class)\s+\w*FEATURE_TERM\w*" \
  src/ components/ pages/ app/

# Next.js page/route files
find . -path "*/pages/*FEATURE_TERM*" -o -path "*/app/*FEATURE_TERM*" 2>/dev/null

# Custom hooks
grep -rn --include="*.{js,ts}" \
  -iE "use[A-Z]\w*FEATURE_TERM\w*|useFeatureTerm" \
  src/ hooks/

# Context providers
grep -rn --include="*.{jsx,tsx}" \
  -iE "(createContext|Provider|useContext).*FEATURE_TERM" \
  src/
```

### Find API routes (Next.js):
```bash
# Next.js App Router API routes
find . -path "*/app/api/*" -name "route.ts" -o -name "route.js"

# Next.js Pages Router API
find . -path "*/pages/api/*" -name "*FEATURE_TERM*"

# tRPC routers
grep -rn --include="*.ts" \
  -iE "(router|procedure|query|mutation).*FEATURE_TERM" \
  src/server/ server/ trpc/
```

---

## Node.js / Express

```bash
# Express routes
grep -rn --include="*.{js,ts}" \
  -iE "router\.(get|post|put|delete|patch)\s*\(['\"].*FEATURE_TERM" \
  routes/ api/ src/routes/

# Middleware
grep -rn --include="*.{js,ts}" \
  -iE "(app\.use|middleware|express)\s*\(.*FEATURE_TERM" \
  middleware/ src/middleware/

# Controllers
find . -name "*FEATURE_TERM*controller*" -o -name "*controller*FEATURE_TERM*" 2>/dev/null

# Services
find . -name "*FEATURE_TERM*service*" -o -name "*service*FEATURE_TERM*" 2>/dev/null
```

---

## Python / Django

```bash
# Django views
grep -rn --include="*.py" \
  -iE "(class\s+\w*FEATURE_TERM\w*View|def\s+\w*FEATURE_TERM)" \
  */views.py views/

# Django URLs
grep -rn --include="*.py" \
  -iE "path\s*\(.*FEATURE_TERM" \
  */urls.py

# Django models
grep -rn --include="*.py" \
  -iE "class\s+\w*FEATURE_TERM\w*\s*\(.*Model" \
  */models.py models/

# Django serializers (DRF)
grep -rn --include="*.py" \
  -iE "class\s+\w*FEATURE_TERM\w*Serializer" \
  */serializers.py serializers/

# Django admin
grep -rn --include="*.py" \
  -i "FEATURE_TERM" \
  */admin.py
```

---

## Python / FastAPI
# └─ END FEATURE-TRACE: Project Core ─────────────────────────

```bash
# FastAPI route decorators
grep -rn --include="*.py" \
  -iE "@(app|router)\.(get|post|put|delete|patch)\s*\(\s*['\"].*FEATURE_TERM" \
  .

# Pydantic schemas
grep -rn --include="*.py" \
  -iE "class\s+\w*FEATURE_TERM\w*\s*\(BaseModel" \
  schemas/ models/

# Dependencies
grep -rn --include="*.py" \
  -iE "Depends\(.*FEATURE_TERM" \
  .
```

---

## Go

```bash
# HTTP handler functions
grep -rn --include="*.go" \
  -iE "func\s+\w*FEATURE_TERM\w*\s*\(w\s+http" \
  .

# Router registrations (gin, echo, chi, gorilla)
grep -rn --include="*.go" \
  -iE "\.(GET|POST|PUT|DELETE|PATCH|Handle)\s*\(\s*\".*FEATURE_TERM" \
  .

# Structs
grep -rn --include="*.go" \
  -iE "type\s+\w*FEATURE_TERM\w*\s+struct" \
  .

# Interface definitions
grep -rn --include="*.go" \
  -iE "type\s+\w*FEATURE_TERM\w*\s+interface" \
  .
```

---

## Ruby on Rails

```bash
# Controllers
find . -name "*FEATURE_TERM*_controller.rb" -o -name "*controller.rb" \
  | xargs grep -l "FEATURE_TERM" 2>/dev/null

# Routes
grep -n "FEATURE_TERM" config/routes.rb 2>/dev/null

# Models
find . -path "*/models/*FEATURE_TERM*" 2>/dev/null
grep -rn "FEATURE_TERM" app/models/ 2>/dev/null

# Views
find . -path "*/views/*FEATURE_TERM*" 2>/dev/null

# Jobs / Workers
find . -path "*/jobs/*FEATURE_TERM*" 2>/dev/null
```

---

## Vue.js / Nuxt

```bash
# Vue Single File Components
find . -name "*FEATURE_TERM*.vue" --exclude-dir={node_modules,dist}

# Composables (Nuxt 3 / Vue 3)
find . -path "*/composables/*FEATURE_TERM*"
grep -rn --include="*.{js,ts}" \
  -iE "export\s+(const|function)\s+use\w*FEATURE_TERM" \
  composables/

# Pinia stores
grep -rn --include="*.{js,ts}" \
  -iE "defineStore\s*\(\s*['\"]FEATURE_TERM" \
  stores/ store/

# Nuxt server routes
find . -path "*/server/api/*FEATURE_TERM*"
```

---

## Database / Schema Layer (any stack)

```bash
# SQL migrations
grep -rn --include="*.sql" \
  -i "FEATURE_TERM" \
  migrations/ db/migrate/

# Prisma schema
grep -n "FEATURE_TERM" prisma/schema.prisma 2>/dev/null

# Drizzle / TypeORM entities
grep -rn --include="*.{ts,js}" \
  -iE "@(Entity|Table|Column|OneToMany).*FEATURE_TERM" \
  .

# MongoDB Mongoose models
grep -rn --include="*.{js,ts}" \
  -iE "(Schema|model)\s*\(.*FEATURE_TERM" \
  models/ src/models/
```

---

## GraphQL

```bash
# Schema definitions
grep -rn --include="*.{graphql,gql}" \
  -i "FEATURE_TERM" \
  .

# Resolvers
grep -rn --include="*.{js,ts}" \
  -iE "(Query|Mutation|Subscription):\s*\{[^}]*FEATURE_TERM" \
  resolvers/ src/resolvers/

# Type definitions in code
grep -rn --include="*.{js,ts}" \
  -iE "gql\`[^']*FEATURE_TERM" \
  .
```

---

## Environment / Config Files

Always check these regardless of stack:

```bash
# Environment variables
grep -rn -i "FEATURE_TERM" \
  .env .env.example .env.local .env.production \
  config/ settings/ 2>/dev/null

# Feature flags
grep -rn -i "FEATURE_TERM" \
  --include="*.{json,yaml,yml,toml}" \
  config/ 2>/dev/null

# Docker / CI config
grep -rn -i "FEATURE_TERM" \
  docker-compose.yml Dockerfile .github/ 2>/dev/null
```

---

## Monorepo / Workspace Projects

When `packages/` or `apps/` directories exist:

```bash
# Find which workspace package owns the feature
ls packages/ apps/ 2>/dev/null

# Search across all packages
grep -rn \
  --include="*.{js,ts,jsx,tsx,py}" \
  --exclude-dir={node_modules,dist,build} \
  -i "FEATURE_TERM" \
  packages/ apps/ | head -60
```

---

## Tips for Reading Search Results

1. **File path depth** — files deeper in a `services/` or `domain/` folder are usually
   core business logic; files in `utils/` or `helpers/` are supporting code.
   
2. **Line density** — if a file has 10+ hits, it's almost certainly a primary owner.

3. **Name conventions** — if you see `authService.ts`, `AuthController.py`, `useAuth.ts`,
   `auth.routes.js` all in results — you've found the feature's full stack.

4. **Follow the imports** — the most important file is often the one everyone else imports.
   Once you identify candidates, grep for who imports them.
