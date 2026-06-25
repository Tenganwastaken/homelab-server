# 04 — *Arr Stack Configuration

Configure Prowlarr, qBittorrent, Radarr, and Sonarr to form a complete
automated download pipeline.

---

## Overview of the Pipeline

```
Prowlarr (indexers)
    ↓ syncs to
Radarr / Sonarr (automation)
    ↓ sends download to
qBittorrent
    ↓ saves file to /downloads/complete
    ↓ notifies Radarr / Sonarr
Radarr / Sonarr (imports to library)
    ↓
/mnt/media/movies or /mnt/media/tv
```

---

## Step 1 — qBittorrent Initial Setup

First login: go to `http://<server-ip>:8080`

Default credentials are in the container logs:
```bash
docker compose logs qbittorrent | grep -i "password"
```

Change the password immediately: Tools → Options → Web UI → Password.

### Configure Download Paths

Tools → Options → Downloads:

| Setting | Value |
|---|---|
| Default Save Path | `/downloads/complete` |
| Keep incomplete torrents in | `/downloads/incomplete` |

Enable "Keep incomplete torrents in:" and set it to `/downloads/incomplete`.

Click **Save**.

---

## Step 2 — Prowlarr Setup

Go to `http://<server-ip>:9696`

### Add Indexers

Settings → Indexers → Add Indexer
- Add the torrent indexers you have access to
- Test each one after adding

### Add Radarr as an App

Settings → Apps → Add Application → Radarr
- Prowlarr Server: `http://prowlarr:9696`
- Radarr Server: `http://radarr:7878`
- API Key: *(paste from Radarr → Settings → General → API Key)*
- Click Test → Save

### Add Sonarr as an App

Settings → Apps → Add Application → Sonarr
- Sonarr Server: `http://sonarr:8989`
- API Key: *(paste from Sonarr → Settings → General → API Key)*
- Click Test → Save

Prowlarr will now automatically sync all indexers to both Radarr and Sonarr.

---

## Step 3 — Radarr Configuration

Go to `http://<server-ip>:7878`

### Add qBittorrent as Download Client

Settings → Download Clients → Add → qBittorrent

| Field | Value |
|---|---|
| Host | `qbittorrent` |
| Port | `8080` |
| Username | `admin` |
| Password | *(your qBittorrent password)* |
| Category | `radarr` |

Click **Test** → **Save**.

### ⚠️ Add Remote Path Mapping (Critical Step)

This is the most common source of import failures.

qBittorrent reports completed downloads using the path it sees inside its
container (`/downloads/complete`). Radarr needs to know how to find those
same files from its own container's perspective.

Settings → Download Clients → scroll to **Remote Path Mappings** → Add:

| Field | Value |
|---|---|
| Host | `qbittorrent` |
| Remote Path | `/downloads/complete` |
| Local Path | `/downloads` |

Click **Save**.

### Set Root Folder

Settings → Media Management → Root Folders → Add:
- Path: `/movies`

### Enable Hardlinks/Instant Moves (optional but recommended)

Settings → Media Management:
- Check "Use Hardlinks instead of Copy"

This avoids duplicating files when importing.

---

## Step 4 — Sonarr Configuration

Go to `http://<server-ip>:8989`

### Add qBittorrent as Download Client

Settings → Download Clients → Add → qBittorrent

| Field | Value |
|---|---|
| Host | `qbittorrent` |
| Port | `8080` |
| Username | `admin` |
| Password | *(your qBittorrent password)* |
| Category | `sonarr` |

Click **Test** → **Save**.

### ⚠️ Add Remote Path Mapping (same as Radarr)

Settings → Download Clients → Remote Path Mappings → Add:

| Field | Value |
|---|---|
| Host | `qbittorrent` |
| Remote Path | `/downloads/complete` |
| Local Path | `/downloads` |

Click **Save**.

### Set Root Folder

Settings → Media Management → Root Folders → Add:
- Path: `/tv`

---

## Step 5 — Test the Full Pipeline

1. In Radarr, search for a movie and add it
2. Go to the movie page → click the download icon (manual search) to trigger an immediate download
3. In qBittorrent, confirm the torrent appears under the `radarr` category
4. Once complete, Radarr should automatically import the file to `/movies`
5. Check Radarr's Activity → History to confirm the import succeeded

If import fails, check:
- Activity → Queue in Radarr (look for import errors)
- The remote path mapping is correct
- `/mnt/media/downloads/complete` on the host actually has the file

---

## Getting API Keys

You'll need these for Prowlarr sync and Homepage dashboard widgets:

```
Radarr:    Settings → General → API Key
Sonarr:    Settings → General → API Key
Prowlarr:  Settings → General → API Key
Bazarr:    Settings → General → Security → API Key (after Bazarr setup)
```
