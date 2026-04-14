import subprocess
import os
import boto3
import shutil
import stat

#  CONFIGURATIONS 
SNS_TOPIC_ARN = "arn:aws:sns:us-east-1:263015886075:terraform-drift-detection"
S3_BUCKET_CODE = "terraform-main-config-bucket"  # Jahan main.tf rakhi hai
# -------------------------------------------

def lambda_handler(event, context):
    # 1. Path Setup
    # terraform zip file is here
    tf_bin = "/opt/bin/terraform"
    work_dir = "/tmp/terraform_project"
    

    #  Clean and Setup Working Directory
    if os.path.exists(work_dir):
        shutil.rmtree(work_dir)
    os.makedirs(work_dir)
    
    # 4. S3 se Terraform files download karna
    s3 = boto3.resource('s3')
    bucket = s3.Bucket(S3_BUCKET_CODE)
    print(f"Downloading files from {S3_BUCKET_CODE}...")
    for obj in bucket.objects.all():
        if obj.key.endswith('.tf') or obj.key.endswith('.tfvars'):
            target = os.path.join(work_dir, obj.key)
            os.makedirs(os.path.dirname(target), exist_ok=True)
            bucket.download_file(obj.key, target)

    os.chdir(work_dir)

    try:
        # 5. Terraform Init
        print("Initializing Terraform...")
        subprocess.run([tf_bin, "init", "-no-color", "-input=false"], check=True)

        # 6. Terraform Plan (Drift Check)
        print("Running Terraform Plan...")
        # detailed-exitcode: 0=No changes, 2=Drift, 1=Error
        result = subprocess.run(
            [tf_bin, "plan", "-detailed-exitcode", "-no-color", "-input=false"],
            capture_output=True, text=True
        )
        
        exit_code = result.returncode
        print(f"Exit Code: {exit_code}")

        if exit_code == 2:
            print("Drift Detected! Sending SNS Alert...")
            send_sns_alert(result.stdout)
        else:
            print("No drift detected. Infrastructure is in sync.")

    except subprocess.CalledProcessError as e:
        # Agar return code 2 hai toh ye error nahi balki drift hai
        if e.returncode == 2:
            send_sns_alert(e.stdout)
        else:
            print(f"Terraform Error: {e.stderr}")
            return {"status": "Error", "details": e.stderr}

    return {"status": "Execution Completed"}

def send_sns_alert(plan_output):
    sns = boto3.client('sns')
    sns.publish(
        TopicArn=SNS_TOPIC_ARN,
        Subject="🚨 Terraform Drift Alert!",
        Message=f"Manual change detected in AWS environment. Plan details:\n\n{plan_output[:2000]}"
    )
