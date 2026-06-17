# Troubleshooting: `LLM_BASE_URL` 設定後 `/agent` 出現 404 / Server Error

這份文件整理當 AI Agent Service 設定本機或內網 OpenAI-compatible LLM gateway 後，呼叫 `/agent` 卻出現 server error 404 時的檢查流程。

## 1. 先理解 AI Agent Service 實際會呼叫哪個 URL

目前 AI Agent Service 的 OpenAI-compatible provider 會使用：

```text
{LLM_BASE_URL}/chat/completions
```

例如你的 `.env` 如果是：

```env
LLM_BASE_URL=http://localhost:8080/api/v1
```

那 AI Agent Service 實際會呼叫：

```text
http://localhost:8080/api/v1/chat/completions
```

所以如果 `/agent` 回 server error 404，通常代表：

```text
localhost:8080 有服務回應，但該服務沒有 /api/v1/chat/completions 這個 endpoint。
```

這通常不是 AI Agent Service 的 `/health` 壞掉，而是 LLM gateway 的 OpenAI-compatible API 路徑不一致。

---

## 2. 最常見原因

### 原因 A：LLM gateway 的 API root 其實是 `/v1`

很多 OpenAI-compatible server 使用：

```env
LLM_BASE_URL=http://localhost:8080/v1
```

而不是：

```env
LLM_BASE_URL=http://localhost:8080/api/v1
```

如果是這種情況，正確 chat endpoint 會是：

```text
http://localhost:8080/v1/chat/completions
```

### 原因 B：AI Agent Service 在 Docker 裡，模型 gateway 在主機上

如果 AI Agent Service 跑在 Docker container 裡：

```env
LLM_BASE_URL=http://localhost:8080/api/v1
```

這裡的 `localhost` 指的是 **container 自己**，不是 server 主機。

若模型 gateway 跑在 server 主機上，通常要改成：

```env
LLM_BASE_URL=http://host.docker.internal:8080/api/v1
```

或如果 gateway 實際 API root 是 `/v1`：

```env
LLM_BASE_URL=http://host.docker.internal:8080/v1
```

### 原因 C：把 health URL 當成 `LLM_BASE_URL`

不要這樣設定：

```env
LLM_BASE_URL=http://localhost:8080/api/v1/health
```

因為 AI Agent Service 會再接上 `/chat/completions`，最後變成錯誤 URL：

```text
http://localhost:8080/api/v1/health/chat/completions
```

---

## 3. 請在 AI Agent Service 所在環境測試

如果 AI Agent Service 是跑在 container 裡，請先進 container：

```bash
docker exec -it ai-agent-service-dev bash
```

進入專案：

```bash
cd /workspace/ai-agent-service
```

如果 AI Agent Service 是直接跑在主機上，就直接在主機 terminal 測。

---

## 4. 檢查 gateway 的 health / models endpoint

先測目前你設定的 `/api/v1`：

```bash
curl -i http://localhost:8080/api/v1/health
curl -i http://localhost:8080/api/v1/models
```

再測常見的 `/v1`：

```bash
curl -i http://localhost:8080/v1/models
```

如果 AI Agent Service 在 Docker 裡，但模型 gateway 在主機上，請改測：

```bash
curl -i http://host.docker.internal:8080/api/v1/health
curl -i http://host.docker.internal:8080/api/v1/models
curl -i http://host.docker.internal:8080/v1/models
```

---

## 5. 直接測 chat completions endpoint

### 測 `/api/v1/chat/completions`

```bash
curl -i -X POST http://localhost:8080/api/v1/chat/completions \
  -H 'Content-Type: application/json' \
  -d '{
    "model": "qwen3.5-35b",
    "messages": [
      {"role": "user", "content": "ping"}
    ],
    "temperature": 0.2
  }'
```

### 如果上面 404，改測 `/v1/chat/completions`

```bash
curl -i -X POST http://localhost:8080/v1/chat/completions \
  -H 'Content-Type: application/json' \
  -d '{
    "model": "qwen3.5-35b",
    "messages": [
      {"role": "user", "content": "ping"}
    ],
    "temperature": 0.2
  }'
```

### Docker container 連 host gateway 的版本

如果 AI Agent Service 在 Docker 裡，模型 gateway 在主機上，請測：

```bash
curl -i -X POST http://host.docker.internal:8080/api/v1/chat/completions \
  -H 'Content-Type: application/json' \
  -d '{
    "model": "qwen3.5-35b",
    "messages": [
      {"role": "user", "content": "ping"}
    ],
    "temperature": 0.2
  }'
```

如果 404，再測：

```bash
curl -i -X POST http://host.docker.internal:8080/v1/chat/completions \
  -H 'Content-Type: application/json' \
  -d '{
    "model": "qwen3.5-35b",
    "messages": [
      {"role": "user", "content": "ping"}
    ],
    "temperature": 0.2
  }'
```

---

## 6. 根據測試結果設定 `.env`

### 如果 `http://localhost:8080/api/v1/chat/completions` 成功

設定：

```env
AI_PROVIDER=openai-compatible
LLM_BASE_URL=http://localhost:8080/api/v1
LLM_MODEL=qwen3.5-35b
LLM_API_KEY=
LLM_TEMPERATURE=0.2
```

### 如果 `http://localhost:8080/v1/chat/completions` 成功

設定：

```env
AI_PROVIDER=openai-compatible
LLM_BASE_URL=http://localhost:8080/v1
LLM_MODEL=qwen3.5-35b
LLM_API_KEY=
LLM_TEMPERATURE=0.2
```

### 如果 AI Agent Service 在 Docker 裡，且 `host.docker.internal:8080/api/v1/chat/completions` 成功

設定：

```env
AI_PROVIDER=openai-compatible
LLM_BASE_URL=http://host.docker.internal:8080/api/v1
LLM_MODEL=qwen3.5-35b
LLM_API_KEY=
LLM_TEMPERATURE=0.2
```

### 如果 AI Agent Service 在 Docker 裡，且 `host.docker.internal:8080/v1/chat/completions` 成功

設定：

```env
AI_PROVIDER=openai-compatible
LLM_BASE_URL=http://host.docker.internal:8080/v1
LLM_MODEL=qwen3.5-35b
LLM_API_KEY=
LLM_TEMPERATURE=0.2
```

---

## 7. 修改 `.env` 前先備份

```bash
cp .env ".env.bak.$(date +%Y%m%d-%H%M%S)"
```

編輯 `.env`：

```bash
nano .env
```

或用 `sed` 替換，例如把 `/api/v1` 改成 `/v1`：

```bash
sed -i.bak 's#^LLM_BASE_URL=.*#LLM_BASE_URL=http://localhost:8080/v1#' .env
```

Docker 連 host 的版本：

```bash
sed -i.bak 's#^LLM_BASE_URL=.*#LLM_BASE_URL=http://host.docker.internal:8080/v1#' .env
```

---

## 8. 重啟 AI Agent Service

如果是用 manual container workflow：

```bash
bash scripts/run-in-container.sh
```

如果服務已經在前景執行，先 `Ctrl+C` 停掉，再重新執行上面指令。

如果是 native local run：

```bash
bash scripts/run-local.sh
```

---

## 9. 測 AI Agent Service

先測 service health：

```bash
curl -i http://127.0.0.1:8020/health
```

再測 `/agent`：

```bash
curl -i -X POST http://127.0.0.1:8020/agent \
  -H 'Content-Type: application/json' \
  -d '{"message":"請用繁體中文簡短回答：模型連線測試"}'
```

如果成功，會看到類似：

```json
{
  "reply": "模型連線測試成功。",
  "model": "qwen3.5-35b",
  "session_id": 1
}
```

實際 `reply` 內容會依模型而不同。

---

## 10. 快速判斷表

| 測試結果 | 代表什麼 | 建議 |
|---|---|---|
| `/api/v1/health` OK，但 `/api/v1/chat/completions` 404 | health endpoint 存在，但 chat endpoint 不在 `/api/v1` | 試 `/v1/chat/completions` |
| `/v1/chat/completions` OK | base URL 應該是 `/v1` | 設 `LLM_BASE_URL=http://localhost:8080/v1` |
| container 裡 `localhost:8080` 連到奇怪服務或 404 | `localhost` 指 container 內，不是 host | 改用 `host.docker.internal` |
| host 上能通，container 裡不能通 | Docker network 問題 | 用 `--add-host=host.docker.internal:host-gateway` 或同一 Docker network |
| `/chat/completions` 全部 404 | gateway 可能不是 OpenAI-compatible chat completions API | 確認 gateway 文件或實際 endpoint |

---

## 11. 如果仍然失敗，請收集這些資訊

請把以下指令輸出貼給維護者：

```bash
pwd
python3 --version || python --version
curl -i http://127.0.0.1:8020/health
curl -i http://localhost:8080/api/v1/health
curl -i http://localhost:8080/api/v1/models
curl -i http://localhost:8080/v1/models
```

如果在 Docker container 裡，也請加測：

```bash
curl -i http://host.docker.internal:8080/api/v1/health
curl -i http://host.docker.internal:8080/api/v1/models
curl -i http://host.docker.internal:8080/v1/models
```

以及目前 `.env` 中的非機密設定：

```bash
grep -E '^(AI_PROVIDER|LLM_BASE_URL|LLM_MODEL|LLM_TEMPERATURE|DATABASE_URL)=' .env
```

不要貼 API key、密碼或其他 secrets。
