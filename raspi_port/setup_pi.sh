#!/bin/bash
echo "Setting up Raspberry Pi Environment for Raksha Simulator..."

# Install system dependencies (for audio and serial)
sudo apt-get update
sudo apt-get install -y python3-dev python3-pip python3-venv portaudio19-dev libatlas-base-dev

# Set up virtual environment
python3 -m venv venv
source venv/bin/activate

# Install python dependencies
pip install -r requirements_pi.txt

echo "Setup complete! Run ./start_pi.sh to start the API."
