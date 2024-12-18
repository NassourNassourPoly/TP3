import subprocess
from time import sleep
import time
import json
import concurrent.futures
from create_ec2_instance import create_ec2_instance
import os
import benchmarking
import asyncio
import create_security_group
import shortuuid

# All these configuration scripts are used to run bash scripts with different arguments
def configure_routing(ip_address, route_ip):
    ip_parts = ip_address.split('.')
    git_bash_path = "C:/Program Files/Git/bin/bash.exe"

    try:
        # Pass manager_private_ip and id as additional arguments to the script
        result = subprocess.run(
            [git_bash_path, "./install_routing.sh", *ip_parts, route_ip], 
            check=True
        )
    except subprocess.CalledProcessError as e:
        print(f"Error during deployment for {ip_address}: {e.stderr}")

def configure_proxy(ip_address, manager_ip, worker1_ip, worker2_ip):
    ip_parts = ip_address.split('.')
    git_bash_path = "C:/Program Files/Git/bin/bash.exe"

    try:
        # Pass manager_private_ip and id as additional arguments to the script
        result = subprocess.run(
            [git_bash_path, "./install_fastapi.sh", *ip_parts, manager_ip, worker1_ip, worker2_ip, str(id)], 
            check=True
        )
    except subprocess.CalledProcessError as e:
        print(f"Error during deployment for {ip_address}: {e.stderr}")

def configure_slave(ip_address, manager_private_ip, id, file, position):
    ip_parts = ip_address.split('.')
    git_bash_path = "C:/Program Files/Git/bin/bash.exe"

    try:
        # Pass manager_private_ip and id as additional arguments to the script
        result = subprocess.run(
            [git_bash_path, "./configure_slave.sh", *ip_parts, manager_private_ip, str(id), file, str(position)], 
            check=True
        )
    except subprocess.CalledProcessError as e:
        print(f"Error during deployment for {ip_address}: {e.stderr}")

def run_bash(ip_address, bash_file_name):
    ip_parts = ip_address.split('.')
    git_bash_path = "C:/Program Files/Git/bin/bash.exe"

    try:
        result = subprocess.run([git_bash_path, bash_file_name, *ip_parts], check=True)
    except subprocess.CalledProcessError as e:
        print(f"Error during deployment for {ip_address}: {e.stderr}")

def run_bash_concurrently(ip_addresses, bash_file_name):
    # Use ThreadPoolExecutor for running tasks concurrently
    with concurrent.futures.ThreadPoolExecutor(max_workers=9) as executor:
        # Submit all deployments to run concurrently
        futures = [executor.submit(run_bash, ip, bash_file_name) for ip in ip_addresses]
        
        # Wait for all deployments to finish and handle any exceptions
        for future in concurrent.futures.as_completed(futures):
            try:
                future.result()
            except Exception as exc:
                print(f"Deployment generated an exception: {exc}")

def wait_for_deployment():
    print("Deploying to instance in 15...")
    sleep(5)

    print("Deploying to instance in 10...")
    sleep(5)

    print("Deploying to instance in 5...")
    sleep(5)

def main():
    start = time.time()

    # Load the JSON file
    with open('AWS_creds.json', 'r') as file:
        creds = json.load(file)

    key_name = creds['key_name']
    vpc_id = creds['vpc_id']

    print("Creating a security group...")
    security_group_id = create_security_group.create_security_group(shortuuid.uuid(), 'Security group for EC2 instances', vpc_id)
    # security_group_id = "sg-0392d0f35327b6529"
    if not security_group_id:
        print("Failed to create security group. Exiting.")
        return

    # Create 3 t2.micro instances
    print("Creating one t2.micro instance...")
    micro_instances = create_ec2_instance('t2.micro', 3, key_name, security_group_id)
    
    # Combine the ip address values
    instance_public_ips = [instance.public_ip_address for instance in micro_instances]
    instance_private_ips = [instance.private_ip_address for instance in micro_instances]


    wait_for_deployment()

    print("Installing mysql standalone for each instance...")
    run_bash_concurrently(instance_public_ips, "./install_mysql.sh")

    print("Configuring MySQL cluster")
    run_bash(instance_public_ips[0], "./configure_manager.sh")
    subprocess.run(f'scp -i "nass.pem" "ubuntu@{instance_public_ips[0]}:/home/ubuntu/master_status.json" results')

    with open('results/master_status.json', 'r') as file:
        master_status = json.load(file)

    configure_slave(instance_public_ips[1], instance_private_ips[0], 2, master_status["File"], master_status["Position"])
    configure_slave(instance_public_ips[2], instance_private_ips[0], 3, master_status["File"], master_status["Position"])

    print("Configuring proxy")
    proxy_instance = create_ec2_instance('t2.large', 1, key_name, security_group_id)
    wait_for_deployment()
    configure_proxy(proxy_instance[0].public_ip_address,
                    instance_public_ips[0], 
                    instance_public_ips[1], 
                    instance_public_ips[2])

    print("Configuring trusted host")
    trusted_host_instance = create_ec2_instance('t2.large', 1, key_name, security_group_id)
    wait_for_deployment()
    configure_routing(trusted_host_instance[0].public_ip_address,
                      proxy_instance[0].public_ip_address)
    
    print("Configuring gatekeeper")
    gatekeeper_instance = create_ec2_instance('t2.large', 1, key_name, security_group_id)
    wait_for_deployment()
    configure_routing(gatekeeper_instance[0].public_ip_address,
                      trusted_host_instance[0].public_ip_address)
    
    os.environ["GATEKEEPER_IP"] = gatekeeper_instance[0].public_ip_address
    asyncio.run(benchmarking.main())

    end = time.time()
    print(f"SQL cluster instances: {instance_public_ips}")
    print(f"File, Position = {master_status["File"]}, {master_status["Position"]}")
    print(f"Proxy: {proxy_instance[0].public_ip_address}")
    print(f"Trusted Host: {trusted_host_instance[0].public_ip_address}")
    print(f"Gatekeeper: {gatekeeper_instance[0].public_ip_address}")

    print(f"Time taken to run the code was {end-start} seconds")

if __name__ == "__main__":
    main()
