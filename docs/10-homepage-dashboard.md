# 10 — Homepage Dashboard

Homepage (gethomepage.dev) is a self-hosted dashboard that gives you a single
page with widgets for all your services. Config is YAML-based and hot-reloads
automatically — no container restart needed after changes.

---

## 1. Create the Directory Structure

```bash
mkdir -p ~/homepage/config
cd ~/homepage
```

---

## 2. Create docker-compose.yml

```bash
nano ~/homepage/docker-compose.yml
```

```yaml
services:
  homepage:
    image: ghcr.io/gethomepage/homepage:latest
    container_name: homepage
    ports:
      - "3002:3000"
    volumes:
      - ./config:/app/config
      - /var/run/docker.sock:/var/run/docker.sock:ro
    restart: unless-stopped
```

The Docker socket mount is optional but enables automatic Docker container
status widgets.

---

## 3. Start Homepage

```bash
cd ~/homepage
docker compose up -d
```

---

## 4. Open the Firewall Port

```bash
sudo ufw allow 3002/tcp comment 'Homepage'
```

---

## 5. Configure services.yaml

Copy `homepage/config/services.yaml` from this repo:

```bash
cp ~/homelab-server/homepage/config/services.yaml ~/homepage/config/services.yaml
```

Then edit it with your actual server IP and API keys:

```bash
nano ~/homepage/config/services.yaml
```

Replace every `<YOUR_SERVER_IP>` with your server's LAN IP (e.g., `192.168.1.100`).
Replace each `<SERVICE_API_KEY>` placeholder with the key from that service.

> Changes to `services.yaml` take effect immediately — just refresh your browser.

---

## 6. Where to Find Each API Key

| Service | Location |
|---|---|
| Radarr | Settings → General → API Key |
| Sonarr | Settings → General → API Key |
| Prowlarr | Settings → General → API Key |
| Bazarr | Settings → General → Security → API Key |
| Jellyfin | Dashboard → API Keys → (create one) |
| Jellyseerr | Settings → General → API Key |
| qBittorrent | No API key needed — uses username/password |
| Immich | Account Settings → API Keys → (create one) |

---

## 7. Configure settings.yaml (optional)

```bash
nano ~/homepage/config/settings.yaml
```

Example:
```yaml
title: Home Server
theme: dark
color: slate
headerStyle: clean
layout:
  Media:
    style: row
    columns: 4
  Monitoring:
    style: row
    columns: 3
```

---

## 8. Configure bookmarks.yaml (optional)

```bash
nano ~/homepage/config/bookmarks.yaml
```

Example:
```yaml
- Developer:
    - GitHub:
        - href: https://github.com

- Media:
    - TMDB:
        - href: https://www.themoviedb.org
    - Trakt:
        - href: https://trakt.tv
```

---

## 9. Updating Homepage

```bash
cd ~/homepage
docker compose pull
docker compose up -d
```

---

## Editing Config via Terminal (Recommended Method)

Since the config is hot-reload, the fastest way to iterate is with `sed`
for small targeted changes. Example — add a new service:

```bash
# Append a new service block to the AI section
cat >> ~/homepage/config/services.yaml << 'EOF'

    - New Service:
        href: http://<YOUR_SERVER_IP>:PORT
        description: Description here
        icon: icon-name.png
EOF
```

Or for targeted replacements:
```bash
sed -i 's/<OLD_VALUE>/<NEW_VALUE>/g' ~/homepage/config/services.yaml
```

Refresh your browser — changes appear instantly.

---

## Troubleshooting

**Widget shows "Error":**
- Check the API key is correct and has no extra whitespace
- Verify the service URL is reachable from the Homepage container
- Homepage uses the service's URL from the `widget.url` field — make sure
  it's the LAN IP (not localhost), accessible from within Docker

**Docker socket warnings:**
- Some systems require adding the homepage user to the docker group
- Or run: `sudo chmod 666 /var/run/docker.sock` (less secure, for testing)
