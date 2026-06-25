# 02 — Storage Setup

Mount a dedicated HDD/SSD for all media and set up the directory structure.

---

## 1. Identify Your Drive

```bash
lsblk -f
```

Look for your media drive (e.g., `/dev/sdb`). Note the UUID of the partition you want to mount.

```bash
sudo blkid /dev/sdb1
# /dev/sdb1: UUID="xxxx-xxxx-xxxx" TYPE="ext4" ...
```

---

## 2. Format the Drive (if new/empty)

> ⚠️ This destroys all data on the drive. Skip if already formatted.

```bash
# Create a single partition
sudo fdisk /dev/sdb
# Press: n (new), p (primary), 1 (partition 1), Enter, Enter, w (write)

# Format as ext4
sudo mkfs.ext4 /dev/sdb1

# Get the UUID of the new partition
sudo blkid /dev/sdb1
```

> **Note:** ext4 is a Linux-only filesystem. Windows cannot read it natively.
> If you ever need to access the drive from Windows, share it over Samba instead
> of physically moving the drive.

---

## 3. Create the Mount Point

```bash
sudo mkdir -p /mnt/media
```

---

## 4. Mount Permanently via fstab

```bash
sudo nano /etc/fstab
```

Add this line at the bottom (replace with your actual UUID):

```
UUID=<YOUR_DRIVE_UUID>  /mnt/media  ext4  defaults,nofail  0  2
```

The `nofail` option prevents boot failure if the drive is absent.

```bash
# Mount now without rebooting
sudo mount -a

# Verify
df -h /mnt/media
```

---

## 5. Create the Media Directory Structure

```bash
sudo mkdir -p /mnt/media/{movies,tv,downloads/{complete,incomplete},photos,immich/{library,postgres}}

# Give your user ownership
sudo chown -R $USER:$USER /mnt/media
```

Final structure:

```
/mnt/media/
├── movies/              # Radarr final movie library
├── tv/                  # Sonarr final TV library
├── downloads/
│   ├── complete/        # qBittorrent completed downloads
│   └── incomplete/      # qBittorrent in-progress downloads
├── photos/              # Organized photo archive
└── immich/
    ├── library/         # Immich photo/video storage
    └── postgres/        # Immich PostgreSQL database
```

---

## 6. Verify Permissions

```bash
ls -la /mnt/media
# All directories should be owned by your user, not root
```

If any are root-owned:

```bash
sudo chown -R $USER:$USER /mnt/media
```

---

## ⚠️ Config Directory Ownership Note

When Docker Compose creates config directories (e.g., `./config/radarr`),
it creates them as **root-owned**, not your user. This is expected.

Always use `sudo` when reading or editing files inside these config directories:

```bash
# Example: read Radarr's config
sudo cat ~/mediastack/config/radarr/config.xml

# Example: edit a config file
sudo nano ~/mediastack/config/bazarr/config/config.ini
```
