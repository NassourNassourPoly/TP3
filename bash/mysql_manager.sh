#!/bin/bash

# Variables
MYSQL_ROOT_PASSWORD=""  # Change to your root password
REPLICATION_USER="replicator"
REPLICATION_PASSWORD=""  # Change to a secure password

# Update and install MySQL
echo "Updating packages and installing MySQL..."
sudo apt-get update && sudo apt-get install -y mysql-server

# Configure MySQL for replication
echo "Configuring MySQL for replication..."
sudo sed -i '/\[mysqld\]/a \
server-id = 1\n\
log_bin = /var/log/mysql/mysql-bin.log\n\
binlog_do_db = sakila' /etc/mysql/mysql.conf.d/mysqld.cnf

# Restart MySQL to apply changes
echo "Restarting MySQL..."
sudo systemctl restart mysql

# Create the replication user
echo "Setting up replication user..."
sudo mysql -u root -p="$MYSQL_ROOT_PASSWORD" -e "
CREATE USER '$REPLICATION_USER'@'%' IDENTIFIED BY '$REPLICATION_PASSWORD';
GRANT REPLICATION SLAVE ON *.* TO '$REPLICATION_USER'@'%';
FLUSH PRIVILEGES;
SHOW MASTER STATUS;
"

echo "Master setup complete. Note down the File and Position values from the SHOW MASTER STATUS output."
