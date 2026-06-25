# 03 — Media Stack Deployment

Deploy all media automation services using Docker Compose.

---

## 1. Create the Directory Structure

```bash
mkdir -p ~/mediastack/config
cd ~/mediastack
```

---

## 2. Copy and Configure the .env File

```bash
cp .env.example .env
nano .env
```

Set your timezone and verify PUID/PGID match your user (`id $USER`).

---

## 3. Start All Services

```bash
cd ~/mediastack
docker compose up -d
```

First run will pull all images — this may take a few minutes.

---

## 4. Verify All Containers Are Running

```bash
docker compose ps
```

All services should show `Up` status. If any show `Exit` or `Restarting`,
check logs:

```bash
docker compose logs <service-name>
# e.g.:
docker compose logs jellyseerr
docker compose logs radarr
```

---

## 5. Access the Web UIs

| Service | URL |
|---|---|
| Prowlarr | http://\<server-ip\>:9696 |
| Radarr | http://\<server-ip\>:7878 |
| Sonarr | http://\<server-ip\>:8989 |
| qBittorrent | http://\<server-ip\>:8080 |
| Jellyseerr | http://\<server-ip\>:5055 |
| Bazarr | http://\<server-ip\>:6767 |
| Portainer | https://\<server-ip\>:9443 |

---

## 6. Open Required Firewall Ports

```bash
sudo ufw allow 9696/tcp comment 'Prowlarr'
sudo ufw allow 7878/tcp comment 'Radarr'
sudo ufw allow 8989/tcp comment 'Sonarr'
sudo ufw allow 8080/tcp comment 'qBittorrent'
sudo ufw allow 5055/tcp comment 'Jellyseerr'
sudo ufw allow 6767/tcp comment 'Bazarr'
sudo ufw allow 9443/tcp comment 'Portainer'
sudo ufw allow 6881/tcp comment 'qBittorrent peer'
sudo ufw allow 6881/udp comment 'qBittorrent peer'
```

---

## 7. Updating Services

```bash
cd ~/mediastack
docker compose pull
docker compose up -d
```

---

## Common Commands

```bash
# Stop all services
docker compose down

# Restart a single service
docker compose restart radarr

# View live logs
docker compose logs -f sonarr

# Run a command inside a container
docker compose exec radarr bash
```

---

## ⚠️ Important: Config Directory Is Root-Owned

Docker creates `./config/` subdirectories as root. Always use `sudo` for
any file operations inside them:

```bash
sudo ls ~/mediastack/config/radarr/
sudo cat ~/mediastack/config/sonarr/config.xml
```

---

## Next Step

→ [Configure Radarr, Sonarr, Prowlarr, and qBittorrent](04-arr-configuration.md)
