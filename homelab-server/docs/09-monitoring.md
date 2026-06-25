# 09 — Monitoring

Three layers of monitoring:
- **Beszel** — lightweight server dashboard (CPU, RAM, disk, network, Docker containers)
- **Prometheus + Node Exporter** — detailed time-series metrics collection
- **Grafana** — metric dashboards and visualization

---

## 1. Prepare Config Directory

```bash
mkdir -p ~/monitoring/{prometheus,grafana/provisioning/datasources,config/beszel}
cd ~/monitoring
```

---

## 2. Copy Configuration Files

Copy `prometheus/prometheus.yml` and
`grafana/provisioning/datasources/prometheus.yml` from this repo.

---

## 3. Configure Environment

```bash
cp .env.example .env
nano .env
```

You'll fill in `BESZEL_KEY` after the first time you start the Hub (step 5).

---

## 4. Start the Monitoring Stack

```bash
cd ~/monitoring
docker compose up -d
```

---

## 5. Open Firewall Ports

```bash
sudo ufw allow 8090/tcp comment 'Beszel Hub'
sudo ufw allow 9090/tcp comment 'Prometheus'
sudo ufw allow 3000/tcp comment 'Grafana'
```

---

## Part A — Beszel Setup

### 6. Initial Beszel Hub Login

Go to `http://<server-ip>:8090`

Create your admin account on first visit.

### 7. Add the Agent

In the Hub UI: **Add System** (top right)

- Name: `homeserver` (or whatever you like)
- Address: `172.17.0.1:45876`

> ⚠️ **Must use `172.17.0.1`, not `localhost`.**
> The Hub is a Docker container. `localhost` inside a container points to the
> container itself, not the host. `172.17.0.1` is the Docker bridge gateway —
> it correctly routes to the host, where the agent is listening.

After clicking **Add**, a **public key** is shown. Copy it.

### 8. Set the Agent Key

```bash
cd ~/monitoring
nano .env
# Paste the key as: BESZEL_KEY=<copied public key>

# Restart the agent with the correct key
docker compose restart beszel-agent
```

Back in the Hub UI, the system should turn green within a few seconds.

### 9. Why the Agent Needs `network_mode: host`

The Beszel agent must use `network_mode: host` so it can:
- Read actual host network interface stats (not just the container's virtual NIC)
- Read disk I/O from the real host filesystems
- Monitor all Docker containers on the host

Without `network_mode: host`, all network metrics would reflect only the
container's loopback interface — useless for real monitoring.

---

## Part B — Prometheus + Grafana Setup

### 10. Verify Prometheus Is Collecting Metrics

Go to `http://<server-ip>:9090`

- Status → Targets — both `prometheus` and `node_exporter` should show **UP**
- Try a query: `node_cpu_seconds_total`

If `node_exporter` shows DOWN, check:
```bash
docker compose logs node-exporter
# Verify it's running: docker compose ps
```

### 11. Grafana First Login

Go to `http://<server-ip>:3000`

Default credentials: `admin` / `admin`
Change the password immediately when prompted.

The Prometheus datasource is auto-provisioned via the config file in
`grafana/provisioning/datasources/prometheus.yml` — no manual setup needed.

### 12. Import a Node Exporter Dashboard

Grafana has a community dashboard library. A great pre-built dashboard
for Node Exporter is available online.

Dashboards → Import → Enter dashboard ID: **1860**
(Node Exporter Full — covers CPU, memory, disk, network in detail)

Select **Prometheus** as the data source → Import.

---

## Useful Monitoring Commands

```bash
# Check all monitoring containers
docker compose -f ~/monitoring/docker-compose.yml ps

# View Beszel Hub logs
docker compose -f ~/monitoring/docker-compose.yml logs beszel-hub -f

# View Beszel Agent logs
docker compose -f ~/monitoring/docker-compose.yml logs beszel-agent -f

# View Prometheus logs
docker compose -f ~/monitoring/docker-compose.yml logs prometheus -f

# Test Node Exporter is serving metrics on the host
curl http://localhost:9100/metrics | head -20

# Check disk usage on the media drive
df -h /mnt/media
```

---

## Cockpit (Bonus — System Management)

Cockpit provides a web-based system management UI (storage, services, logs, updates).
It runs as a systemd service — no Docker needed.

```bash
sudo apt install -y cockpit
sudo systemctl enable --now cockpit.socket
sudo ufw allow 9090/tcp comment 'Cockpit'
```

Access at: `https://<server-ip>:9090`
Login with your Linux username and password.

> ⚠️ Note: Cockpit uses port 9090, the same default port as Prometheus.
> In the provided monitoring `docker-compose.yml`, Prometheus runs on `9090`.
> If you run both, you'll need to change Prometheus to a different port
> (e.g., `9091:9090`) or access Cockpit via a different interface.
