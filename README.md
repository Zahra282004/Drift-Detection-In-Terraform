# Drift-Detection-In-Terraform

An automated, serverless solution to detect **infrastructure drift** in Terraform-managed cloud environments using AWS Lambda, Amazon S3, and Amazon SNS.


## Overview
In production environments, manual changes made directly via the AWS Console can cause state files and reality to go out of sync (known as *infrastructure drift*). This project provides a serverless approach to continuously monitor and alert your team when drift occurs.

## How It Works:
1. **Configuration Storage:** Your Terraform configuration files and remote S3 backend settings are stored in an Amazon S3 bucket so they are accessible to the Lambda function.
2. **Initialization:** The AWS Lambda function pulls these files into a temporary execution workspace and runs `terraform init` to configure the backend state and plugins.
3. **Plan & Detect:** The function runs `terraform plan` to compare the live cloud infrastructure against the saved state file.
4. **Automated Alerting:** If `terraform plan` detects any differences (drift), it returns a specific exit code (`2`), which instantly triggers an **Amazon SNS** alert to notify your team of manual tweaks or unauthorized changes.


### 1. Prerequisites

* An AWS Account with permissions to create Lambda functions, S3 buckets, and SNS topics.
* Terraform installed locally (for initial configuration setup).
* Python 3.x (for writing/testing the Lambda function).

### 2. S3 Bucket Setup

* Create an S3 bucket to store your Terraform configuration files (and optionally your remote backend state).
* Upload your `.tf` files to this bucket.

### 3. Lambda Function Configuration

* Package your Lambda function (`lambda_function.py`) along with a compatible Terraform binary layer (or include the binary in your deployment package).
* Set the necessary environment variables in AWS Lambda (e.g., S3 bucket names, SNS Topic ARN, region).
* Grant the Lambda execution role appropriate permissions:
* Read/Write access to the configuration S3 bucket and state backend.
* Permission to publish messages to the **Amazon SNS** topic.


### 4. AWS SNS Topic Setup

* Create an SNS Topic (e.g., `terraform-drift-alerts`).
* Subscribe your email address, Slack webhook, or PagerDuty endpoint to the topic to receive notifications.


## 💡 Usage

* Once deployed, you can trigger the Lambda function manually via the AWS Console/CLI or automate it using an **Amazon EventBridge (CloudWatch Events)** schedule (e.g., run every 12 hours or daily).
* If drift is detected, you will receive an SNS notification containing details of the changes so your team can reconcile them back into your codebase.
<img width="495" height="308" alt="image" src="https://github.com/user-attachments/assets/bbd02bec-511d-409c-9c99-2a6eb107af9a" />
<img width="353" height="62" alt="image" src="https://github.com/user-attachments/assets/5022b71a-829c-4f39-88f4-a692903e6ab4" />



