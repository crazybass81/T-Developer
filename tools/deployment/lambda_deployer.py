"""
AWS Lambda deployment tool for T-Developer

Handles packaging and deploying code to AWS Lambda
"""
import boto3
import logging
import os
import shutil
import subprocess
import tempfile
import zipfile
from typing import Dict, Any, Optional

from config import settings

# Set up logging
logger = logging.getLogger(__name__)

class LambdaDeployer:
    """
    AWS Lambda deployment tool
    """
    
    def __init__(self):
        """Initialize the Lambda deployer"""
        self.lambda_client = boto3.client('lambda', region_name=settings.AWS_REGION)
        self.function_name = settings.LAMBDA_FUNCTION_NAME
        self.s3_client = boto3.client('s3', region_name=settings.AWS_REGION)
        self.bucket_name = settings.S3_BUCKET_NAME
    
    def package_code(self, source_dir: str) -> str:
        """
        Package code into a ZIP file for Lambda deployment
        
        Args:
            source_dir: Source directory containing the code
            
        Returns:
            Path to the created ZIP file
        """
        logger.info(f"Packaging code from {source_dir}")
        
        # Create a temporary directory for packaging
        with tempfile.TemporaryDirectory() as temp_dir:
            # Create a ZIP file
            zip_path = os.path.join(temp_dir, "lambda_package.zip")
            
            with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
                # Walk through the source directory and add files to the ZIP
                for root, _, files in os.walk(source_dir):
                    for file in files:
                        # Skip __pycache__ directories and .pyc files
                        if "__pycache__" in root or file.endswith(".pyc"):
                            continue
                        
                        file_path = os.path.join(root, file)
                        # Calculate the relative path for the ZIP file
                        rel_path = os.path.relpath(file_path, source_dir)
                        zipf.write(file_path, rel_path)
            
            # Copy the ZIP file to a more permanent location
            output_path = os.path.join(os.path.dirname(source_dir), "lambda_package.zip")
            shutil.copy(zip_path, output_path)
            
            logger.info(f"Code packaged to {output_path}")
            return output_path
    
    def upload_to_s3(self, zip_path: str) -> Dict[str, str]:
        """
        Upload the ZIP package to S3
        
        Args:
            zip_path: Path to the ZIP file
            
        Returns:
            Dictionary with S3 bucket and key
        """
        logger.info(f"Uploading package to S3 bucket {self.bucket_name}")
        
        # Generate a key for the ZIP file
        key = f"lambda-deployments/{os.path.basename(zip_path)}"
        
        # Upload the file to S3
        self.s3_client.upload_file(zip_path, self.bucket_name, key)
        
        logger.info(f"Package uploaded to s3://{self.bucket_name}/{key}")
        return {
            "bucket": self.bucket_name,
            "key": key
        }
    
    def update_lambda_function(self, s3_location: Dict[str, str]) -> Dict[str, Any]:
        """
        Update the Lambda function code
        
        Args:
            s3_location: Dictionary with S3 bucket and key
            
        Returns:
            Response from the Lambda update function call
        """
        logger.info(f"Updating Lambda function {self.function_name}")
        
        try:
            # Check if the function exists
            self.lambda_client.get_function(FunctionName=self.function_name)
            
            # Update the function code
            response = self.lambda_client.update_function_code(
                FunctionName=self.function_name,
                S3Bucket=s3_location["bucket"],
                S3Key=s3_location["key"],
                Publish=True
            )
            
            logger.info(f"Lambda function {self.function_name} updated successfully")
            return {
                "status": "updated",
                "version": response.get("Version"),
                "function_name": self.function_name,
                "function_url": f"https://{settings.AWS_REGION}.console.aws.amazon.com/lambda/home?region={settings.AWS_REGION}#/functions/{self.function_name}"
            }
            
        except self.lambda_client.exceptions.ResourceNotFoundException:
            logger.warning(f"Lambda function {self.function_name} not found, creating new function")
            
            # Create a new function
            response = self.lambda_client.create_function(
                FunctionName=self.function_name,
                Runtime='python3.9',
                Role=settings.LAMBDA_ROLE_ARN,
                Handler='main.handler',
                Code={
                    'S3Bucket': s3_location["bucket"],
                    'S3Key': s3_location["key"]
                },
                Description='T-Developer automated deployment',
                Timeout=30,
                MemorySize=256,
                Publish=True
            )
            
            logger.info(f"Lambda function {self.function_name} created successfully")
            return {
                "status": "created",
                "version": response.get("Version"),
                "function_name": self.function_name,
                "function_url": f"https://{settings.AWS_REGION}.console.aws.amazon.com/lambda/home?region={settings.AWS_REGION}#/functions/{self.function_name}"
            }
    
    def deploy(self, source_dir: str) -> Dict[str, Any]:
        """
        Deploy code to AWS Lambda
        
        Args:
            source_dir: Source directory containing the code
            
        Returns:
            Deployment result information
        """
        try:
            # Package the code
            zip_path = self.package_code(source_dir)
            
            # Upload to S3
            s3_location = self.upload_to_s3(zip_path)
            
            # Update Lambda function
            result = self.update_lambda_function(s3_location)
            
            # Clean up the ZIP file
            os.remove(zip_path)
            
            return result
        except Exception as e:
            logger.error(f"Error deploying to Lambda: {e}")
            return {
                "status": "error",
                "error": str(e)
            }