import boto3
import time

# Initialize AWS clients
ec2 = boto3.client('ec2', region_name='us-east-1')
rds = boto3.client('rds', region_name='us-east-1')
s3 = boto3.client('s3', region_name='us-east-1')

def create_infrastructure():
    """
    Automates the creation of the multi-tier resource stack.
    """
    print("Initializing Infrastructure Deployment...")

    # 1. Network setup (VPC and basic networking)
    vpc = ec2.create_vpc(CidrBlock='10.0.0.0/16')
    vpc_id = vpc['Vpc']['VpcId']
    ec2.create_tags(
        Resources=[vpc_id],
        Tags=[{'Key': 'Name', 'Value': 'MultiTierVPC'}]
    )
    print(f"VPC Created: {vpc_id}")

    # 2. Storage (S3 Bucket for assets)
    bucket_name = f"assets-{int(time.time())}"
    s3.create_bucket(Bucket=bucket_name)
    print(f"S3 Bucket Created: {bucket_name}")

    # 3. Database (RDS MySQL Instance)
    print("Provisioning RDS Instance...")
    db_instance = rds.create_db_instance(
        DBInstanceIdentifier='cloud-app-db',
        AllocatedStorage=20,
        DBInstanceClass='db.t3.micro',
        Engine='mysql',
        MasterUsername='admin',
        MasterUserPassword='SecurePassword123!', # In production, use Secrets Manager
        VpcSecurityGroupIds=[],
        PubliclyAccessible=False
    )
    db_id = db_instance['DBInstance']['DBInstanceIdentifier']
    print(f"RDS Instance created: {db_id}")

    # 4. Compute Security Group
    sg = ec2.create_security_group(
        GroupName='WebServerSG',
        Description='Allow HTTP access',
        VpcId=vpc_id
    )
    sg_id = sg['GroupId']
    ec2.authorize_security_group_ingress(
        GroupId=sg_id,
        IpProtocol='tcp',
        FromPort=80,
        ToPort=80,
        CidrIp='0.0.0.0/0'
    )
    print(f"Security Group configured: {sg_id}")

    # 5. Launch Application Instance
    # Uses IAM Instance Profile for security instead of static credentials
    instance = ec2.run_instances(
        ImageId='ami-0c55b159cbfafe1f0', # Amazon Linux 2
        InstanceType='t2.micro',
        MinCount=1,
        MaxCount=1,
        SecurityGroupIds=[sg_id]
    )
    instance_id = instance['Instances'][0]['InstanceId']
    print(f"EC2 Instance launched: {instance_id}")

    print("\nInfrastructure deployment stack complete.")

if __name__ == "__main__":
    create_infrastructure()
