import boto3
import boto3.session
from botocore.exceptions import ClientError

# Initialiser la ressource EC2 avec boto3 pour la région us-east-1
ec2 = boto3.resource('ec2', region_name='us-east-1')

def create_ec2_instance(instance_type, count, key_name, security_group_id):
    try:
        # Créer des instances EC2 avec les paramètres donnés
        instances = ec2.create_instances(
            ImageId='ami-0e86e20dae9224db8',  # ID de l'image AMI
            InstanceType=instance_type,       # Type d'instance (par ex. t2.micro, t2.large)
            KeyName=key_name,                 # Clé SSH pour accéder à l'instance
            MinCount=1,                       # Nombre minimum d'instances à créer
            MaxCount=count,                   # Nombre maximum d'instances à créer
            SecurityGroupIds=[security_group_id],  # ID du groupe de sécurité à associer
            TagSpecifications=[
                {
                    'ResourceType': 'instance', 
                    'Tags': [{'Key': 'InstanceTest', 'Value': f'{instance_type} instance'}]  
                }
            ]
        )
    except ClientError as e:
        # Gérer les erreurs liées à la création des instances EC2
        print(f"Error creating EC2 instance(s): {e}")
        return []  # Retourner une liste vide si la création échoue
    
    # Boucle pour chaque instance créée afin de surveiller son démarrage
    for instance in instances:
        try:
            print(f'Waiting for instance {instance.id} to be running...')
            instance.wait_until_running()  # Attendre que l'instance soit en état "running"
            instance.reload()  # Recharger les informations de l'instance
            print(f'Instance {instance.id} is now running at {instance.public_ip_address}')
        except ClientError as e:
            # Gérer les erreurs lors de l'attente du démarrage de l'instance
            print(f"Error waiting for instance {instance.id} to be running: {e}")
    
    return instances  # Retourner les instances créées et démarrées

