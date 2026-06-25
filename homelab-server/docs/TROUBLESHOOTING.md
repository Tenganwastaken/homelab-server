# Troubleshooting

All the gotchas, errors, and fixes encountered building this stack.

---

## 🔴 The Golden Rule: Docker Containers and `localhost`

> **From inside a Docker container, `localhost` is the container itself — NOT the host machine.**

This causes the majority of connection failures in this stack.

**The fix:** Use `172.17.0.1` (Docker bridge gateway) to reach:
- The host machine
- Services running on the host (Jellyfin, Ollama)
- Other containers' exposed host ports

| Connection | Wrong | Right |
|---|---|---|
| Jellyseerr → Jellyfin | `http://localhost:8096` | `http://172.17.0.1:8096` |
| Bazarr → Radarr | `http://localhost:7878` | `http://172.17.0.1:7878` |
| Bazarr → Sonarr | `http://localhost:8989` | `http://172.17.0.1:8989` |
| Open WebUI → Ollama | `http://localhost:11434` | `http://172.17.0.1:11434` |
| Beszel Hub → Agent | `localhost:45876` | `172.17.0.1:45876` |

---

## Jellyseerr

### `EAI_AGAIN` DNS errors / can't reach TMDB

**Symptom:**
```
Error: getaddrinfo EAI_AGAIN api.themoviedb.org
```

**Cause:** The Jellyseerr Docker container doesn't inherit the host's DNS resolver.

**Fix:** Ensure the `dns:` block is present in `docker-compose.yml`:
```yaml
jellyseerr:
  dns:
    - 8.8.8.8
    - 1.1.1.1
```

Then restart:
```bash
docker compose restart jellyseerr
```

### Can't connect to Jellyfin during setup

**Cause:** Using `localhost` or the server's LAN IP directly.

**Fix:** Use `http://172.17.0.1:8096` as the Jellyfin URL.

### Testing connectivity from inside the Jellyseerr container

> ⚠️ Jellyseerr's container does not have `curl`. Use `wget` instead:

```bash
docker exec jellyseerr wget -qO- http://172.17.0.1:8096/health
```

---

## Radarr / Sonarr — Import Failures

### Downloads complete in qBittorrent but never import

**Cause:** Missing remote path mapping. qBittorrent reports the file path
using its internal container path, which Radarr/Sonarr can't map to their
own volume mount without being told explicitly.

**Fix:** In Radarr AND Sonarr:
Settings → Download Clients → Remote Path Mappings → Add:

| Field | Value |
|---|---|
| Host | `qbittorrent` |
| Remote Path | `/downloads/complete` |
| Local Path | `/downloads` |

### "Permissions error" on import

**Cause:** The config directory and downloaded files may have ownership
conflicts between the container user (PUID 1000) and root.

**Fix:** Check PUID/PGID in `.env` matches your user:
```bash
id $USER
# uid=1000(...) gid=1000(...)
```

If they don't match, update `.env` and restart:
```bash
docker compose down && docker compose up -d
```

### Manually added files not appearing in Radarr/Sonarr

Files must be in a correctly named folder structure before importing:
```
/mnt/media/movies/Movie Name (Year)/Movie Name (Year).mkv
```

Then in Radarr: Movies → Import Existing Movies → select `/movies`.

---

## Bazarr

### "Connection refused" when adding Radarr or Sonarr

**Cause:** Using `localhost` as the host address.

**Fix:** Use `172.17.0.1` as the address in both Radarr and Sonarr connection settings.

### Bazarr doesn't see movies/shows

**Cause:** Bazarr sources its library from Radarr/Sonarr, not directly from the filesystem.
Any file that isn't in Radarr or Sonarr's database won't appear in Bazarr.

**Fix:** Add or import the files in Radarr/Sonarr first. Then wait for Bazarr to sync.

### Addic7ed subtitles not working

**Cause:** Cookie-based auth expires and needs to be refreshed periodically.

**Fix:** Export fresh cookies from your browser after logging into addic7ed.com,
and update them in Bazarr's Addic7ed provider settings.

---

## Beszel

### Agent shows as disconnected in Hub

**Most common cause:** The Hub is trying to reach `localhost:45876` which doesn't
work from inside a Docker container.

**Fix:** In the Hub UI, ensure the system address is set to `172.17.0.1:45876`.

**Also check:** Is the `KEY` environment variable correct?

```bash
# View the agent's logs for clues
docker compose -f ~/monitoring/docker-compose.yml logs beszel-agent

# Verify the agent is actually listening
ss -tlnp | grep 45876
```

### Agent network stats look wrong (showing container stats, not host)

**Cause:** `network_mode: host` is missing from the agent's service definition.

**Fix:** Ensure the agent in `docker-compose.yml` has:
```yaml
beszel-agent:
  network_mode: host
```

Then restart:
```bash
docker compose restart beszel-agent
```

---

## Immich

### Container fails to start / PostgreSQL errors

**Cause:** Often a version mismatch between Immich server and its database.

**Fix:** Check all services use the same version tag in `.env`:
```bash
cat ~/immich/.env | grep IMMICH_VERSION
```

Always pin the version. Never use `:latest`.

### Photos not appearing after CLI import

**Cause:** The import job may still be running in the background.

**Fix:** Check Immich's job queue: Administration → Jobs → Library.
Let the "Extract metadata" and "Generate thumbnails" jobs finish.

### CLI import fails with auth error

```bash
# Re-authenticate
immich logout
immich login http://<server-ip>:2283 <your-email>
```

---

## Jellyfin

### Custom CSS not saving / not applying

**Cause:** In Jellyfin v10.11+, the CSS location changed.

**Fix:** Go to Dashboard → Administration → **Branding** (not General).
Paste custom CSS in the "Custom CSS code" field.

### Jellyfin service won't start after `apt upgrade`

```bash
sudo systemctl status jellyfin
sudo journalctl -u jellyfin -n 50
```

Common cause: incompatible plugin after a major version update.
Fix: clear plugin cache and restart:
```bash
sudo systemctl stop jellyfin
sudo rm -rf /var/lib/jellyfin/plugins/*/
sudo systemctl start jellyfin
```

---

## Docker / General

### Config directory is root-owned, can't read files

This is expected — Docker creates config directories as root.

```bash
# Always use sudo for config file operations
sudo ls ~/mediastack/config/radarr/
sudo cat ~/mediastack/config/sonarr/config.xml
sudo nano ~/mediastack/config/bazarr/config/config.ini
```

### Container exits immediately on start

```bash
# Check the specific container's logs
docker compose logs <container-name>

# View last 50 lines even after container stopped
docker logs --tail 50 <container-name>
```

### Port already in use

```bash
# Find what's using a port
sudo ss -tlnp | grep :PORT
# or
sudo lsof -i :PORT
```

### Renaming the server hostname after setup

If you rename the server, update all config files that reference the old name:

```bash
# Dry run first — see what would change
grep -r "old-hostname" ~/mediastack/ ~/monitoring/ ~/immich/ ~/homepage/

# Then replace (be specific with paths to avoid unintended replacements)
sed -i 's/old-hostname/new-hostname/g' ~/homepage/config/services.yaml
```

Also update:
```bash
sudo hostnamectl set-hostname new-hostname
sudo nano /etc/hosts   # update 127.0.1.1 line
```

---

## Discord Bot

### Bot not responding to commands

1. Check the service is running: `systemctl status discordbot`
2. Check logs: `sudo journalctl -u discordbot -n 50`
3. Verify the `.env` token is correct and not expired
4. Ensure "Message Content Intent" is enabled in the Developer Portal

### Reaction roles not working

- Confirm Developer Mode is enabled in Discord settings
- Verify the `REACTION_ROLES_MESSAGE_ID` in `.env` is the exact message ID
- Check "Server Members Intent" is enabled in the Developer Portal

### Voice rooms not being created

- Verify `VOICE_CREATOR_CHANNEL_ID` is set to a voice channel (not a text channel)
- Ensure the bot has permission to Create Voice Channels and Move Members
- Check logs for permission errors: `sudo journalctl -u discordbot -f`
