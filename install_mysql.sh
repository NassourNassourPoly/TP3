#!/bin/bash

# Ensure the script exits if any command fails
set -e

# Variables
KEY_PATH="nass.pem"
REMOTE_USER="ubuntu"
REMOTE_DEST="/home/ubuntu"

# Check if all 4 IP parts are provided
if [ -z "$1" ] || [ -z "$2" ] || [ -z "$3" ] || [ -z "$4" ]; then
  echo "Usage: ./install_mysql.sh <part1> <part2> <part3> <part4>"
  exit 1
fi

echo "Transferring bash scripts file to the instance..."
scp -i "$KEY_PATH" -o StrictHostKeyChecking=no "./bash/mysql_manager.sh" $REMOTE_USER@${1}.${2}.${3}.${4}:$REMOTE_DEST
scp -i "$KEY_PATH" -o StrictHostKeyChecking=no "./bash/mysql_slave.sh" $REMOTE_USER@${1}.${2}.${3}.${4}:$REMOTE_DEST


echo "Connecting to the instance and setting it up..."
ssh -i "$KEY_PATH" -o StrictHostKeyChecking=no $REMOTE_USER@ec2-${1}-${2}-${3}-${4}.compute-1.amazonaws.com << EOF
    # Step 1: MySQL and sysbench installations
    sudo apt-get update && sudo apt-get install -y mysql-server sysbench dos2unix

    # Step 2: Sakila database install
    wget https://downloads.mysql.com/docs/sakila-db.tar.gz
    tar -xvzf sakila-db.tar.gz

    # Step 3: Sakila database setup
    cd sakila-db
    sudo mysql -u root <<MYSQL_CMD
SOURCE /home/ubuntu/sakila-db/sakila-schema.sql;
SOURCE /home/ubuntu/sakila-db/sakila-data.sql;
MYSQL_CMD

    # Step 4: Benchmarking with sysbench
    sudo sysbench /usr/share/sysbench/oltp_read_only.lua --mysql-db=sakila --mysql-user="root" --mysql-password="" prepare
    sudo sysbench /usr/share/sysbench/oltp_read_only.lua --mysql-db=sakila --mysql-user="root" --mysql-password="" run > /home/ubuntu/sysbench_${1}-${2}-${3}-${4}.txt 2>&1

    # Step 5: Preparing replicated cluster
    cd /home/ubuntu
    dos2unix ./mysql_manager.sh
    dos2unix ./mysql_slave.sh
    chmod +x ./mysql_manager.sh
    chmod +x ./mysql_slave.sh
EOF

scp -i "$KEY_PATH" -o StrictHostKeyChecking=no "$REMOTE_USER@${1}.${2}.${3}.${4}:/home/ubuntu/sysbench_${1}-${2}-${3}-${4}.txt" results

echo "Deployment complete!"
