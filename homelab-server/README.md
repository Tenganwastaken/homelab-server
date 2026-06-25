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
