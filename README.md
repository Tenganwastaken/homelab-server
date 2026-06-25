# 🏠 Homelab Server

A fully self-hosted home server running 24/7 on Ubuntu 24.04. Hosts a complete media automation stack, Discord bots, photo management, local AI, and monitoring — all managed via Docker Compose and systemd.

---

## 📦 Services Overview

| Service | Purpose | Port | Stack |
|---|---|---|---|
| Jellyfin | Media server | 8096 | systemd |
| Jellyseerr | Media request frontend | 5055 | Docker |
| Radarr | Movie automation | 7878 | Docker |
| Sonarr | TV show automation | 8989 | Docker |
| Prowlarr | Indexer manager | 9696 | Docker |
| qBittorrent | Download client | 8080 | Docker |
| Bazarr | Subtitle management | 6767 | Docker |
| Immich | Photo management | 2283 | Docker |
| Beszel Hub | Server monitoring | 8090 | Docker |
| Prometheus | Metrics collection | 9090 | Docker |
| Grafana | Metrics dashboards | 3000 | Docker |
| Open WebUI | Local AI chat (Ollama) | 3001 | Docker |
| Homepage | Server dashboard | 3002 | Docker |
| Portainer | Docker management | 9443 | Docker |
| Cockpit | System management | 9090 | systemd |
| Discord Bot | Server automation | — | systemd |
| SkinPeek | Valorant skin checker | — | systemd |
| Bot Control API | Bot management REST API | 9999 | systemd |

---

## 🗂️ Repository Structure

```
homelab-server/
├── mediastack/
│   ├── docker-compose.yml      # Radarr, Sonarr, Prowlarr, qBittorrent, Jellyseerr, Bazarr
│   └── .env.example
├── monitoring/
│   ├── docker-compose.yml      # Beszel, Prometheus, Node Exporter, Grafana
│   └── prometheus/
│       └── prometheus.yml
├── immich/
│   ├── docker-compose.yml      # Immich + PostgreSQL + Redis
│   └── .env.example
├── homepage/
│   └── config/
│       └── services.yaml       # Dashboard service definitions
├── bots/
│   ├── discord-bot/
│   │   ├── bot.py              # Main Discord bot (Python)
│   │   ├── requirements.txt
│   │   └── .env.example
│   └── bot-control/
│       ├── app.py              # Flask REST API for bot management
│       └── requirements.txt
├── systemd/
│   ├── discordbot.service
│   ├── skinpeek.service
│   └── bot-control.service
└── docs/
    ├── 01-server-setup.md
    ├── 02-storage-setup.md
    ├── 03-media-stack.md
    ├── 04-arr-configuration.md
    ├── 05-jellyfin-setup.md
    ├── 06-jellyseerr-bazarr.md
    ├── 07-discord-bots.md
    ├── 08-immich-photos.md
    ├── 09-monitoring.md
    ├── 10-homepage-dashboard.md
    ├── 11-remote-access.md
    ├── 12-local-ai.md
    └── TROUBLESHOOTING.md
```

---

## ⚡ Quick Start

Follow the documentation in order:

1. [Server Setup](docs/01-server-setup.md) — Ubuntu, Docker, SSH
2. [Storage Setup](docs/02-storage-setup.md) — Mount media drive, directory structure
3. [Media Stack](docs/03-media-stack.md) — Deploy all *arr services
4. [*Arr Configuration](docs/04-arr-configuration.md) — Connect and configure Radarr/Sonarr/Prowlarr/qBittorrent
5. [Jellyfin Setup](docs/05-jellyfin-setup.md) — Install media server
6. [Jellyseerr & Bazarr](docs/06-jellyseerr-bazarr.md) — Request frontend and subtitles
7. [Discord Bots](docs/07-discord-bots.md) — Deploy bots and bot control API
8. [Immich Photos](docs/08-immich-photos.md) — Self-hosted photo library
9. [Monitoring](docs/09-monitoring.md) — Beszel, Prometheus, Grafana
10. [Homepage Dashboard](docs/10-homepage-dashboard.md) — Central service dashboard
11. [Remote Access](docs/11-remote-access.md) — Tailscale VPN + NoMachine
12. [Local AI](docs/12-local-ai.md) — Ollama + Open WebUI

---

## ⚠️ Critical Networking Note

> **Docker containers on this stack cannot use `localhost` to reach the host or other containers' exposed ports.**
> Always use `172.17.0.1` (Docker bridge gateway) when a container needs to reach the host or another container via its host port.

This affects: Bazarr → Radarr/Sonarr, Jellyseerr → Jellyfin, Beszel Hub → Agent.

---

## 🔧 Prerequisites

- Ubuntu 24.04 LTS (server or desktop)
- Docker + Docker Compose v2
- A dedicated HDD/SSD for media storage (recommended: 2TB+)
- Basic Linux terminal familiarity

---

## 🖥️ Essential Commands

### Docker Compose — Media Stack

```bash
# Start all media services
cd ~/mediastack && docker compose up -d

# Stop all media services
cd ~/mediastack && docker compose down

# Restart a single service
docker compose -f ~/mediastack/docker-compose.yml restart radarr

# Pull latest images and redeploy
cd ~/mediastack && docker compose pull && docker compose up -d

# View live logs for a service
docker compose -f ~/mediastack/docker-compose.yml logs -f sonarr

# View logs for all media services
docker compose -f ~/mediastack/docker-compose.yml logs -f

# Check status of all media containers
docker compose -f ~/mediastack/docker-compose.yml ps
```

### Docker Compose — Monitoring

```bash
cd ~/monitoring && docker compose up -d
cd ~/monitoring && docker compose down
docker compose -f ~/monitoring/docker-compose.yml logs -f beszel-hub
docker compose -f ~/monitoring/docker-compose.yml ps
```

### Docker Compose — Immich

```bash
cd ~/immich && docker compose up -d
cd ~/immich && docker compose down
docker compose -f ~/immich/docker-compose.yml logs -f immich-server
```

### Docker — General

```bash
# List all running containers across all stacks
docker ps

# List all containers including stopped ones
docker ps -a

# Check resource usage (CPU, RAM, network) per container
docker stats

# Remove unused images to free disk space
docker image prune -a

# Remove stopped containers, unused networks, dangling images
docker system prune

# Execute a shell inside a running container
docker exec -it radarr bash
docker exec -it jellyseerr sh   # some containers use sh, not bash
```

### Systemd — Bots & Services

```bash
# Check status of all bots at once
systemctl status discordbot skinpeek bot-control

# Start / stop / restart a bot
sudo systemctl start discordbot
sudo systemctl stop discordbot
sudo systemctl restart discordbot

# Enable / disable auto-start on boot
sudo systemctl enable discordbot
sudo systemctl disable discordbot

# View live logs for a bot
sudo journalctl -u discordbot -f

# View last 100 lines of logs
sudo journalctl -u discordbot -n 100

# Jellyfin (runs as systemd service)
sudo systemctl restart jellyfin
sudo systemctl status jellyfin
sudo journalctl -u jellyfin -f
```

### Storage & Disk

```bash
# Check disk usage on all mounted drives
df -h

# Check media drive specifically
df -h /mnt/media

# Check size of each media directory
du -sh /mnt/media/movies
du -sh /mnt/media/tv
du -sh /mnt/media/downloads
du -sh /mnt/media/immich

# Check total media drive usage at a glance
du -sh /mnt/media/*

# Find large files (over 4GB) in downloads
find /mnt/media/downloads -size +4G -type f

# Check if media drive is mounted
mountpoint /mnt/media

# Remount all fstab entries (if drive isn't mounted after boot)
sudo mount -a
```

### Network & Firewall

```bash
# View all open firewall rules
sudo ufw status verbose

# Allow a new port
sudo ufw allow 8096/tcp comment 'Jellyfin'

# Check what's listening on a specific port
sudo ss -tlnp | grep :8096

# Check all listening ports
sudo ss -tlnp

# Test if a port is reachable from inside a container
docker exec jellyseerr wget -qO- http://172.17.0.1:8096/health
```

### System Health

```bash
# CPU, RAM, processes — interactive
htop

# RAM usage summary
free -h

# CPU temperature (if sensors installed)
sensors

# System uptime and load average
uptime

# Top 10 processes by RAM usage
ps aux --sort=-%mem | head -10

# Top 10 processes by CPU usage
ps aux --sort=-%cpu | head -10

# Full system info
uname -a
```

### Updates

```bash
# Update the OS
sudo apt update && sudo apt upgrade -y

# Update Jellyfin specifically
sudo apt update && sudo apt install --only-upgrade jellyfin

# Update all Docker Compose stacks at once
for stack in ~/mediastack ~/monitoring ~/immich ~/homepage; do
  echo "Updating $stack..."
  docker compose -f $stack/docker-compose.yml pull
  docker compose -f $stack/docker-compose.yml up -d
done

# Update Ollama
curl -fsSL https://ollama.com/install.sh | sh

# Update Tailscale
sudo apt update && sudo apt install --only-upgrade tailscale
```

### Tailscale

```bash
# Check connection status and all peers
tailscale status

# Get this server's Tailscale IP
tailscale ip -4

# Reconnect after going down
sudo tailscale up

# Disconnect temporarily
sudo tailscale down
```

### Immich CLI

```bash
# Authenticate
immich login http://<server-ip>:2283 <your-email>

# Upload a folder (creates albums from subfolder names)
immich upload --recursive --album /mnt/media/photos/

# Upload without creating albums
immich upload --recursive /mnt/media/photos/

# Check server info
immich server-info
```

### Ollama (Local AI)

```bash
# List downloaded models
ollama list

# Pull a new model
ollama pull llama3.2

# Run a model interactively
ollama run llama3.2

# Remove a model (free disk space)
ollama rm llama3.2

# Check Ollama service status
sudo systemctl status ollama
```
