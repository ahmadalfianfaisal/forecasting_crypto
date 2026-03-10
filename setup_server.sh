#!/bin/bash
# Setup script untuk deployment awal di server

echo "=== Setup Forecast Vibecoding Application ==="

# Update sistem
echo "Updating system packages..."
sudo apt update && sudo apt upgrade -y

# Install git dan python
echo "Installing Git and Python..."
sudo apt install -y git python3 python3-pip python3-venv

# Install tmux
echo "Installing Tmux..."
sudo apt install -y tmux

# Clone repository jika belum ada
if [ ! -d "forecast-vibecoding" ]; then
    echo "Cloning repository..."
    git clone https://github.com/[username]/[repo-name].git forecast-vibecoding
else
    echo "Repository already exists, updating..."
    cd forecast-vibecoding
    git pull
    cd ..
fi

# Masuk ke direktori proyek
cd forecast-vibecoding

# Setup virtual environment
echo "Setting up virtual environment..."
if [ ! -d "venv" ]; then
    python3 -m venv venv
fi

# Activate virtual environment
source venv/bin/activate

# Install dependencies
echo "Installing dependencies..."
pip install --upgrade pip
pip install -r requirements.txt

# Buat file konfigurasi jika belum ada
if [ ! -f ".env" ]; then
    echo "# Environment variables" > .env
    echo "# Add your environment variables here" >> .env
fi

echo "Setup completed!"
echo "To start the application and scheduler, run:"
echo "chmod +x start_tmux_sessions.sh"
echo "./start_tmux_sessions.sh"