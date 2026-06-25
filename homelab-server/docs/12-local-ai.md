# 12 — Local AI (Ollama + Open WebUI)

Run large language models locally on your server. Ollama manages model
downloads and inference. Open WebUI provides a ChatGPT-style browser interface.

---

## Part A — Ollama

### 1. Install Ollama

```bash
curl -fsSL https://ollama.com/install.sh | sh
```

This installs Ollama as a systemd service and starts it automatically.

### 2. Verify Installation

```bash
sudo systemctl status ollama
ollama --version
```

### 3. Pull a Model

```bash
# Pull Llama 3.2 (3B — fast, runs well on CPU)
ollama pull llama3.2

# Or the larger 8B version
ollama pull llama3.2:8b

# List downloaded models
ollama list
```

Model files are stored in `/usr/share/ollama/.ollama/models/`

### 4. Test Ollama in the Terminal

```bash
ollama run llama3.2
# Type a prompt and press Enter. Ctrl+D or /bye to exit.
```

### 5. Expose Ollama to Docker Containers

By default, Ollama only listens on `127.0.0.1:11434` (localhost only).
For Open WebUI (Docker) to reach it, Ollama needs to listen on all interfaces.

```bash
sudo systemctl edit ollama
```

In the editor that opens, add:

```ini
[Service]
Environment="OLLAMA_HOST=0.0.0.0"
```

Save and restart:

```bash
sudo systemctl daemon-reload
sudo systemctl restart ollama
```

Verify it's listening on all interfaces:
```bash
ss -tlnp | grep 11434
# Should show 0.0.0.0:11434
```

---

## Part B — Open WebUI

Open WebUI connects to Ollama and provides a full chat interface in the browser.

### 1. Create docker-compose.yml

```bash
mkdir -p ~/openwebui
nano ~/openwebui/docker-compose.yml
```

```yaml
services:
  open-webui:
    image: ghcr.io/open-webui/open-webui:main
    container_name: open-webui
    environment:
      # Ollama runs on the host, so use the Docker bridge gateway
      - OLLAMA_BASE_URL=http://172.17.0.1:11434
    volumes:
      - open-webui-data:/app/backend/data
    ports:
      - "3001:8080"
    restart: unless-stopped
    extra_hosts:
      - "host.docker.internal:host-gateway"

volumes:
  open-webui-data:
```

> The `OLLAMA_BASE_URL` uses `172.17.0.1` — the Docker bridge gateway —
> because Ollama runs on the host, not in a container.
> `localhost` from inside the Open WebUI container points to itself.

### 2. Start Open WebUI

```bash
cd ~/openwebui
docker compose up -d
```

### 3. Open the Firewall Port

```bash
sudo ufw allow 3001/tcp comment 'Open WebUI'
```

### 4. First Login

Go to `http://<server-ip>:3001`

Create your admin account on first visit.

Open WebUI will automatically detect models available in Ollama.

### 5. Start Chatting

Select a model from the top dropdown and start a conversation.
The first response may be slow as the model loads into memory.

---

## Managing Models

```bash
# List all downloaded models
ollama list

# Pull a new model
ollama pull mistral
ollama pull codellama
ollama pull phi3

# Remove a model (frees disk space)
ollama rm llama3.2

# Show model details
ollama show llama3.2

# Run a quick one-shot prompt (no interactive mode)
ollama run llama3.2 "Explain Docker networking in two sentences"
```

---

## Updating

```bash
# Update Ollama
curl -fsSL https://ollama.com/install.sh | sh

# Update Open WebUI
cd ~/openwebui
docker compose pull
docker compose up -d
```

---

## Performance Notes

- **CPU only:** Most models run on CPU. Responses will be slow (10–60s/response)
  depending on model size and your CPU. The 3B models are most practical on CPU.
- **GPU acceleration:** If your server has an NVIDIA GPU, install the NVIDIA
  Container Toolkit and Ollama will automatically use it for much faster inference.
- **RAM:** Models are loaded into RAM. 3B models need ~3–4GB, 8B models need ~6–8GB.
  Ensure your server has enough free RAM.

```bash
# Monitor RAM and CPU usage while Ollama runs
htop
# or
watch -n1 free -h
```
