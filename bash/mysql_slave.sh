#!/bin/bash

# Variables
MASTER_IP="$1"  # Replace with the master node's private IP
MYSQL_ROOT_PASSWORD=""  # Change to your root password
REPLICATION_USER="replicator"
REPLICATION_PASSWORD=""  # Change to the password set on the master
SERVER_ID=$2  # Pass a unique server ID as a script argument
MASTER_LOG_FILE="mysql-bin.000001"  # Replace with the File from SHOW MASTER STATUS
MASTER_LOG_POS="778"  # Replace with the Position from SHOW MASTER STATUS

# Check if all 4 IP parts are provided
if [ -z "$1" ] || [ -z "$2" ]; then
  echo "Usage: ./install_mysql.sh <part1> <part2> <part3> <part4>"
  exit 1
fi

# Update and install MySQL
echo "Updating packages and installing MySQL..."
sudo apt-get update && sudo apt-get install -y mysql-server

# Configure MySQL for replication
echo "Configuring MySQL for replication..."
sudo sed -i "/\[mysqld\]/a \
server-id = $SERVER_ID\n\
relay_log = /var/log/mysql/mysql-relay-bin.log" /etc/mysql/mysql.conf.d/mysqld.cnf

# Restart MySQL to apply changes
echo "Restarting MySQL..."
sudo systemctl restart mysql

# Set up replication
echo "Setting up replication..."
sudo mysql -u root -p="$MYSQL_ROOT_PASSWORD" -e "
CHANGE MASTER TO
    MASTER_HOST = '$MASTER_IP',
    MASTER_USER = '$REPLICATION_USER',
    MASTER_PASSWORD = '$REPLICATION_PASSWORD',
    MASTER_LOG_FILE = '$MASTER_LOG_FILE',
    MASTER_LOG_POS = $MASTER_LOG_POS;
START SLAVE;
SHOW SLAVE STATUS\G
"

echo "Worker setup complete. Check the output to ensure replication is running correctly."
