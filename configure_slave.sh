#!/bin/bash

# Ensure the script exits if any command fails
set -e

# Variables
KEY_PATH="nass.pem"
REMOTE_USER="ubuntu"
REMOTE_DEST="/home/ubuntu"

# Check if all 6 args are provided
if [ -z "$1" ] || [ -z "$2" ] || [ -z "$3" ] || [ -z "$4" ] || [ -z "$5" ] || [ -z "$6" ]; then
  echo "Usage: ./configure_manager.sh <part1> <part2> <part3> <part4>"
  exit 1
fi

# Step 2: SSH into the EC2 instance and install necessary packages
echo "Connecting to the instance and setting it up..."
ssh -i "$KEY_PATH" -o StrictHostKeyChecking=no $REMOTE_USER@ec2-${1}-${2}-${3}-${4}.compute-1.amazonaws.com << EOF
    ./mysql_slave.sh $5 $6
EOF
echo "Deployment complete!"
