import subprocess
from time import sleep
import json
import concurrent.futures
from create_ec2_instance import create_ec2_instance


def deploy_to_instance(ip_address):
    ip_parts = ip_address.split('.')
    git_bash_path = "C:/Program Files/Git/bin/bash.exe"

    try:
        print(f"BEGIN SUBPROCESS RUN for {ip_address}")
        result = subprocess.run([git_bash_path, "./install_mysql.sh", *ip_parts], check=True)
        print(f"Deployment successful for {ip_address}: {result.stdout}")
    except subprocess.CalledProcessError as e:
        print(f"Error during deployment for {ip_address}: {e.stderr}")

def deploy_to_instances_concurrently(ip_addresses):
    # Use ThreadPoolExecutor for running tasks concurrently
    with concurrent.futures.ThreadPoolExecutor(max_workers=9) as executor:
        # Submit all deployments to run concurrently
        futures = [executor.submit(deploy_to_instance, ip) for ip in ip_addresses]
        
        # Wait for all deployments to finish and handle any exceptions
        for future in concurrent.futures.as_completed(futures):
            try:
                future.result()
            except Exception as exc:
                print(f"Deployment generated an exception: {exc}")

def main():
    # Load the JSON file
    with open('AWS_creds.json', 'r') as file:
        creds = json.load(file)

    key_name = creds['key_name']

    print("Creating a security group...")
    security_group_id = "sg-0392d0f35327b6529"

    if not security_group_id:
        print("Failed to create security group. Exiting.")
        return

    # Create one t2.micro and one t2.large instance
    print("Creating one t2.micro instance...")
    micro_instances = create_ec2_instance('t2.micro', 1, key_name, security_group_id)
    
    # Combine the instance IDs from both instance types
    instance_ips = [instance.public_ip_address for instance in micro_instances]

    print("Deploying to instance in 15...")
    sleep(5)

    print("Deploying to instance in 10...")
    sleep(5)

    print("Deploying to instance in 5...")
    sleep(5)

    print("Deploying to instance...")
    deploy_to_instance(instance_ips[0])
    print(f"Completed for {instance_ips[0]}")

if __name__ == "__main__":
    main()
