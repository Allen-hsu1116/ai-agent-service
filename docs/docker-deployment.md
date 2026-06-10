# Docker Deployment Guide

這份文件說明如何在 Linux 環境用 Docker 啟動 AI Agent Service。若你會自己建立 container 並進 container 執行指令，優先看第 4 節；若要使用 Docker Compose，請看第 5 節。

## 1. Prerequisites

Linux 主機需要先安裝：

- Docker Engine
- Docker Compose v2
- Git

Ubuntu / Debian 範例：

```bash
sudo apt-get update
sudo apt-get install -y ca-certificates curl git

# Install Docker using the official convenience script.
curl -fsSL https://get.docker.com | sudo sh

# Optional: allow current user to run docker without sudo.
sudo usermod -aG docker $USER
newgrp docker

docker --version
docker compose version
```

> Production 環境建議依照 Docker 官方文件安裝與管理套件來源。

## 2. Clone Project

```bash
git clone https://github.com/Allen-hsu1116/ai-agent-service.git
cd ai-agent-service
```

## 3. Configure Environment

複製環境變數範例：

```bash
cp .env.example .env
```

如果你是要在 server 上接本機地端模型 `qwen3.5-35b`，可以改用 server 範例：

```bash
cp .env.server.example .env
```

編輯 `.env`：

```bash
nano .env
```

線上 OpenAI-compatible API 範例：

```env
AI_PROVIDER=openai-compatible
LLM_BASE_URL=https://api.openai.com/v1
LLM_MODEL=gpt-4o-mini
LLM_API_KEY=your_api_key_here
LLM_TEMPERATURE=0.2
DATABASE_URL=sqlite:///./data/agent.db
```

如果之後要接地端 OpenAI-compatible endpoint，例如 vLLM、Ollama、LM Studio、llama.cpp server，可以改成：

```env
AI_PROVIDER=openai-compatible
LLM_BASE_URL=http://host.docker.internal:8080/api/v1
LLM_MODEL=qwen3.5-35b
LLM_API_KEY=
LLM_TEMPERATURE=0.2
```

Linux Docker 使用 `docker-compose.yml` 內建的 `extra_hosts`，container 可以用 `host.docker.internal` 連到宿主機服務。若你的 Docker 版本太舊不支援 `host-gateway`，可改用宿主機 LAN IP。

`LLM_BASE_URL` 不要包含 `/health`，因為服務會自動呼叫 `{LLM_BASE_URL}/chat/completions`。

## 4. Manual Container Workflow

如果你會自己建立 container，然後進 container 裡面執行指令，可以用這個流程。

在 server 的專案根目錄建立 container：

```bash
docker run -it \
  --name ai-agent-service-dev \
  -p 8020:8020 \
  --add-host=host.docker.internal:host-gateway \
  -v "$PWD:/workspace/ai-agent-service" \
  -w /workspace/ai-agent-service \
  python:3.11-slim \
  bash
```

進 container 後安裝基本工具：

```bash
apt-get update
apt-get install -y git curl
```

建立環境檔：

```bash
cp .env.server.example .env
```

如果模型 gateway 跑在 server 主機的 `8080`，container 內建議使用：

```env
LLM_BASE_URL=http://host.docker.internal:8080/api/v1
```

啟動服務：

```bash
./scripts/run-in-container.sh
```

這個 script 會在 container 內安裝 Python package、載入 `.env`，並啟動 `uvicorn` 監聽 `0.0.0.0:8020`。

從 server 主機另一個 terminal 測試：

```bash
curl http://127.0.0.1:8020/health
```

更完整的 manual container 步驟請看：[`docs/server-deployment.md`](server-deployment.md)。

## 5. Docker Compose Build and Start

用 Docker Compose 啟動：

```bash
docker compose up -d --build
```

也可以使用 repo 內建 script，script 會自動以專案根目錄為基準建立 `.env` 與 `data/`：

```bash
./scripts/run-docker.sh
```

查看狀態：

```bash
docker compose ps
```

查看 logs：

```bash
docker compose logs -f ai-agent-service
```

## 6. Verify Service

健康檢查：

```bash
curl http://127.0.0.1:8020/health
```

預期：

```json
{"status":"ok"}
```

測試線上 LLM API：

```bash
curl -X POST http://127.0.0.1:8020/agent \
  -H 'Content-Type: application/json' \
  -d '{"message":"Say hello in Traditional Chinese"}'
```

如果 `.env` 有正確設定 `LLM_API_KEY`，服務會呼叫指定 OpenAI-compatible API，並把 user / assistant messages 寫入 SQLite。

查詢已儲存的對話：

```bash
curl http://127.0.0.1:8020/sessions/1/messages
```

Read-only SQL 查詢：

```bash
curl -X POST http://127.0.0.1:8020/sql/query \
  -H 'Content-Type: application/json' \
  -d '{"query":"SELECT id, session_id, role, content FROM messages ORDER BY id"}'
```

## 7. Stop / Restart / Update

停止：

```bash
docker compose down
```

重啟：

```bash
docker compose restart
```

更新程式碼並重新部署：

```bash
git pull
docker compose up -d --build
```

清理舊 image：

```bash
docker image prune -f
```

## 8. Operational Notes

### Container Port

服務在 container 內監聽 `8020`，Compose 預設會映射到宿主機 `8020`：

```env
SERVICE_HOST_PORT=8020
```

如果宿主機 8020 已被占用，可在 `.env` 改成：

```env
SERVICE_HOST_PORT=8080
```

然後用：

```bash
curl http://127.0.0.1:8080/health
```

### SQLite Persistence

Compose 會把本機 `./data` 掛到 container 內的 `/app/data`：

```yaml
volumes:
  - ./data:/app/data
```

預設 SQLite 檔案位置：

```env
DATABASE_URL=sqlite:///./data/agent.db
```

所以重啟 container 後，對話資料仍會保存在 Linux 主機的 `./data/agent.db`。

### Secrets

不要把 `.env` commit 到 GitHub。此 repo 已透過 `.gitignore` 與 `.dockerignore` 排除 `.env`。

### Healthcheck

Dockerfile 與 Compose 都包含 healthcheck，會定期呼叫：

```text
http://127.0.0.1:8020/health
```

查看健康狀態：

```bash
docker compose ps
```

### Non-root Runtime

Dockerfile 會建立 `app` 使用者，服務不是用 root 身分執行，較適合 Linux server 長期運行。

### Logs

目前 logs 直接輸出到 stdout/stderr，由 Docker 管理：

```bash
docker compose logs -f ai-agent-service
```

Production 可再接 Docker logging driver、Prometheus、OpenTelemetry 或集中式 log 系統。

## 9. Troubleshooting

### Port already allocated

錯誤類似：

```text
Bind for 0.0.0.0:8020 failed: port is already allocated
```

解法：如果是 Compose，修改 `.env`：

```env
SERVICE_HOST_PORT=8080
```

如果是 manual container，建立 container 時改成：

```bash
-p 8080:8020
```

### LLM API Unauthorized

如果 `/agent` 一般訊息回傳 401 / 403 / 500，請檢查：

```bash
docker compose logs -f ai-agent-service
```

確認 `.env`：

```env
LLM_API_KEY=your_real_key
LLM_BASE_URL=https://api.openai.com/v1
LLM_MODEL=gpt-4o-mini
```

### Container cannot reach local model server

如果模型服務跑在 Linux 宿主機，container 不能直接用 `localhost` 連宿主機。請使用：

```yaml
extra_hosts:
  - "host.docker.internal:host-gateway"
```

然後設定：

```env
LLM_BASE_URL=http://host.docker.internal:8080/api/v1
```

### Rebuild after dependency changes

如果 `pyproject.toml` 有變更，請重新 build：

```bash
docker compose build --no-cache
docker compose up -d
```

## 10. Production Checklist

- [ ] `.env` 已填入正確 API key，且沒有 commit 到 GitHub
- [ ] `docker compose ps` 顯示 service healthy
- [ ] `/health` 可以從 server 本機存取
- [ ] 防火牆只開必要 port
- [ ] 若對外提供服務，前面加 reverse proxy，例如 Nginx / Caddy / Traefik
- [ ] 設定 HTTPS
- [ ] 設定 log rotation 或集中式 logs
- [ ] 設定 restart policy，目前預設 `unless-stopped`
- [ ] 若接地端模型，確認 container 能連到模型 endpoint
