#!/usr/bin/env python3
"""Deploy T-Developer AWS Infrastructure for Phase 2.

This script creates all necessary AWS resources for T-Developer:
- DynamoDB tables
- S3 buckets
- SQS queues
- Lambda functions
- API Gateway
"""

import json
import time

import boto3

# AWS Configuration
AWS_REGION = "us-east-1"
AWS_ACCOUNT_ID = "036284794745"

# Resource names
DYNAMODB_TABLES = {
    "t-developer-evolution-state": {
        "AttributeDefinitions": [
            {"AttributeName": "id", "AttributeType": "S"},
            {"AttributeName": "timestamp", "AttributeType": "N"},
        ],
        "KeySchema": [
            {"AttributeName": "id", "KeyType": "HASH"},
            {"AttributeName": "timestamp", "KeyType": "RANGE"},
        ],
        "BillingMode": "PAY_PER_REQUEST",
    },
    "t-developer-patterns": {
        "AttributeDefinitions": [
            {"AttributeName": "pattern_id", "AttributeType": "S"},
            {"AttributeName": "category", "AttributeType": "S"},
        ],
        "KeySchema": [{"AttributeName": "pattern_id", "KeyType": "HASH"}],
        "GlobalSecondaryIndexes": [
            {
                "IndexName": "category-index",
                "KeySchema": [{"AttributeName": "category", "KeyType": "HASH"}],
                "Projection": {"ProjectionType": "ALL"},
            }
        ],
        "BillingMode": "PAY_PER_REQUEST",
    },
    "t-developer-metrics": {
        "AttributeDefinitions": [
            {"AttributeName": "metric_id", "AttributeType": "S"},
            {"AttributeName": "timestamp", "AttributeType": "N"},
        ],
        "KeySchema": [
            {"AttributeName": "metric_id", "KeyType": "HASH"},
            {"AttributeName": "timestamp", "KeyType": "RANGE"},
        ],
        "BillingMode": "PAY_PER_REQUEST",
    },
    "t-developer-agent-registry": {
        "AttributeDefinitions": [{"AttributeName": "agent_id", "AttributeType": "S"}],
        "KeySchema": [{"AttributeName": "agent_id", "KeyType": "HASH"}],
        "BillingMode": "PAY_PER_REQUEST",
    },
}

S3_BUCKETS = [
    f"t-developer-artifacts-{AWS_ACCOUNT_ID}",
    f"t-developer-code-{AWS_ACCOUNT_ID}",
    f"t-developer-logs-{AWS_ACCOUNT_ID}",
]

SQS_QUEUES = ["agent-squad-tasks", "agent-squad-dlq"]


def create_dynamodb_tables():
    """Create DynamoDB tables."""
    dynamodb = boto3.client("dynamodb", region_name=AWS_REGION)

    for table_name, config in DYNAMODB_TABLES.items():
        try:
            print(f"Creating DynamoDB table: {table_name}")

            # Check if table exists
            try:
                dynamodb.describe_table(TableName=table_name)
                print(f"  Table {table_name} already exists, skipping...")
                continue
            except dynamodb.exceptions.ResourceNotFoundException:
                pass

            # Create table
            response = dynamodb.create_table(TableName=table_name, **config)

            # Wait for table to be active
            waiter = dynamodb.get_waiter("table_exists")
            waiter.wait(TableName=table_name)

            print(f"  ✅ Table {table_name} created successfully")

        except Exception as e:
            print(f"  ❌ Error creating table {table_name}: {e}")


def create_s3_buckets():
    """Create S3 buckets."""
    s3 = boto3.client("s3", region_name=AWS_REGION)

    for bucket_name in S3_BUCKETS:
        try:
            print(f"Creating S3 bucket: {bucket_name}")

            # Check if bucket exists
            try:
                s3.head_bucket(Bucket=bucket_name)
                print(f"  Bucket {bucket_name} already exists, skipping...")
                continue
            except:
                pass

            # Create bucket
            if AWS_REGION == "us-east-1":
                s3.create_bucket(Bucket=bucket_name)
            else:
                s3.create_bucket(
                    Bucket=bucket_name, CreateBucketConfiguration={"LocationConstraint": AWS_REGION}
                )

            # Enable versioning
            s3.put_bucket_versioning(
                Bucket=bucket_name, VersioningConfiguration={"Status": "Enabled"}
            )

            # Enable encryption
            s3.put_bucket_encryption(
                Bucket=bucket_name,
                ServerSideEncryptionConfiguration={
                    "Rules": [{"ApplyServerSideEncryptionByDefault": {"SSEAlgorithm": "AES256"}}]
                },
            )

            print(f"  ✅ Bucket {bucket_name} created successfully")

        except Exception as e:
            print(f"  ❌ Error creating bucket {bucket_name}: {e}")


def create_sqs_queues():
    """Create SQS queues."""
    sqs = boto3.client("sqs", region_name=AWS_REGION)

    for queue_name in SQS_QUEUES:
        try:
            print(f"Creating SQS queue: {queue_name}")

            # Check if queue exists
            try:
                sqs.get_queue_url(QueueName=queue_name)
                print(f"  Queue {queue_name} already exists, skipping...")
                continue
            except:
                pass

            # Create queue with appropriate settings
            attributes = {
                "MessageRetentionPeriod": "1209600",  # 14 days
                "VisibilityTimeout": "300",  # 5 minutes
            }

            # DLQ gets special configuration
            if "dlq" in queue_name:
                attributes["MaximumMessageSize"] = "262144"  # 256 KB
            else:
                # Regular queue needs DLQ configuration
                attributes["RedrivePolicy"] = json.dumps(
                    {
                        "deadLetterTargetArn": f"arn:aws:sqs:{AWS_REGION}:{AWS_ACCOUNT_ID}:agent-squad-dlq",
                        "maxReceiveCount": 3,
                    }
                )

            response = sqs.create_queue(QueueName=queue_name, Attributes=attributes)

            print(f"  ✅ Queue {queue_name} created successfully")

        except Exception as e:
            print(f"  ❌ Error creating queue {queue_name}: {e}")


def create_lambda_function(function_name: str, handler: str, role_arn: str):
    """Create a Lambda function."""
    lambda_client = boto3.client("lambda", region_name=AWS_REGION)

    try:
        print(f"Creating Lambda function: {function_name}")

        # Check if function exists
        try:
            lambda_client.get_function(FunctionName=function_name)
            print(f"  Function {function_name} already exists, skipping...")
            return
        except:
            pass

        # Create basic Lambda code
        lambda_code = '''
import json

def lambda_handler(event, context):
    """Basic Lambda handler."""
    print(f"Received event: {json.dumps(event)}")

    return {
        'statusCode': 200,
        'body': json.dumps({
            'message': f'{context.function_name} executed successfully',
            'event': event
        })
    }
'''

        # Create deployment package
        import io
        import zipfile

        zip_buffer = io.BytesIO()
        with zipfile.ZipFile(zip_buffer, "w", zipfile.ZIP_DEFLATED) as zip_file:
            zip_file.writestr("lambda_function.py", lambda_code)

        # Create function
        response = lambda_client.create_function(
            FunctionName=function_name,
            Runtime="python3.9",
            Role=role_arn,
            Handler=handler,
            Code={"ZipFile": zip_buffer.getvalue()},
            Description=f"T-Developer {function_name}",
            Timeout=300,
            MemorySize=512,
            Environment={
                "Variables": {"T_DEVELOPER_REGION": AWS_REGION, "ENVIRONMENT": "production"}
            },
        )

        print(f"  ✅ Function {function_name} created successfully")

    except Exception as e:
        print(f"  ❌ Error creating function {function_name}: {e}")


def create_lambda_functions():
    """Create Lambda functions for T-Developer."""

    # First, create IAM role for Lambda
    iam = boto3.client("iam", region_name=AWS_REGION)

    role_name = "t-developer-lambda-role"

    try:
        # Check if role exists
        try:
            role = iam.get_role(RoleName=role_name)
            role_arn = role["Role"]["Arn"]
            print(f"Using existing IAM role: {role_arn}")
        except:
            # Create role
            print(f"Creating IAM role: {role_name}")

            trust_policy = {
                "Version": "2012-10-17",
                "Statement": [
                    {
                        "Effect": "Allow",
                        "Principal": {"Service": "lambda.amazonaws.com"},
                        "Action": "sts:AssumeRole",
                    }
                ],
            }

            response = iam.create_role(
                RoleName=role_name,
                AssumeRolePolicyDocument=json.dumps(trust_policy),
                Description="IAM role for T-Developer Lambda functions",
            )

            role_arn = response["Role"]["Arn"]

            # Attach policies
            policies = [
                "arn:aws:iam::aws:policy/service-role/AWSLambdaBasicExecutionRole",
                "arn:aws:iam::aws:policy/AmazonDynamoDBFullAccess",
                "arn:aws:iam::aws:policy/AmazonS3FullAccess",
                "arn:aws:iam::aws:policy/AmazonSQSFullAccess",
                "arn:aws:iam::aws:policy/AmazonBedrockFullAccess",
            ]

            for policy_arn in policies:
                iam.attach_role_policy(RoleName=role_name, PolicyArn=policy_arn)

            print(f"  ✅ IAM role created: {role_arn}")

            # Wait for role to propagate
            time.sleep(10)

        # Create Lambda functions
        functions = [
            ("t-developer-security-gate", "lambda_function.lambda_handler"),
            ("t-developer-quality-gate", "lambda_function.lambda_handler"),
            ("t-developer-test-gate", "lambda_function.lambda_handler"),
            ("t-developer-orchestrator", "lambda_function.lambda_handler"),
            ("t-developer-agentcore", "lambda_function.lambda_handler"),
        ]

        for function_name, handler in functions:
            create_lambda_function(function_name, handler, role_arn)

    except Exception as e:
        print(f"  ❌ Error in Lambda setup: {e}")


def main():
    """Main deployment function."""
    print("=" * 60)
    print("T-Developer AWS Infrastructure Deployment")
    print("=" * 60)
    print(f"Account: {AWS_ACCOUNT_ID}")
    print(f"Region: {AWS_REGION}")
    print("=" * 60)

    # Create DLQ first (needed by other queues)
    print("\n📦 Creating Dead Letter Queue...")
    sqs = boto3.client("sqs", region_name=AWS_REGION)
    try:
        sqs.create_queue(
            QueueName="agent-squad-dlq", Attributes={"MessageRetentionPeriod": "1209600"}
        )
        print("  ✅ DLQ created")
    except:
        print("  DLQ already exists")

    print("\n📊 Creating DynamoDB Tables...")
    create_dynamodb_tables()

    print("\n🗄️ Creating S3 Buckets...")
    create_s3_buckets()

    print("\n📨 Creating SQS Queues...")
    create_sqs_queues()

    print("\n⚡ Creating Lambda Functions...")
    create_lambda_functions()

    print("\n" + "=" * 60)
    print("✅ AWS Infrastructure Deployment Complete!")
    print("=" * 60)

    # Print resource summary
    print("\n📋 Resource Summary:")
    print(f"  • DynamoDB Tables: {len(DYNAMODB_TABLES)}")
    print(f"  • S3 Buckets: {len(S3_BUCKETS)}")
    print(f"  • SQS Queues: {len(SQS_QUEUES)}")
    print("  • Lambda Functions: 5")

    print("\n🔗 Next Steps:")
    print("  1. Configure Bedrock access")
    print("  2. Deploy actual Lambda code")
    print("  3. Set up API Gateway")
    print("  4. Configure monitoring")


if __name__ == "__main__":
    main()
