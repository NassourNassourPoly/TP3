#!/bin/bash

# Ensure the script exits if any command fails
set -e

# Variables
KEY_PATH="nass.pem"
LOCAL_FILE_PATH="./main_fastapi.py"
REMOTE_USER="ubuntu"
REMOTE_DEST="/home/ubuntu"

# Check if all 4 IP parts are provided
if [ -z "$1" ] || [ -z "$2" ] || [ -z "$3" ] || [ -z "$4" ] || [ -z "$5" ] || [ -z "$6" ] || [ -z "$7" ]; then
  echo "Usage: ./deploy_fastapi.sh <part1> <part2> <part3> <part4>"
  exit 1
fi

export MANAGER_IP=$5
export WORKER1_IP=$6
export WORKER2_IP=$7

# Step 1: Copy the FastAPI script to the EC2 instance
echo "Transferring FastAPI file to the instance..."
scp -i "$KEY_PATH" -o StrictHostKeyChecking=no "$LOCAL_FILE_PATH" $REMOTE_USER@${1}.${2}.${3}.${4}:$REMOTE_DEST


# # Step 2: SSH into the EC2 instance and install necessary packages
echo "Connecting to the instance and setting it up..."
ssh -i "$KEY_PATH" -o StrictHostKeyChecking=no $REMOTE_USER@ec2-${1}-${2}-${3}-${4}.compute-1.amazonaws.com << EOF
    sudo apt-get update && sudo apt-get upgrade -y 
    sudo apt-get install python3 python3-pip python3-venv -y 
    python3 -m venv venv
    source venv/bin/activate
    pip install mysql-connector-python uvicorn fastapi

    # Export environment variables for the session
    export MANAGER_IP=$MANAGER_IP
    export WORKER1_IP=$WORKER1_IP
    export WORKER2_IP=$WORKER2_IP

#   # Step 3: Run the FastAPI application in the background
nohup uvicorn main_fastapi:app --host 0.0.0.0 --port 8000 > fastapi.log 2>&1 &
EOF

echo "Deployment complete!"