#!/bin/bash

# Setup script for Docker Swarm on VPS
# Script này sẽ cài đặt Docker và khởi tạo Docker Swarm

set -e

echo "🔧 Setting up Docker Swarm..."

# Check if Docker is installed
if ! command -v docker &> /dev/null; then
    echo "📦 Installing Docker..."
    curl -fsSL https://get.docker.com -o get-docker.sh
    sh get-docker.sh
    usermod -aG docker $USER
    echo "✅ Docker installed"
else
    echo "✅ Docker already installed"
fi

# Check if swarm is initialized
if ! docker info | grep -q "Swarm: active"; then
    echo "🐝 Initializing Docker Swarm..."
    # Get the primary IP address to advertise (prefer IPv4)
    ADVERTISE_ADDR=$(hostname -I | awk '{print $1}')
    echo "Using IP address: $ADVERTISE_ADDR"
    docker swarm init --advertise-addr $ADVERTISE_ADDR
    echo "✅ Docker Swarm initialized"
else
    echo "✅ Docker Swarm already active"
fi

echo ""
echo "🎉 Setup complete!"
echo ""
echo "To add worker nodes, run this command on other nodes:"
echo "  docker swarm join --token $(docker swarm join-token worker | grep -o 'docker swarm join.*')"
echo ""
echo "To get manager join token, run:"
echo "  docker swarm join-token manager"
