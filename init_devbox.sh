#!/bin/bash
set -e

echo "--- 1. Updating System & Installing Dependencies ---"
apt-get update
DEBIAN_FRONTEND=noninteractive apt-get install -y \
    openssh-server \
    curl git sudo build-essential gdb cmake \
    python3 python3-pip python3-venv \
    openjdk-17-jdk \
    nmap net-tools iputils-ping \
    postgresql-client jq htop vim tree tmux zsh

echo "--- 2. Installing Node.js (LTS) ---"
if ! command -v node > /dev/null; then
    curl -fsSL https://deb.nodesource.com/setup_lts.x | bash -
    apt-get install -y nodejs
fi

echo "--- 3. Installing AI CLIs ---"
npm install -g @google/gemini-cli
curl -fsSL https://claude.ai/install.sh | bash

echo "--- 4. Installing Oh My Zsh ---"
if [ ! -d "$HOME/.oh-my-zsh" ]; then
    sh -c "$(curl -fsSL https://raw.githubusercontent.com/ohmyzsh/ohmyzsh/master/tools/install.sh)" "" --unattended
fi

echo "--- 5. Copying Shell Configs ---"
INFRA_DIR="/workspace/.dev-infra"
cp "$INFRA_DIR/configs/zshrc" /root/.zshrc
cp "$INFRA_DIR/configs/tmux.conf" /root/.tmux.conf

echo "--- 6. Installing Docker CLI (for DooD) ---"
if ! command -v docker > /dev/null; then
    curl -fsSL https://get.docker.com | bash
fi

echo "--- 7. Configuring SSH (Port 2222) ---"
mkdir -p /var/run/sshd
mkdir -p /root/.ssh
chmod 700 /root/.ssh

# Copy authorized_keys from host if available and container has none
if [ ! -s /root/.ssh/authorized_keys ] && [ -f /host_root/root/.ssh/authorized_keys ]; then
    cp /host_root/root/.ssh/authorized_keys /root/.ssh/authorized_keys
    chmod 600 /root/.ssh/authorized_keys
fi

sed -i 's/^#\?Port .*/Port 2222/' /etc/ssh/sshd_config
sed -i 's/^#\?PermitRootLogin .*/PermitRootLogin prohibit-password/' /etc/ssh/sshd_config
sed -i 's/^#\?PubkeyAuthentication .*/PubkeyAuthentication yes/' /etc/ssh/sshd_config

# Set default shell to zsh
chsh -s /usr/bin/zsh root 2>/dev/null || true

echo "--- 8. Starting SSH Daemon ---"
exec /usr/sbin/sshd -D
