---
name: sqlite-readonly-inspection
description: "Use when inspecting persisted sessions, messages, and agent runs through the read-only SQL endpoint."
version: 1.0.0
author: AI Agent Service Team
license: MIT
metadata:
  tags: [sqlite, sql, inspection, debugging]
  related_skills: []
---

# SQLite Read-only Inspection

## When to Use

Use this skill when:

- The operator wants to verify conversations were persisted.
- `/agent` returned a response but the database should be checked.
- Debugging session history or recent model outputs.
- Inspecting data through `/sql/query` without mutating the database.

## Safety Rules

Only use read-only SQL:

- `SELECT`
- `WITH`
- `PRAGMA`
- `EXPLAIN`

Do not use:

- `INSERT`
- `UPDATE`
- `DELETE`
- `DROP`
- `ALTER`
- `CREATE`
- multiple SQL statements in one request

## Useful Queries

List recent messages:

```bash
curl -X POST http://127.0.0.1:8020/sql/query \
  -H 'Content-Type: application/json' \
  -d '{"query":"SELECT id, session_id, role, content FROM messages ORDER BY id DESC LIMIT 20"}'
```

List recent agent runs:

```bash
curl -X POST http://127.0.0.1:8020/sql/query \
  -H 'Content-Type: application/json' \
  -d '{"query":"SELECT id, session_id, model, input_text, output_text FROM agent_runs ORDER BY id DESC LIMIT 10"}'
```

Check tables:

```bash
curl -X POST http://127.0.0.1:8020/sql/query \
  -H 'Content-Type: application/json' \
  -d '{"query":"SELECT name FROM sqlite_master WHERE type = '\''table'\'' ORDER BY name"}'
```

Count messages by role:

```bash
curl -X POST http://127.0.0.1:8020/sql/query \
  -H 'Content-Type: application/json' \
  -d '{"query":"SELECT role, COUNT(*) AS count FROM messages GROUP BY role"}'
```

## Direct File Inspection

If inside the project root and direct SQLite inspection is available:

```bash
sqlite3 ./data/agent.db '.tables'
sqlite3 ./data/agent.db 'SELECT id, session_id, role, content FROM messages ORDER BY id DESC LIMIT 20;'
```

Prefer `/sql/query` for application-level inspection because it exercises the same database URL and service path.

## Verification Checklist

- [ ] `/sql/query` accepts read-only query.
- [ ] Recent user and assistant messages exist.
- [ ] Recent agent runs include expected model name.
- [ ] No write SQL was executed.
