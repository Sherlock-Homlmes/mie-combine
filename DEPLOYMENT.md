# Deployment Guide - Mie Discord Bot

Hướng dẫn deploy bot Discord với Docker Compose (local) và Docker Swarm (production).

## 📋 Cấu trúc Files

- [`Dockerfile`](Dockerfile:1) - Docker image definition
- [`docker-compose.yaml`](docker-compose.yaml:1) - Docker Swarm config (production)
- [`docker-compose.dev.yaml`](docker-compose.dev.yaml:1) - Docker Compose config (local development)
- [`deploy-swarm.sh`](deploy-swarm.sh:1) - Deployment script cho Swarm
- [`.env`](.env:1) - Environment variables (KHÔNG commit vào git)

## 🚀 Local Development (Docker Compose)

### 1. Setup Environment Variables

```bash
# Copy file .env.example
cp .env.example .env

# Edit .env và điền thông tin
nano .env
```

### 2. Chạy bot với Docker Compose

```bash
# Build và start
docker compose -f docker-compose.dev.yaml up --build

# Hoặc chạy ở background
docker compose -f docker-compose.dev.yaml up -d

# Xem logs
docker compose -f docker-compose.dev.yaml logs -f

# Stop
docker compose -f docker-compose.dev.yaml down
```

## 🐳 Production Deployment (Docker Swarm)

### 1. Chuẩn bị Server

```bash
# Update system
sudo apt update && sudo apt upgrade -y

# Cài Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh

# Thêm user vào docker group
sudo usermod -aG docker $USER

# Kích hoạt Docker
sudo systemctl enable docker
sudo systemctl start docker
```

### 2. Setup Environment Variables

```bash
# Tạo file .env trên server
nano .env
```

Nội dung file `.env`:

```env
BOT_TOKEN="discord_bot_token_cua_ban"
DATABASE_URL="mongodb://username:password@host:port/database"
GEMINI_AI_API_KEY="gemini_api_key_cua_ban"
ENV="PROD"
BOT_ONLY="false"
OOPS_WEBHOOK_URL="webhook_url_optionnal"
```

### 3. Khởi tạo Docker Swarm

```bash
# Single node (cho bot Discord)
docker swarm init

# Multi-node cluster (nếu cần)
# Manager node:
docker swarm init --advertise-addr <IP_MANAGER>

# Worker nodes:
docker swarm join --token <WORKER_TOKEN> <MANAGER_IP>:2377
```

### 4. Deploy Bot

#### Cách 1: Sử dụng deployment script (Khuyến nghị)

```bash
# Make script executable (chạy 1 lần)
chmod +x deploy-swarm.sh

# Deploy
./deploy-swarm.sh
```

#### Cách 2: Deploy thủ công

```bash
# Build image
docker build -t mie-bot:latest .

# Deploy stack
docker stack deploy -c docker-compose.yaml mie-bot
```

### 5. Quản lý Services

```bash
# Xem danh sách services
docker service ls

# Xem chi tiết service
docker service ps mie-bot_mie-bot

# Xem logs real-time
docker service logs -f mie-bot_mie-bot

# Xem 100 dòng logs gần nhất
docker service logs --tail 100 mie-bot_mie-bot

# Scale services (nếu cần)
docker service scale mie-bot_mie-bot=3

# Update stack
./deploy-swarm.sh

# Hoặc
docker stack deploy -c docker-compose.yaml mie-bot

# Remove stack
docker stack rm mie-bot
```

## 🔧 Troubleshooting

### Service không start

```bash
# Xem logs
docker service logs mie-bot_mie-bot

# Xem events
docker service ps mie-bot_mie-bot --no-trunc

# Inspect service
docker service inspect mie-bot_mie-bot
```

### Rollback nếu có vấn đề

```bash
# Xem versions
docker service ps mie-bot_mie-bot

# Rollback
docker service rollback mie-bot_mie-bot
```

### Rebuild và redeploy

```bash
# Build lại image
docker build -t mie-bot:latest .

# Redeploy
docker stack deploy -c docker-compose.yaml mie-bot

# Force update (không có thay đổi code)
docker service update --force mie-bot_mie-bot
```

## 🔒 Security Best Practices

### 1. Environment Variables

- **KHÔNG** commit file `.env` vào git
- Sử dụng strong passwords cho database
- Rotate keys/passwords thường xuyên

### 2. Firewall Rules

```bash
# Chỉ cho phép port cần thiết
sudo ufw allow 22/tcp    # SSH
sudo ufw allow 2377/tcp  # Cluster management
sudo ufw allow 7946/tcp  # Container network discovery
sudo ufw allow 7946/udp  # Container network discovery
sudo ufw allow 4789/udp  # Overlay network
sudo ufw enable
```

### 3. Docker Secrets (Optional)

```bash
# Tạo secret cho BOT_TOKEN
echo "discord_bot_token" | docker secret create bot_token -

# Trong docker-compose.yaml:
# secrets:
#   bot_token:
#     external: true
# environment:
#   BOT_TOKEN_FILE: /run/secrets/bot_token
```

## 📊 Monitoring

### Health Check

```bash
# Xem status
docker service ps mie-bot_mie-bot

# Xem resource usage
docker stats
```

### Log Rotation

Tạo file `/etc/docker/daemon.json`:

```json
{
  "log-driver": "json-file",
  "log-opts": {
    "max-size": "10m",
    "max-file": "3"
  }
}
```

Restart Docker:

```bash
sudo systemctl restart docker
```

## 🔄 CI/CD (Optional)

### GitHub Actions Example

```yaml
name: Deploy to Production

on:
  push:
    branches: [main]

jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2

      - name: Deploy to server
        uses: appleboy/ssh-action@master
        with:
          host: ${{ secrets.SERVER_HOST }}
          username: ${{ secrets.SERVER_USER }}
          key: ${{ secrets.SSH_KEY }}
          script: |
            cd /path/to/app
            git pull
            ./deploy-swarm.sh
```

## 💾 Backup & Recovery

### Backup Data

```bash
# Backup MongoDB (nếu dùng local)
docker exec mongodb_container mongodump --out /backup

# Backup Docker configs
tar -czf docker-backup.tar.gz docker-compose.yaml .env

# Backup image
docker save mie-bot:latest | gzip > mie-bot-backup.tar.gz
```

### Recovery

```bash
# Restore MongoDB
docker exec mongodb_container mongorestore /backup

# Re-deploy stack
docker stack deploy -c docker-compose.yaml mie-bot

# Restore image
docker load < mie-bot-backup.tar.gz
```

## 📝 Tóm tắt Commands

### Local Development

```bash
docker compose -f docker-compose.dev.yaml up --build
docker compose -f docker-compose.dev.yaml logs -f
docker compose -f docker-compose.dev.yaml down
```

### Production

```bash
./deploy-swarm.sh
docker service ls
docker service logs -f mie-bot_mie-bot
docker stack rm mie-bot
```

## 🆘 Hỗ trợ

Nếu gặp vấn đề:

1. Kiểm tra logs: `docker service logs mie-bot_mie-bot`
2. Kiểm tra service status: `docker service ps mie-bot_mie-bot`
3. Rebuild và redeploy: `./deploy-swarm.sh`
