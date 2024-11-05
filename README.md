# LOG8415E
Step 1: Install requirements
python3 -m venv venv
.\venv\Scripts\activate
pip install -r requirements.txt

Step 2: create key pair
aws ec2 create-key-pair --key-name YOURKEYNAME --query 'KeyMaterial' --output text > YOURKEYNAME .pem

Step 3: Update variables in AWS_Creds.json
key_name, vpc_id and subnets

Step 4: Update variables in deploy_fastapi.sh
KEY_PATH and LOCAL_FILE_PATH

Step 6: Update /.aws/credentials variables
aws_access_key_id, aws_secret_access_key and aws_session_token

Step 7: (optional)
In the Main_Aws.py you might have to update the git_bash_path variable

Step 8: 
Assuming you're using Windows, open a git bash terminal and run the following command:
python Main_Aws.py