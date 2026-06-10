# Server Deployment from GitHub

這份文件適合你把 GitHub 上的整個 `ai-agent-service` 資料夾下載到 server 後執行，尤其是你會自己建立 Docker container，然後進 container 裡面跑指令的情境。

設計原則：

- 不綁定任何個人電腦絕對路徑。
- 所有路徑都以專案根目錄為基準。
- `.env` 不上傳 GitHub，server 端自行複製範例檔產生。
- SQLite 預設保存在專案底下的 `./data/agent.db`。
- 如果用 container，建議把專案資料夾掛到 container 裡，讓 `.env` 與 `data/` 可以留在 server 主機上。

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

你可以依照自己的 server 習慣選一種方式：

- **Manual Docker container:** 如果你會自己建立 container，然後進 container 執行指令，請看第 4 節。這是目前建議給你的方式。
- **Docker Compose:** 如果你想讓 repo 的 compose 檔幫你建立 container，請看第 5 節。
- **Native Python:** 如果你想直接在主機上跑，不透過 container，請看第 6 節。

## 3. Environment File

如果你要接本機地端模型 `qwen3.5-35b`，可以直接複製 server 範例：

```bash
cp .env.server.example .env
```

`.env.server.example` 預設給 Docker container 使用：

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

## 4. Manual Docker Container Run

這一節適合你自己建立 container，然後進 container 裡執行安裝與啟動指令。

### 4.1 建立 container 時要注意的參數

假設你的模型 gateway 跑在 server 主機的 `8080`，AI Agent Service 跑在你自己建立的 container 裡，建議建立 container 時加上：

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

參數說明：

- `-p 8020:8020`：把 container 裡的服務 port 8020 映射到 server 主機的 8020。
- `--add-host=host.docker.internal:host-gateway`：讓 container 可以用 `host.docker.internal` 連回 server 主機上的模型 gateway。
- `-v "$PWD:/workspace/ai-agent-service"`：把目前專案資料夾掛進 container，方便你在 server 上更新檔案後 container 直接看到。
- `-w /workspace/ai-agent-service`：進 container 後直接在專案目錄。

如果你的 Docker 版本不支援 `host-gateway`，可以改用 server 的 LAN IP，例如：

```env
LLM_BASE_URL=http://192.168.1.10:8080/api/v1
```

如果你刻意使用 host network：

```bash
docker run -it \
  --name ai-agent-service-dev \
  --network host \
  -v "$PWD:/workspace/ai-agent-service" \
  -w /workspace/ai-agent-service \
  python:3.11-slim \
  bash
```

那 `LLM_BASE_URL` 可以用：

```env
LLM_BASE_URL=http://localhost:8080/api/v1
```

因為 container 會和宿主機共用 network namespace。不過 host network 在不同環境限制較多，預設仍建議用 `--add-host`。

### 4.2 在 container 裡安裝基本工具

如果你用 `python:3.11-slim`，進 container 後先安裝常用工具：

```bash
apt-get update
apt-get install -y git curl
```

如果你已經把 repo 掛進 container，確認檔案存在：

```bash
pwd
ls
```

如果你沒有掛 volume，而是想在 container 裡 clone：

```bash
git clone https://github.com/Allen-hsu1116/ai-agent-service.git
cd ai-agent-service
```

### 4.3 建立 `.env`

在 container 的專案根目錄執行：

```bash
cp .env.server.example .env
```

如果模型 gateway 跑在 server 主機，且 container 是用 `--add-host=host.docker.internal:host-gateway` 建立，保留：

```env
LLM_BASE_URL=http://host.docker.internal:8080/api/v1
```

如果 container 是用 `--network host` 建立，改成：

```env
LLM_BASE_URL=http://localhost:8080/api/v1
```

不要把 `/health` 放進 `LLM_BASE_URL`。

### 4.4 在 container 裡啟動服務

最簡單使用內建 script：

```bash
./scripts/run-in-container.sh
```

這個 script 會：

1. 自動切到專案根目錄。
2. 如果沒有 `.env`，從 `.env.server.example` 建立。
3. 建立 `data/`。
4. 在 container 的 Python 環境安裝套件。
5. 載入 `.env`。
6. 啟動 `uvicorn`，監聽 `0.0.0.0:8020`。

如果你想手動執行，等同於：

```bash
mkdir -p data
python -m pip install --upgrade pip
python -m pip install -e .
set -a
source .env
set +a
python -m uvicorn ai_agent_service.main:app --host 0.0.0.0 --port 8020
```

### 4.5 從另一個 terminal 測試

服務啟動後，在 server 主機另一個 terminal 測：

```bash
curl http://127.0.0.1:8020/health
```

確認模型 gateway：

```bash
curl http://127.0.0.1:8080/api/v1/health
```

測試 agent：

```bash
curl -X POST http://127.0.0.1:8020/agent \
  -H 'Content-Type: application/json' \
  -d '{"message":"請用繁體中文簡短回答：模型連線測試"}'
```

### 4.6 停止與重新進入 container

如果服務在前景執行，按 `Ctrl+C` 停止。

離開 container：

```bash
exit
```

重新進入既有 container：

```bash
docker start ai-agent-service-dev
docker exec -it ai-agent-service-dev bash
cd /workspace/ai-agent-service
./scripts/run-in-container.sh
```

### 4.7 長期背景執行方式

如果你要讓服務在 container 裡背景常駐，可以用 `nohup` 或 `tmux`。例如：

```bash
nohup ./scripts/run-in-container.sh > app.log 2>&1 &
```

查看 log：

```bash
tail -f app.log
```

如果你偏好由 Docker 管理前景 process，則可以建立 container 時直接把啟動指令放在最後：

```bash
docker run -d \
  --name ai-agent-service \
  -p 8020:8020 \
  --add-host=host.docker.internal:host-gateway \
  -v "$PWD:/workspace/ai-agent-service" \
  -w /workspace/ai-agent-service \
  python:3.11-slim \
  bash -lc "apt-get update && apt-get install -y git curl && ./scripts/run-in-container.sh"
```

查看 log：

```bash
docker logs -f ai-agent-service
```

## 5. Docker Compose Run

如果之後你想改用 repo 內建 compose：

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

## 6. Native Python Run

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

## 7. Data Path

預設 SQLite：

```env
DATABASE_URL=sqlite:///./data/agent.db
```

這是相對路徑，意思是：

```text
<project-root>/data/agent.db
```

如果你用第 4 節的 manual container 並掛載：

```text
-v "$PWD:/workspace/ai-agent-service"
```

那 `data/agent.db` 會保存在 server 主機的專案資料夾裡，不會只留在 container 內部。

Docker Compose 預設：

```env
DATA_DIR=./data
```

並掛載：

```text
./data:/app/data
```

所以你更新 image 或重啟 container 時，資料仍會保存在 server 的專案資料夾裡。

## 8. Updating from GitHub

如果是 Git clone，而且 repo 是掛進你自己建立的 container：

```bash
git pull
docker exec -it ai-agent-service-dev bash
cd /workspace/ai-agent-service
./scripts/run-in-container.sh
```

如果是 Git clone，而且使用 Docker Compose：

```bash
git pull
docker compose up -d --build
```

如果是下載 ZIP，請保留 server 上的 `.env` 和 `data/`，用新版程式檔覆蓋其他檔案後再重啟。

## 9. Common Troubleshooting

### Model health check can pass, but `/agent` fails

確認 `LLM_BASE_URL` 沒有包含 `/health`，且模型服務有提供 OpenAI-compatible：

```text
POST /chat/completions
```

### Container cannot reach model server

如果 AI Agent Service 跑在 container 裡，`localhost` 通常是 container 自己，不是 server 主機。請優先確認 `.env` 使用：

```env
LLM_BASE_URL=http://host.docker.internal:8080/api/v1
```

而且建立 container 時有加：

```bash
--add-host=host.docker.internal:host-gateway
```

如果 server Docker 版本太舊不支援 `host-gateway`，改用 server 的 LAN IP，例如：

```env
LLM_BASE_URL=http://192.168.1.10:8080/api/v1
```

### Port 8020 is occupied

如果是 manual container，建立 container 時改 port mapping：

```bash
-p 8021:8020
```

然後：

```bash
curl http://127.0.0.1:8021/health
```

如果是 Docker Compose，改 `.env`：

```env
SERVICE_HOST_PORT=8021
```

然後：

```bash
docker compose up -d
curl http://127.0.0.1:8021/health
```
