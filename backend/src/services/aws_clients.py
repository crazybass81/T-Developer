"""
AWS Service Clients Wrapper
Provides unified interface for AWS services
"""
import json
import logging
import os
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional

import boto3
from botocore.exceptions import ClientError

logger = logging.getLogger(__name__)


class DynamoDBClient:
    """DynamoDB client wrapper"""

    def __init__(self, region_name: str = None):
        self.region_name = region_name or os.getenv("AWS_REGION", "us-east-1")
        self.client = boto3.client("dynamodb", region_name=self.region_name)
        self.resource = boto3.resource("dynamodb", region_name=self.region_name)

    def put_item(self, table_name: str, item: Dict[str, Any]) -> bool:
        """Put item to DynamoDB table"""
        try:
            table = self.resource.Table(table_name)
            table.put_item(Item=item)
            return True
        except ClientError as e:
            logger.error(f"Error putting item to {table_name}: {e}")
            return False

    def get_item(self, table_name: str, key: Dict[str, Any]) -> Optional[Dict]:
        """Get item from DynamoDB table"""
        try:
            table = self.resource.Table(table_name)
            response = table.get_item(Key=key)
            return response.get("Item")
        except ClientError as e:
            logger.error(f"Error getting item from {table_name}: {e}")
            return None

    def query(
        self,
        table_name: str,
        key_condition: Dict,
        index_name: str = None,
        limit: int = None,
    ) -> List[Dict]:
        """Query DynamoDB table"""
        try:
            table = self.resource.Table(table_name)
            kwargs = {"KeyConditionExpression": key_condition}
            if index_name:
                kwargs["IndexName"] = index_name
            if limit:
                kwargs["Limit"] = limit

            response = table.query(**kwargs)
            return response.get("Items", [])
        except ClientError as e:
            logger.error(f"Error querying {table_name}: {e}")
            return []

    def update_item(self, table_name: str, key: Dict[str, Any], updates: Dict[str, Any]) -> bool:
        """Update item in DynamoDB table"""
        try:
            table = self.resource.Table(table_name)

            # Build update expression
            update_expr = "SET "
            expr_values = {}
            for idx, (k, v) in enumerate(updates.items()):
                update_expr += f"{k} = :val{idx}, "
                expr_values[f":val{idx}"] = v
            update_expr = update_expr.rstrip(", ")

            table.update_item(
                Key=key,
                UpdateExpression=update_expr,
                ExpressionAttributeValues=expr_values,
            )
            return True
        except ClientError as e:
            logger.error(f"Error updating item in {table_name}: {e}")
            return False

    def delete_item(self, table_name: str, key: Dict[str, Any]) -> bool:
        """Delete item from DynamoDB table"""
        try:
            table = self.resource.Table(table_name)
            table.delete_item(Key=key)
            return True
        except ClientError as e:
            logger.error(f"Error deleting item from {table_name}: {e}")
            return False


class S3Client:
    """S3 client wrapper"""

    def __init__(self, region_name: str = None):
        self.region_name = region_name or os.getenv("AWS_REGION", "us-east-1")
        self.client = boto3.client("s3", region_name=self.region_name)
        self.resource = boto3.resource("s3", region_name=self.region_name)

    def upload_file(
        self, file_path: str, bucket_name: str, object_key: str, metadata: Dict = None
    ) -> bool:
        """Upload file to S3"""
        try:
            extra_args = {}
            if metadata:
                extra_args["Metadata"] = metadata

            self.client.upload_file(file_path, bucket_name, object_key, ExtraArgs=extra_args)
            return True
        except ClientError as e:
            logger.error(f"Error uploading file to S3: {e}")
            return False

    def upload_data(
        self, data: bytes, bucket_name: str, object_key: str, content_type: str = None
    ) -> bool:
        """Upload data to S3"""
        try:
            kwargs = {"Body": data}
            if content_type:
                kwargs["ContentType"] = content_type

            self.client.put_object(Bucket=bucket_name, Key=object_key, **kwargs)
            return True
        except ClientError as e:
            logger.error(f"Error uploading data to S3: {e}")
            return False

    def download_file(self, bucket_name: str, object_key: str, file_path: str) -> bool:
        """Download file from S3"""
        try:
            self.client.download_file(bucket_name, object_key, file_path)
            return True
        except ClientError as e:
            logger.error(f"Error downloading file from S3: {e}")
            return False

    def get_object(self, bucket_name: str, object_key: str) -> Optional[bytes]:
        """Get object data from S3"""
        try:
            response = self.client.get_object(Bucket=bucket_name, Key=object_key)
            return response["Body"].read()
        except ClientError as e:
            logger.error(f"Error getting object from S3: {e}")
            return None

    def delete_object(self, bucket_name: str, object_key: str) -> bool:
        """Delete object from S3"""
        try:
            self.client.delete_object(Bucket=bucket_name, Key=object_key)
            return True
        except ClientError as e:
            logger.error(f"Error deleting object from S3: {e}")
            return False

    def list_objects(
        self, bucket_name: str, prefix: str = None, max_keys: int = 1000
    ) -> List[Dict]:
        """List objects in S3 bucket"""
        try:
            kwargs = {"Bucket": bucket_name, "MaxKeys": max_keys}
            if prefix:
                kwargs["Prefix"] = prefix

            response = self.client.list_objects_v2(**kwargs)
            return response.get("Contents", [])
        except ClientError as e:
            logger.error(f"Error listing objects in S3: {e}")
            return []

    def generate_presigned_url(
        self, bucket_name: str, object_key: str, expiration: int = 3600
    ) -> Optional[str]:
        """Generate presigned URL for S3 object"""
        try:
            url = self.client.generate_presigned_url(
                "get_object",
                Params={"Bucket": bucket_name, "Key": object_key},
                ExpiresIn=expiration,
            )
            return url
        except ClientError as e:
            logger.error(f"Error generating presigned URL: {e}")
            return None


class SecretsManagerClient:
    """Secrets Manager client wrapper"""

    def __init__(self, region_name: str = None):
        self.region_name = region_name or os.getenv("AWS_REGION", "us-east-1")
        self.client = boto3.client("secretsmanager", region_name=self.region_name)

    def get_secret(self, secret_name: str) -> Optional[Dict]:
        """Get secret value"""
        try:
            response = self.client.get_secret_value(SecretId=secret_name)
            secret_string = response.get("SecretString")
            if secret_string:
                return json.loads(secret_string)
            return None
        except ClientError as e:
            logger.error(f"Error getting secret {secret_name}: {e}")
            return None

    def create_secret(self, secret_name: str, secret_value: Dict) -> bool:
        """Create new secret"""
        try:
            self.client.create_secret(Name=secret_name, SecretString=json.dumps(secret_value))
            return True
        except ClientError as e:
            if e.response["Error"]["Code"] == "ResourceExistsException":
                return self.update_secret(secret_name, secret_value)
            logger.error(f"Error creating secret {secret_name}: {e}")
            return False

    def update_secret(self, secret_name: str, secret_value: Dict) -> bool:
        """Update existing secret"""
        try:
            self.client.update_secret(SecretId=secret_name, SecretString=json.dumps(secret_value))
            return True
        except ClientError as e:
            logger.error(f"Error updating secret {secret_name}: {e}")
            return False


class ParameterStoreClient:
    """Parameter Store client wrapper"""

    def __init__(self, region_name: str = None):
        self.region_name = region_name or os.getenv("AWS_REGION", "us-east-1")
        self.client = boto3.client("ssm", region_name=self.region_name)

    def get_parameter(self, parameter_name: str, with_decryption: bool = True) -> Optional[str]:
        """Get parameter value"""
        try:
            response = self.client.get_parameter(
                Name=parameter_name, WithDecryption=with_decryption
            )
            return response["Parameter"]["Value"]
        except ClientError as e:
            logger.error(f"Error getting parameter {parameter_name}: {e}")
            return None

    def get_parameters_by_path(self, path: str, recursive: bool = True) -> Dict[str, str]:
        """Get all parameters under a path"""
        try:
            parameters = {}
            paginator = self.client.get_paginator("get_parameters_by_path")

            for page in paginator.paginate(Path=path, Recursive=recursive, WithDecryption=True):
                for param in page["Parameters"]:
                    # Extract parameter name without path
                    name = param["Name"].split("/")[-1]
                    parameters[name] = param["Value"]

            return parameters
        except ClientError as e:
            logger.error(f"Error getting parameters by path {path}: {e}")
            return {}

    def put_parameter(
        self,
        parameter_name: str,
        value: str,
        param_type: str = "String",
        overwrite: bool = True,
    ) -> bool:
        """Put parameter value"""
        try:
            self.client.put_parameter(
                Name=parameter_name, Value=value, Type=param_type, Overwrite=overwrite
            )
            return True
        except ClientError as e:
            logger.error(f"Error putting parameter {parameter_name}: {e}")
            return False


class CloudWatchClient:
    """CloudWatch client wrapper"""

    def __init__(self, region_name: str = None):
        self.region_name = region_name or os.getenv("AWS_REGION", "us-east-1")
        self.logs_client = boto3.client("logs", region_name=self.region_name)
        self.metrics_client = boto3.client("cloudwatch", region_name=self.region_name)

    def put_log_events(self, log_group: str, log_stream: str, messages: List[str]) -> bool:
        """Put log events to CloudWatch"""
        try:
            # Create log stream if it doesn't exist
            try:
                self.logs_client.create_log_stream(logGroupName=log_group, logStreamName=log_stream)
            except ClientError:
                pass  # Stream already exists

            # Prepare log events
            events = [
                {"timestamp": int(datetime.utcnow().timestamp() * 1000), "message": msg}
                for msg in messages
            ]

            # Put log events
            self.logs_client.put_log_events(
                logGroupName=log_group, logStreamName=log_stream, logEvents=events
            )
            return True
        except ClientError as e:
            logger.error(f"Error putting log events: {e}")
            return False

    def put_metric(
        self,
        namespace: str,
        metric_name: str,
        value: float,
        unit: str = "None",
        dimensions: Dict[str, str] = None,
    ) -> bool:
        """Put metric to CloudWatch"""
        try:
            metric_data = {
                "MetricName": metric_name,
                "Value": value,
                "Unit": unit,
                "Timestamp": datetime.utcnow(),
            }

            if dimensions:
                metric_data["Dimensions"] = [{"Name": k, "Value": v} for k, v in dimensions.items()]

            self.metrics_client.put_metric_data(Namespace=namespace, MetricData=[metric_data])
            return True
        except ClientError as e:
            logger.error(f"Error putting metric: {e}")
            return False

    def get_metric_statistics(
        self,
        namespace: str,
        metric_name: str,
        start_time: datetime,
        end_time: datetime,
        period: int = 300,
        statistics: List[str] = None,
        dimensions: Dict[str, str] = None,
    ) -> List[Dict]:
        """Get metric statistics from CloudWatch"""
        try:
            kwargs = {
                "Namespace": namespace,
                "MetricName": metric_name,
                "StartTime": start_time,
                "EndTime": end_time,
                "Period": period,
                "Statistics": statistics or ["Average", "Sum", "Minimum", "Maximum"],
            }

            if dimensions:
                kwargs["Dimensions"] = [{"Name": k, "Value": v} for k, v in dimensions.items()]

            response = self.metrics_client.get_metric_statistics(**kwargs)
            return response.get("Datapoints", [])
        except ClientError as e:
            logger.error(f"Error getting metric statistics: {e}")
            return []


class SQSClient:
    """SQS client wrapper"""

    def __init__(self, region_name: str = None):
        self.region_name = region_name or os.getenv("AWS_REGION", "us-east-1")
        self.client = boto3.client("sqs", region_name=self.region_name)

    def send_message(
        self,
        queue_url: str,
        message_body: Dict[str, Any],
        message_attributes: Dict = None,
    ) -> Optional[str]:
        """Send message to SQS queue"""
        try:
            kwargs = {"QueueUrl": queue_url, "MessageBody": json.dumps(message_body)}

            if message_attributes:
                kwargs["MessageAttributes"] = message_attributes

            response = self.client.send_message(**kwargs)
            return response.get("MessageId")
        except ClientError as e:
            logger.error(f"Error sending message to SQS: {e}")
            return None

    def receive_messages(
        self, queue_url: str, max_messages: int = 10, wait_time: int = 20
    ) -> List[Dict]:
        """Receive messages from SQS queue"""
        try:
            response = self.client.receive_message(
                QueueUrl=queue_url,
                MaxNumberOfMessages=max_messages,
                WaitTimeSeconds=wait_time,
                MessageAttributeNames=["All"],
            )

            messages = []
            for msg in response.get("Messages", []):
                messages.append(
                    {
                        "MessageId": msg["MessageId"],
                        "ReceiptHandle": msg["ReceiptHandle"],
                        "Body": json.loads(msg["Body"]),
                        "Attributes": msg.get("MessageAttributes", {}),
                    }
                )

            return messages
        except ClientError as e:
            logger.error(f"Error receiving messages from SQS: {e}")
            return []

    def delete_message(self, queue_url: str, receipt_handle: str) -> bool:
        """Delete message from SQS queue"""
        try:
            self.client.delete_message(QueueUrl=queue_url, ReceiptHandle=receipt_handle)
            return True
        except ClientError as e:
            logger.error(f"Error deleting message from SQS: {e}")
            return False


# Singleton instances
_dynamodb_client = None
_s3_client = None
_secrets_client = None
_params_client = None
_cloudwatch_client = None
_sqs_client = None


def get_dynamodb_client() -> DynamoDBClient:
    """Get singleton DynamoDB client"""
    global _dynamodb_client
    if _dynamodb_client is None:
        _dynamodb_client = DynamoDBClient()
    return _dynamodb_client


def get_s3_client() -> S3Client:
    """Get singleton S3 client"""
    global _s3_client
    if _s3_client is None:
        _s3_client = S3Client()
    return _s3_client


def get_secrets_client() -> SecretsManagerClient:
    """Get singleton Secrets Manager client"""
    global _secrets_client
    if _secrets_client is None:
        _secrets_client = SecretsManagerClient()
    return _secrets_client


def get_params_client() -> ParameterStoreClient:
    """Get singleton Parameter Store client"""
    global _params_client
    if _params_client is None:
        _params_client = ParameterStoreClient()
    return _params_client


def get_cloudwatch_client() -> CloudWatchClient:
    """Get singleton CloudWatch client"""
    global _cloudwatch_client
    if _cloudwatch_client is None:
        _cloudwatch_client = CloudWatchClient()
    return _cloudwatch_client


def get_sqs_client() -> SQSClient:
    """Get singleton SQS client"""
    global _sqs_client
    if _sqs_client is None:
        _sqs_client = SQSClient()
    return _sqs_client


__all__ = [
    "DynamoDBClient",
    "S3Client",
    "SecretsManagerClient",
    "ParameterStoreClient",
    "CloudWatchClient",
    "SQSClient",
    "get_dynamodb_client",
    "get_s3_client",
    "get_secrets_client",
    "get_params_client",
    "get_cloudwatch_client",
    "get_sqs_client",
]
