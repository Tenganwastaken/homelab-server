# 05 — Jellyfin Setup

Jellyfin runs as a native systemd service (not Docker) for better hardware
transcoding support and GPU access. It listens on port 8096.

---

## 1. Install Jellyfin

```bash
# Add Jellyfin repository
curl -fsSL https://repo.jellyfin.org/install-debuntu.sh | sudo bash
```

This script:
- Adds the Jellyfin apt repository and GPG key
- Installs `jellyfin` (server + web)
- Creates the `jellyfin` systemd service

---

## 2. Start and Enable the Service

```bash
sudo systemctl enable --now jellyfin
sudo systemctl status jellyfin
```

---

## 3. Open the Firewall Port

```bash
sudo ufw allow 8096/tcp comment 'Jellyfin'
```

---

## 4. Initial Setup

Go to `http://<server-ip>:8096`

Follow the setup wizard:
1. Create an admin account
2. Set up your media libraries:
   - **Movies** → Add folder: `/mnt/media/movies`
   - **TV Shows** → Add folder: `/mnt/media/tv`
3. Choose metadata providers (TheTVDB, TheMovieDB recommended)
4. Let the initial library scan complete

---

## 5. Hardware Transcoding (Optional)

For Intel iGPU (Quick Sync):

```bash
# Check if Intel GPU is available
ls /dev/dri/

# Add jellyfin user to the render group
sudo usermod -aG render jellyfin
sudo usermod -aG video jellyfin
sudo systemctl restart jellyfin
```

In Jellyfin: Dashboard → Playback → Transcoding:
- Enable Hardware Acceleration: Intel Quick Sync (or appropriate option)
- Enable all compatible codecs

---

## 6. Custom CSS (Jellyfin v10.11+)

> ⚠️ Location changed in v10.11: CSS is no longer under "General" settings.

Dashboard → Administration → **Branding** → Custom CSS

Paste your CSS there. Example minimal dark theme tweak:
```css
:root {
  --accent-color: #00a4dc;
}
```

---

## 7. Get the API Key (for Homepage widget)

Dashboard → API Keys → + (create new key)
Label it "homepage" or similar. Copy the key.

---

## 8. Useful Commands

```bash
# View Jellyfin logs
sudo journalctl -u jellyfin -f

# Restart Jellyfin
sudo systemctl restart jellyfin

# Check Jellyfin version
dpkg -l jellyfin

# Update Jellyfin
sudo apt update && sudo apt upgrade jellyfin
```

---

## ⚠️ Jellyfin from Jellyseerr/Docker Containers

Because Jellyfin runs on the **host** (not in Docker), other containers cannot
reach it via `localhost`. They must use the Docker bridge gateway:

```
http://172.17.0.1:8096
```

See [Jellyseerr & Bazarr setup](06-jellyseerr-bazarr.md) for details.
