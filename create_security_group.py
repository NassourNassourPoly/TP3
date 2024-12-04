import boto3
from botocore.exceptions import ClientError

# Initialize EC2 client
ec2_client = boto3.client('ec2')

def create_security_group(group_name, description, vpc_id):
    """
    Creates a security group and sets up rules for all inbound and outbound traffic.
    
    Parameters:
        group_name (str): The name of the security group.
        description (str): Description of the security group.
        vpc_id (str): The VPC ID where the security group will be created.
    
    Returns:
        str: The security group ID.
    """
    try:
        # Create the security group
        response = ec2_client.create_security_group(
            GroupName=group_name,
            Description=description,
            VpcId=vpc_id
        )
        security_group_id = response['GroupId']
        print(f'Security Group {group_name} created with ID: {security_group_id}')

        # Add inbound rules (all traffic)
        ec2_client.authorize_security_group_ingress(
            GroupId=security_group_id,
            IpPermissions=[
                {
                    'IpProtocol': '-1',  # All protocols
                    'FromPort': -1,     # All ports
                    'ToPort': -1,       # All ports
                    'IpRanges': [{'CidrIp': '0.0.0.0/0'}]  # Open to all IPs
                }
            ]
        )

        return security_group_id

    except ClientError as e:
        print(f"Error creating security group: {e}")
        return None
