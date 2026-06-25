# 11 — Remote Access

Two tools for accessing the server remotely:
- **Tailscale** — zero-config VPN; access all services by Tailscale IP from anywhere
- **NoMachine** — remote desktop with full GUI; useful for graphical tasks

---

## Part A — Tailscale VPN

Tailscale creates a private encrypted mesh network between all your devices.
Once set up, you can access the server (and all its service ports) from your
phone, laptop, or any other device on your Tailscale network — no port
forwarding or VPN server configuration needed.

### 1. Install Tailscale on the Server

```bash
curl -fsSL https://tailscale.com/install.sh | sh
sudo tailscale up
```

A URL will be printed — open it in your browser to authenticate and link
the server to your Tailscale account.

### 2. Get the Server's Tailscale IP

```bash
tailscale ip -4
# e.g., 100.x.x.x
```

### 3. Enable Auto-Start

Tailscale starts automatically after installation. Verify:

```bash
sudo systemctl status tailscaled
sudo systemctl is-enabled tailscaled
```

### 4. Install Tailscale on Your Other Devices

- **Mobile:** Tailscale app from App Store / Google Play
- **Desktop:** https://tailscale.com/download

Sign in with the same account. All your devices will appear in the same mesh.

### 5. Access Services Remotely

Once on Tailscale, use the server's Tailscale IP instead of its LAN IP:

```
http://100.x.x.x:8096    ← Jellyfin (from anywhere)
http://100.x.x.x:5055    ← Jellyseerr
http://100.x.x.x:2283    ← Immich
etc.
```

No additional firewall rules needed — Tailscale traffic bypasses UFW.

### 6. Useful Tailscale Commands

```bash
# Check connection status and peers
tailscale status

# See this device's Tailscale IP
tailscale ip

# Temporarily disconnect from Tailscale
sudo tailscale down

# Reconnect
sudo tailscale up

# View Tailscale logs
sudo journalctl -u tailscaled -f
```

---

## Part B — NoMachine Remote Desktop

NoMachine provides a fast, low-latency remote desktop to the server's GUI.
This is useful for graphical tasks that are awkward over SSH
(e.g., running a browser on the server, GUI apps, desktop file management).

> Only needed if your server runs a desktop environment (Ubuntu Desktop).
> If using Ubuntu Server (headless), skip this section.

### 1. Download and Install NoMachine on the Server

```bash
# Download the .deb package (check https://www.nomachine.com/download for latest)
wget https://download.nomachine.com/download/8.x/Linux/nomachine_8.x.x_x_amd64.deb

# Install
sudo dpkg -i nomachine_*.deb
```

NoMachine runs as a background service automatically after install.

### 2. Open the Firewall Port

```bash
sudo ufw allow 4000/tcp comment 'NoMachine'
```

### 3. Install NoMachine on Your Client Machine

Download from https://www.nomachine.com/download for your OS (Windows/macOS/Linux).

### 4. Connect

Open NoMachine → Add machine → enter the server's **Tailscale IP** (recommended)
or LAN IP → port `4000` → connect with your Linux username and password.

### 5. Performance Tips

- In the NoMachine session, set Display Quality to "Adapt to network"
- Disable "Use hardware acceleration" if you see graphical glitches
- Connection over Tailscale works well even over mobile networks

---

## SSH Access (Always Available)

SSH is always the most reliable remote access method for terminal work:

```bash
# From your local machine
ssh <username>@<server-lan-ip>

# Over Tailscale (from anywhere)
ssh <username>@<tailscale-ip>
```

For passwordless SSH, ensure your public key is in `~/.ssh/authorized_keys`
on the server (set up in doc 01).
