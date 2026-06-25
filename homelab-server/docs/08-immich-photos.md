# 08 — Immich Photos

Immich is a self-hosted Google Photos replacement with face recognition,
album sharing, and mobile sync. It uses PostgreSQL and Redis internally.

---

## 1. Prepare the Directory Structure

This should already exist from the storage setup, but verify:

```bash
ls /mnt/media/immich/
# Should show: library/  postgres/
```

If not:
```bash
sudo mkdir -p /mnt/media/immich/{library,postgres}
sudo chown -R $USER:$USER /mnt/media/immich
```

---

## 2. Configure the .env File

```bash
cd ~/immich
cp .env.example .env
nano .env
```

Set:
- `IMMICH_VERSION` — pin to the latest stable (check https://github.com/immich-app/immich/releases)
- `DB_PASSWORD` — use a strong random password
- `UPLOAD_LOCATION=/mnt/media/immich/library`
- `DB_DATA_LOCATION=/mnt/media/immich/postgres`

> ⚠️ **Never use `:latest` for Immich.** It has frequent breaking changes.
> Always pin to a specific version tag like `v1.111.0`.

---

## 3. Start Immich

```bash
cd ~/immich
docker compose up -d
```

Wait about 30–60 seconds for all services to initialize, especially
the PostgreSQL container with pgvecto-rs extensions.

```bash
docker compose ps
# All containers should show healthy/running
```

---

## 4. Open the Firewall Port

```bash
sudo ufw allow 2283/tcp comment 'Immich'
```

---

## 5. Initial Setup

Go to `http://<server-ip>:2283`

1. Create your admin account (email + password)
2. You're in — skip the optional onboarding steps for now

---

## 6. Mobile Sync

Install the Immich app (iOS or Android) → Settings → Server URL:

```
http://<server-ip>:2283
```

If accessing from outside your home network, use your Tailscale IP:
```
http://<tailscale-ip>:2283
```

Enable automatic backup in the mobile app settings.

---

## 7. Bulk Import via CLI

Use the Immich CLI to import existing photo libraries from disk.
It handles deduplication automatically via checksums — safe to run multiple times.

### Install the CLI

```bash
npm install -g @immich/cli
```

### Authenticate

```bash
immich login http://<server-ip>:2283 <your-email>
# Enter your password when prompted
```

### Import a Folder (flat, no album)

```bash
immich upload --recursive /mnt/media/photos/
```

### Import a Folder and Create an Album

```bash
immich upload --recursive --album /mnt/media/photos/2023/
```

The `--album` flag uses the folder name as the album name.
Each subdirectory becomes its own album.

### Import with Albums from Folder Structure

```bash
# Recursively import and group into albums by top-level subfolder
immich upload --recursive --album-name "Imported" /mnt/media/photos/
```

### Incremental Imports (safe to repeat)

The CLI will skip already-uploaded files via SHA1 checksums.
You can run the import command again after adding new files — no duplicates.

```bash
immich upload --recursive /mnt/media/photos/
```

---

## 8. Updating Immich

Immich updates frequently. Always check the release notes first:
https://github.com/immich-app/immich/releases

```bash
cd ~/immich
# Update the version in .env
nano .env   # change IMMICH_VERSION=vX.X.X

# Pull and restart
docker compose pull
docker compose up -d
```

> ⚠️ Never skip versions when major releases include migration scripts.
> Read the release notes before each update.

---

## 9. Useful Commands

```bash
# View Immich server logs
docker compose logs immich-server -f

# View all Immich logs
docker compose logs -f

# Stop Immich (e.g., before a database backup)
docker compose down

# Backup the PostgreSQL database
docker exec immich-postgres pg_dumpall -U postgres > immich-backup-$(date +%F).sql
```
