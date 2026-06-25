# 06 — Jellyseerr & Bazarr Setup

Both services have specific networking requirements because they run in Docker
but need to communicate with Jellyfin (on the host) and Radarr/Sonarr (also
in Docker). Use `172.17.0.1` consistently — never `localhost`.

---

## Jellyseerr

Jellyseerr is the request frontend. Users browse and request movies/shows here,
which get automatically sent to Radarr or Sonarr.

### 1. DNS — Why It's In the docker-compose

Jellyseerr makes outbound API calls to TMDB and other external services.
Without explicit DNS entries, Docker containers may inherit a broken or missing
resolver, causing `EAI_AGAIN` DNS resolution errors that completely break
Jellyseerr's functionality.

The `dns:` block in `docker-compose.yml` fixes this permanently:

```yaml
jellyseerr:
  dns:
    - 8.8.8.8
    - 1.1.1.1
```

This is already included in the provided `docker-compose.yml`. Do not remove it.

**Symptom without it:**
```
Error: getaddrinfo EAI_AGAIN api.themoviedb.org
```

### 2. Connect Jellyseerr to Jellyfin

Go to `http://<server-ip>:5055` → complete the setup wizard.

When asked for the Jellyfin URL:

```
http://172.17.0.1:8096
```

> ❌ **Do NOT use** `http://localhost:8096` — Jellyseerr is a container and
> `localhost` points to the container itself, not your host machine.
> ✅ **Always use** `http://172.17.0.1:8096` (Docker bridge gateway = host).

Enter your Jellyfin admin username and password, then click **Test**.

### 3. Connect Jellyseerr to Radarr

Settings → Services → Add Radarr:

| Field | Value |
|---|---|
| Default Server | ✅ |
| Server Name | Radarr |
| Hostname | `172.17.0.1` |
| Port | `7878` |
| API Key | *(from Radarr Settings → General)* |
| Quality Profile | Your preferred quality profile |
| Root Folder | `/movies` |

Click **Test** → **Save**.

### 4. Connect Jellyseerr to Sonarr

Settings → Services → Add Sonarr:

| Field | Value |
|---|---|
| Default Server | ✅ |
| Server Name | Sonarr |
| Hostname | `172.17.0.1` |
| Port | `8989` |
| API Key | *(from Sonarr Settings → General)* |
| Quality Profile | Your preferred quality profile |
| Root Folder | `/tv` |
| Language Profile | *(select one)* |

Click **Test** → **Save**.

### 5. Test It End-to-End

1. Log into Jellyseerr
2. Search for a movie and click "Request"
3. Check Radarr — the movie should appear as "Monitored"
4. qBittorrent should pick up the download shortly after

---

## Bazarr

Bazarr automatically downloads subtitles for your entire library.
It reads the library via Radarr and Sonarr (not directly from the filesystem).

### 1. Access Bazarr

`http://<server-ip>:6767`

### 2. Connect to Sonarr

Settings → Sonarr:

| Field | Value |
|---|---|
| Enabled | ✅ |
| Address | `172.17.0.1` |
| Port | `8989` |
| API Key | *(from Sonarr Settings → General)* |

Click **Test** → **Save**.

### 3. Connect to Radarr

Settings → Radarr:

| Field | Value |
|---|---|
| Enabled | ✅ |
| Address | `172.17.0.1` |
| Port | `7878` |
| API Key | *(from Radarr Settings → General)* |

Click **Test** → **Save**.

> ❌ **Do NOT use** `localhost` for either address — same Docker networking
> rule applies. Bazarr is a container; the host is at `172.17.0.1`.

### 4. Add Subtitle Providers

Settings → Providers → Add Provider

Recommended providers (requires accounts on each):
- **OpenSubtitles.com** — large database, requires free account
- **OpenSubtitles.org** — older database, also free
- **Addic7ed** — great for TV shows; requires browser cookie authentication

**For Addic7ed:**
1. Log into addic7ed.com in your browser
2. Export cookies as a Netscape-format file (use a browser extension)
3. In Bazarr's Addic7ed settings, paste the cookies
4. Also paste the User-Agent string from your browser

### 5. Set Up Language Profiles

Settings → Languages → Add Profile:

Example "English + Greek" profile:
- Language: Greek (preferred, cutoff language: English)
- Language: English

Assign this profile to both Movies and Series in Bazarr's settings.

### 6. Trigger Initial Subtitle Scan

Movies → ☁ icon (top right) → "Search for Missing"
Series → same

Bazarr will queue up subtitle searches for your entire library.

> ⚠️ **Bazarr reads the library from Radarr/Sonarr.**
> If you manually moved or added files outside of Radarr/Sonarr, Bazarr
> won't see them until you add/import those files into Radarr/Sonarr first.
