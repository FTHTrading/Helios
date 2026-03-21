# Helios Terminology Refactor Plan

> Date: 2026-03-20
> Objective: Rename "bond" → "link" across the entire codebase to eliminate confusion with financial bond instruments

---

## Naming Decision

### Candidates evaluated

| Term | Pros | Cons | Verdict |
|------|------|------|---------|
| `connection` | Familiar, social | Generic, long, overloaded in DB/HTTP context | ❌ |
| `field_link` | Domain-specific | Too coupled to "field" metaphor | ❌ |
| `network_link` | Clear | Verbose for variable names | ❌ |
| `trust_link` | Implies trust | Trust has legal connotations | ❌ |
| `member_link` | Clear origin | Verbose | ❌ |
| `relationship_edge` | Graph-accurate | Too academic, long | ❌ |
| **`link`** | **Short, clear, graph-accurate, no financial connotation** | Low chance of keyword collision | **✅ SELECTED** |

### Why `link`

1. **Short** — `link` is 4 characters vs `bond` at 4 — zero code verbosity increase
2. **Clear** — universally understood as "connection between two things"
3. **No financial connotation** — nobody confuses `link` with a debt instrument
4. **Graph-standard** — links/edges are standard graph-theory terminology
5. **Already used** — `form_link`, `dissolve_link`, `get_links`, `link_count` all read naturally

---

## Scope of Changes

### 1. Database Model — `models/bond.py` → `models/link.py`

| Before | After |
|--------|-------|
| File: `models/bond.py` | File: `models/link.py` |
| Class: `Bond` | Class: `Link` |
| Table: `bonds` | Table: `links` |
| Method: `ordered_pair()` | Method: `ordered_pair()` (unchanged) |
| Column: `node_a` | `node_a` (unchanged) |
| Column: `node_b` | `node_b` (unchanged) |
| Config: `BOND_STATE_ACTIVE` | `LINK_STATE_ACTIVE` |
| Config: `BOND_STATE_INACTIVE` | `LINK_STATE_INACTIVE` |
| Config: `BOND_STATE_BOUND` | `LINK_STATE_BOUND` |

### 2. Member Model — `models/member.py`

| Before | After |
|--------|-------|
| Column: `bond_count` | Column: `link_count` |
| Method: `update_node_state()` references bond_count | References `link_count` |

### 3. Core Network — `core/network.py`

| Before | After |
|--------|-------|
| `form_bond()` | `form_link()` |
| `dissolve_bond()` | `dissolve_link()` |
| `get_bonds()` | `get_links()` |
| All docstrings referencing "bond" | Updated to "link" |
| Import `from models.bond import Bond` | `from models.link import Link` |

### 4. Core Rewards — `core/rewards.py`

| Before | After |
|--------|-------|
| Import `from models.bond import Bond` | `from models.link import Link` |
| All `Bond.` queries | `Link.` queries |
| All "bond" in docstrings/comments | "link" |

### 5. Core Identity — `core/identity.py`

| Before | After |
|--------|-------|
| `_get_bond_count()` | `_get_link_count()` |
| References to bond_count | `link_count` |

### 6. Core Validation — `core/validation.py`

| Before | After |
|--------|-------|
| `BondCreateSchema` | `LinkCreateSchema` |
| `BondDissolveSchema` | `LinkDissolveSchema` |
| Schema key: `"bond_create"` | `"link_create"` |
| Schema key: `"bond_dissolve"` | `"link_dissolve"` |

### 7. Core Node Telemetry — `core/node_telemetry.py`

| Before | After |
|--------|-------|
| `bond_count` references | `link_count` |

### 8. API Routes — `api/routes.py`

| Before | After |
|--------|-------|
| `/api/field/bond` (POST) | `/api/field/link` (POST) |
| `/api/field/bond/dissolve` (POST) | `/api/field/link/dissolve` (POST) |
| `/api/field/bonds/<id>` (GET) | `/api/field/links/<id>` (GET) |
| Function: `form_bond()` | `form_link()` |
| Function: `dissolve_bond()` | `dissolve_link()` |
| Function: `get_bonds()` | `get_links()` |
| All "bond" in docstrings | "link" |
| `validate_payload("bond_create", ...)` | `validate_payload("link_create", ...)` |
| `validate_payload("bond_dissolve", ...)` | `validate_payload("link_dissolve", ...)` |

### 9. Config — `config.py`

| Before | After |
|--------|-------|
| `FIELD_MAX_BONDS = 5` | `FIELD_MAX_LINKS = 5` |
| `FIELD_COOLDOWN_HOURS = 0` | `FIELD_COOLDOWN_HOURS = 0` (unchanged, already 0) |
| `BOND_STATE_ACTIVE = "active"` | `LINK_STATE_ACTIVE = "active"` |
| `BOND_STATE_INACTIVE = "inactive"` | `LINK_STATE_INACTIVE = "inactive"` |
| `BOND_STATE_BOUND = "bound"` | `LINK_STATE_BOUND = "bound"` |

### 10. Documentation

| File | Action |
|------|--------|
| `docs/*.md` | Update all references to "bond" → "link" |
| `prompts/*.md` | Update all references to "bond" → "link" |
| `README.md` | Update |
| `SYSTEM_MAP.md` | Update |
| `REPO_OVERVIEW.md` | Update |

### 11. Bootstrap/Test Scripts

| File | Action |
|------|--------|
| `_bond_founders.py` | Rename to `_link_founders.py`, update internals |
| `_bootstrap_founders.py` | Update Bond → Link references |
| `_inject_founders.py` | No changes needed (energy-only) |

---

## Database Migration Strategy

### SQLite (current dev)

Since SQLite has limited `ALTER TABLE` support and the dev database contains only test/founding data:

1. **Export founding member data** (13 members + 26 links)
2. **Drop and recreate** the `bonds` → `links` table
3. **Re-import founding data** with new schema

### PostgreSQL (future prod)

For production, use Alembic migration:

```python
# alembic migration
op.rename_table('bonds', 'links')
op.alter_column('members', 'bond_count', new_column_name='link_count')
```

---

## Backward Compatibility

### API versioning

The old `/api/field/bond` paths will be removed immediately. Since the system is pre-launch with no external consumers, this is a clean break. If backward compatibility were needed:

```python
# Temporary redirect (NOT implementing — clean break instead)
@field_bp.route("/bond", methods=["POST"])
def bond_redirect():
    return redirect(url_for("field.form_link"), code=308)
```

---

## Execution Order

1. Rename `models/bond.py` → `models/link.py`, update class/table names
2. Update `models/member.py` — `bond_count` → `link_count`
3. Update `config.py` — all `BOND_*` → `LINK_*`, `FIELD_MAX_BONDS` → `FIELD_MAX_LINKS`
4. Update `core/network.py` — all method names, imports, docstrings
5. Update `core/rewards.py` — imports and queries
6. Update `core/identity.py` — `_get_bond_count` → `_get_link_count`
7. Update `core/validation.py` — schema names and keys
8. Update `core/node_telemetry.py` — references
9. Update `api/routes.py` — endpoints, function names, schema keys
10. Update `app.py` — model import
11. Rebuild database (drop → recreate → re-seed founders)
12. Update docs
13. Run full test suite
14. Commit and push
