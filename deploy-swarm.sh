#!/bin/bash

# Deploy script cho Docker Swarm
# Script này sẽ build image và deploy lên Docker Swarm

set -e

echo "🔨 Building Docker image..."
docker build -t mie-bot:latest .

echo "🚀 Deploying to Docker Swarm..."
docker stack deploy -c docker-compose.yaml mie-bot

echo "✅ Deployment complete!"
echo ""
echo "Kiểm tra status:"
echo "  docker service ls"
echo "  docker service logs -f mie-bot_mie-bot"
echo ""
echo "Xem logs:"
echo "  docker service logs mie-bot_mie-bot"
