# Server Deployment from GitHub

這份文件適合你把 GitHub 上的整個 `ai-agent-service` 資料夾下載到 server 後直接執行。

設計原則：

- 不綁定任何個人電腦絕對路徑。
- 所有路徑都以專案根目錄為基準。
- `.env` 不上傳 GitHub，server 端自行複製範例檔產生。
- SQLite 預設保存在專案底下的 `./data/agent.db`。
- Docker 模式會把 server 上的 `./data` 掛到 container 內的 `/app/data`。

## 1. Download the Project

用 Git clone：

```bash
git clone https://github.com/Allen-hsu1116/ai-agent-service.git
cd ai-agent-service
```

或從 GitHub 下載 ZIP 後解壓縮，進入資料夾：

```bash
cd ai-agent-service
```

後續指令都假設你人在專案根目錄。

## 2. Choose How to Run

建議 server 用 Docker Compose，比較不受 Python 路徑與套件環境影響。

- **Docker Compose:** 推薦 production/server 使用。
- **Native Python:** 適合你想直接在主機上跑，不透過 container。

## 3. Environment File

如果你要接本機地端模型 `qwen3.5-35b`，可以直接複製 server 範例：

```bash
cp .env.server.example .env
```

`.env.server.example` 預設給 Docker Compose 使用：

```env
AI_PROVIDER=openai-compatible
LLM_BASE_URL=http://host.docker.internal:8080/api/v1
LLM_MODEL=qwen3.5-35b
LLM_API_KEY=
LLM_TEMPERATURE=0.2
DATABASE_URL=sqlite:///./data/agent.db
SERVICE_HOST_PORT=8020
DATA_DIR=./data
```

### Important: native vs Docker model URL

如果 AI Agent Service 和模型 gateway 都直接跑在同一台 server 主機上，使用：

```env
LLM_BASE_URL=http://localhost:8080/api/v1
```

如果 AI Agent Service 跑在 Docker container 裡，而模型 gateway 跑在 server 主機上，使用：

```env
LLM_BASE_URL=http://host.docker.internal:8080/api/v1
```

不要把 health-check path 放進 `LLM_BASE_URL`。正確是：

```env
LLM_BASE_URL=http://host.docker.internal:8080/api/v1
```

不是：

```env
LLM_BASE_URL=http://host.docker.internal:8080/api/v1/health
```

因為服務會自動呼叫：

```text
{LLM_BASE_URL}/chat/completions
```

## 4. Docker Compose Run

最簡單：

```bash
./scripts/run-docker.sh
```

或手動：

```bash
cp .env.server.example .env
mkdir -p data
docker compose up -d --build
```

查看狀態：

```bash
docker compose ps
```

查看 logs：

```bash
docker compose logs -f ai-agent-service
```

健康檢查：

```bash
curl http://127.0.0.1:8020/health
```

測試 agent：

```bash
curl -X POST http://127.0.0.1:8020/agent \
  -H 'Content-Type: application/json' \
  -d '{"message":"請用繁體中文簡短回答：模型連線測試"}'
```

## 5. Native Python Run

如果不用 Docker：

```bash
cp .env.server.example .env
```

然後把 `.env` 裡的 `LLM_BASE_URL` 改成：

```env
LLM_BASE_URL=http://localhost:8080/api/v1
```

啟動：

```bash
./scripts/run-local.sh
```

這個 script 會：

1. 自動切到專案根目錄。
2. 建立 `.venv`。
3. 安裝套件。
4. 載入 `.env`。
5. 啟動 `uvicorn`。

預設監聽：

```text
0.0.0.0:8020
```

如果要改 host / port：

```env
APP_HOST=0.0.0.0
APP_PORT=8020
```

## 6. Data Path

預設 SQLite：

```env
DATABASE_URL=sqlite:///./data/agent.db
```

這是相對路徑，意思是：

```text
<project-root>/data/agent.db
```

Docker Compose 預設：

```env
DATA_DIR=./data
```

並掛載：

```text
./data:/app/data
```

所以你更新 image 或重啟 container 時，資料仍保存在 server 的專案資料夾裡。

## 7. Updating from GitHub

如果是 Git clone：

```bash
git pull
docker compose up -d --build
```

如果是下載 ZIP，請保留 server 上的 `.env` 和 `data/`，用新版程式檔覆蓋其他檔案後再重啟。

## 8. Common Troubleshooting

### Model health check can pass, but `/agent` fails

確認 `LLM_BASE_URL` 沒有包含 `/health`，且模型服務有提供 OpenAI-compatible：

```text
POST /chat/completions
```

### Docker cannot reach model server

確認 `.env` 使用：

```env
LLM_BASE_URL=http://host.docker.internal:8080/api/v1
```

如果 server Docker 版本太舊不支援 `host-gateway`，改用 server 的 LAN IP，例如：

```env
LLM_BASE_URL=http://192.168.1.10:8080/api/v1
```

### Port 8020 is occupied

改 `.env`：

```env
SERVICE_HOST_PORT=8021
```

然後：

```bash
docker compose up -d
curl http://127.0.0.1:8021/health
```
