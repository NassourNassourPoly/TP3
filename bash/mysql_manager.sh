#!/bin/bash

# Variables
MYSQL_ROOT_PASSWORD=""  # Change to your root password
REPLICATION_USER="replicator"
REPLICATION_PASSWORD=""  # Change to a secure password
STATUS_FILE="master_status.json"  # File to save master status

# Configure MySQL for replication
echo "Configuring MySQL for replication..."

# Remove any existing bind-address and mysqlx-bind-address settings
echo "Removing any previous bind-address and mysqlx-bind-address settings..."
sudo sed -i '/^bind-address/d' /etc/mysql/mysql.conf.d/mysqld.cnf
sudo sed -i '/^mysqlx-bind-address/d' /etc/mysql/mysql.conf.d/mysqld.cnf

# Update bind-address to 0.0.0.0 to allow external connections
echo "Setting bind-address to 0.0.0.0..."
sudo sed -i '/\[mysqld\]/a \
bind-address = 0.0.0.0' /etc/mysql/mysql.conf.d/mysqld.cnf

# Update mysqlx-bind-address to 0.0.0.0 to allow external connections for MySQL X protocol (if applicable)
echo "Setting mysqlx-bind-address to 0.0.0.0..."
sudo sed -i '/\[mysqld\]/a \
mysqlx-bind-address = 0.0.0.0' /etc/mysql/mysql.conf.d/mysqld.cnf

# Add replication-specific configuration
echo "Adding replication configuration..."
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
GRANT ALL PRIVILEGES ON sakila.* TO '$REPLICATION_USER'@'%';
FLUSH PRIVILEGES;
SHOW MASTER STATUS;
"

# Capture and save the SHOW MASTER STATUS output in JSON format
echo "Capturing master status and saving to $STATUS_FILE..."
MASTER_STATUS=$(sudo mysql -u root -p="$MYSQL_ROOT_PASSWORD" -e "SHOW MASTER STATUS;" \
    --batch --skip-column-names | awk '{print "{\"File\": \"" $1 "\", \"Position\": " $2 "}"}')

echo "$MASTER_STATUS" > "$STATUS_FILE"

echo "Master setup complete. Master status saved to $STATUS_FILE."
