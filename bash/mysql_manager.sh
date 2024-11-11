#!/bin/bash

# Variables
MYSQL_ROOT_PASSWORD=""  # Change to your root password
REPLICATION_USER="replicator"
REPLICATION_PASSWORD=""  # Change to a secure password

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
CREATE USER 'remote_admin'@'%' IDENTIFIED BY '';
GRANT ALL PRIVILEGES ON sakila.* TO 'remote_admin'@'%';
FLUSH PRIVILEGES;
SHOW MASTER STATUS;
"

echo "Master setup complete. Note down the File and Position values from the SHOW MASTER STATUS output."
