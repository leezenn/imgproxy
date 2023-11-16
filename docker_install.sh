#!/bin/bash

function display_help {
    echo "Usage: $0 [option...]"
    echo
    echo "   -f     Force reinstall Docker without checking"
    echo "   -c     Run check at the end"
    echo "   -h     Display help"
    exit 1
}

force_reinstall=false
run_check=false

while getopts 'fch' flag; do
    case "${flag}" in
        f) force_reinstall=true ;;
        c) run_check=true ;;
        h) display_help ;;
        *) display_help ;;
    esac
done

# Check Docker installation if not forcing reinstall
if ! $force_reinstall; then
    if command -v docker &> /dev/null; then
        echo "Docker is already installed. Use -f to force reinstall."
        exit 0
    fi
fi

# Uninstall previous Docker installations
for pkg in docker.io docker-doc docker-compose podman-docker containerd runc; do
    sudo apt-get remove -y $pkg
done

# Set up the repository
sudo apt-get update
sudo apt-get install -y ca-certificates curl gnupg

sudo install -m 0755 -d /etc/apt/keyrings
curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo gpg --dearmor -o /etc/apt/keyrings/docker.gpg
sudo chmod a+r /etc/apt/keyrings/docker.gpg

# Add Docker's official GPG key
echo \
  "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.gpg] https://download.docker.com/linux/ubuntu \
  $(. /etc/os-release && echo "$VERSION_CODENAME") stable" | \
  sudo tee /etc/apt/sources.list.d/docker.list > /dev/null

# Install Docker Engine
sudo apt-get update
sudo apt-get install -y docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin

# Check Docker installation
if $run_check; then
    sudo docker run hello-world
fi
