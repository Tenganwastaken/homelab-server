# 01 — Server Setup

Ubuntu 24.04 LTS setup, Docker installation, and server hardening.

---

## 1. Install Ubuntu Server 24.04

Download the ISO from https://ubuntu.com/download/server and install.
During setup, create your user account and enable OpenSSH server.

---

## 2. First Boot — System Updates

```bash
sudo apt update && sudo apt upgrade -y
sudo apt install -y curl git wget htop nano ufw
```

---

## 3. Set a Static Hostname

```bash
sudo hostnamectl set-hostname <your-hostname>
```

Edit `/etc/hosts` to match:

```bash
sudo nano /etc/hosts
# Change the line:  127.0.1.1  old-hostname
# To:               127.0.1.1  <your-hostname>
```

---

## 4. Install Docker

```bash
# Add Docker's official GPG key
sudo apt-get install -y ca-certificates curl
sudo install -m 0755 -d /etc/apt/keyrings
sudo curl -fsSL https://download.docker.com/linux/ubuntu/gpg \
  -o /etc/apt/keyrings/docker.asc
sudo chmod a+r /etc/apt/keyrings/docker.asc

# Add Docker repo
echo \
  "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.asc] \
  https://download.docker.com/linux/ubuntu \
  $(. /etc/os-release && echo "$VERSION_CODENAME") stable" | \
  sudo tee /etc/apt/sources.list.d/docker.list > /dev/null

# Install Docker Engine + Compose plugin
sudo apt-get update
sudo apt-get install -y docker-ce docker-ce-cli containerd.io \
  docker-buildx-plugin docker-compose-plugin
```

### Add your user to the docker group

```bash
sudo usermod -aG docker $USER
newgrp docker
```

### Verify

```bash
docker compose version
docker run hello-world
```

---

## 5. Enable UFW Firewall

```bash
sudo ufw allow OpenSSH
sudo ufw allow 80/tcp
sudo ufw allow 443/tcp
sudo ufw enable
sudo ufw status
```

Add additional port rules as you deploy each service:

```bash
# Example: open a service port
sudo ufw allow 8096/tcp comment 'Jellyfin'
```

---

## 6. Install Node.js (for SkinPeek bot)

```bash
curl -fsSL https://deb.nodesource.com/setup_20.x | sudo -E bash -
sudo apt-get install -y nodejs
node --version
```

---

## 7. Set Up SSH Key Authentication (optional but recommended)

From your local machine:

```bash
ssh-keygen -t ed25519 -C "homelab"
ssh-copy-id <username>@<server-ip>
```

Then disable password SSH login on the server:

```bash
sudo nano /etc/ssh/sshd_config
# Set: PasswordAuthentication no
sudo systemctl restart ssh
```

---

## 8. Check Your User's PUID/PGID

You'll need these for all Docker containers:

```bash
id $USER
# uid=1000(username) gid=1000(username) groups=...
```

Note: Most Docker containers use `PUID=1000` and `PGID=1000` by default.
If your values differ, update the `.env` files in each service.
