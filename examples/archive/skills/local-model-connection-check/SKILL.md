---
name: local-model-connection-check
description: "Use when diagnosing connectivity between AI Agent Service and a local OpenAI-compatible model gateway."
version: 1.0.0
author: AI Agent Service Team
license: MIT
metadata:
  tags: [local-model, openai-compatible, docker, networking, qwen]
  related_skills: [server-container-runbook]
---

# Local Model Connection Check

## When to Use

Use this skill when:

- `/agent` returns `500 Internal Server Error`.
- AI Agent Service `/health` is OK but model calls fail.
- The model health URL works on the host but not from a container.
- `LLM_BASE_URL` may incorrectly include `/health`.
- The deployment uses a local model such as `qwen3.5-35b`.

## Inputs Needed

- AI Agent Service URL, usually `http://127.0.0.1:8020`.
- Model health URL, for example `http://127.0.0.1:8080/api/v1/health`.
- Current `LLM_BASE_URL` from `.env`.
- Whether the service runs natively, in a manual Docker container, or via Docker Compose.

## Steps

1. Verify AI Agent Service health from the host:

```bash
curl http://127.0.0.1:8020/health
```

2. Verify model gateway health from the host:

```bash
curl http://127.0.0.1:8080/api/v1/health
```

3. Normalize the model base URL.

Correct:

```env
LLM_BASE_URL=http://host.docker.internal:8080/api/v1
```

Incorrect:

```env
LLM_BASE_URL=http://host.docker.internal:8080/api/v1/health
```

The app appends `/chat/completions` automatically.

4. If the service runs inside a manual Docker container, verify the container was created with host routing:

```bash
--add-host=host.docker.internal:host-gateway
```

5. From inside the container, verify the model gateway:

```bash
curl http://host.docker.internal:8080/api/v1/health
```

6. Restart the service after changing `.env`.

7. Run an agent smoke test:

```bash
curl -X POST http://127.0.0.1:8020/agent \
  -H 'Content-Type: application/json' \
  -d '{"message":"請用繁體中文簡短回答：模型連線測試"}'
```

## Expected Result

- `/health` returns `{"status":"ok"}`.
- Model health endpoint returns a successful response.
- `/agent` returns a JSON response with `reply`, `model`, and `session_id`.

## Common Failure Modes

### Wrong base URL

Symptom: model server health works, but `/agent` fails.

Fix: remove `/health` from `LLM_BASE_URL`.

### Container uses localhost incorrectly

Symptom: host can reach model, container cannot.

Fix: use `host.docker.internal` or the server LAN IP.

### Missing Docker host mapping

Symptom: `host.docker.internal` cannot resolve inside container.

Fix: recreate container with:

```bash
--add-host=host.docker.internal:host-gateway
```

## Verification Checklist

- [ ] AI Agent Service health OK.
- [ ] Model gateway health OK from host.
- [ ] Model gateway health OK from container if applicable.
- [ ] `LLM_BASE_URL` does not include `/health`.
- [ ] `/agent` smoke test returns a model response.
