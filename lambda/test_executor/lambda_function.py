import json
import os
import boto3
import logging
import subprocess
import tempfile
import shutil
import zipfile
from io import BytesIO

# Configure logging
logger = logging.getLogger()
logger.setLevel(logging.INFO)

# Initialize S3 client
s3_client = boto3.client('s3')

def lambda_handler(event, context):
    """
    Lambda handler for test execution
    
    Args:
        event: Lambda event containing test details
        context: Lambda context
        
    Returns:
        Response with test results
    """
    logger.info(f"Received event: {json.dumps(event)}")
    
    try:
        # Extract test details
        task_id = event.get('task_id')
        s3_bucket = event.get('s3_bucket')
        s3_key = event.get('s3_key')
        
        if not task_id or not s3_bucket or not s3_key:
            raise ValueError("Missing required parameters: task_id, s3_bucket, or s3_key")
        
        # Create a temporary directory for the code
        with tempfile.TemporaryDirectory() as temp_dir:
            # Download the code from S3
            logger.info(f"Downloading code from s3://{s3_bucket}/{s3_key}")
            s3_response = s3_client.get_object(Bucket=s3_bucket, Key=s3_key)
            zip_content = s3_response['Body'].read()
            
            # Extract the ZIP file
            with zipfile.ZipFile(BytesIO(zip_content)) as zip_ref:
                zip_ref.extractall(temp_dir)
            
            # Run tests
            logger.info(f"Running tests in {temp_dir}")
            test_result = run_tests(temp_dir)
            
            # Upload test results to S3
            result_key = f"test_results/{task_id}.json"
            s3_client.put_object(
                Bucket=s3_bucket,
                Key=result_key,
                Body=json.dumps(test_result),
                ContentType='application/json'
            )
            
            # Upload test logs to S3
            log_key = f"test_logs/{task_id}.txt"
            s3_client.put_object(
                Bucket=s3_bucket,
                Key=log_key,
                Body=test_result.get('log', ''),
                ContentType='text/plain'
            )
            
            logger.info(f"Test results uploaded to s3://{s3_bucket}/{result_key}")
            
            return {
                'statusCode': 200,
                'body': json.dumps({
                    'status': 'success',
                    'task_id': task_id,
                    'result': test_result,
                    'result_key': result_key,
                    'log_key': log_key
                })
            }
    
    except Exception as e:
        logger.error(f"Error: {str(e)}")
        return {
            'statusCode': 500,
            'body': json.dumps({
                'status': 'error',
                'message': str(e)
            })
        }

def run_tests(directory):
    """
    Run tests in the specified directory
    
    Args:
        directory: Directory containing the code to test
        
    Returns:
        Test results
    """
    try:
        # Install dependencies
        subprocess.run(
            ["pip", "install", "-r", "requirements.txt"],
            cwd=directory,
            capture_output=True,
            text=True,
            check=False
        )
        
        # Run pytest
        process = subprocess.run(
            ["pytest", "-v"],
            cwd=directory,
            capture_output=True,
            text=True,
            timeout=60
        )
        
        # Parse test results
        success = process.returncode == 0
        log_output = process.stdout + process.stderr
        
        # Extract test counts
        import re
        summary_match = re.search(r'(\d+) passed(?:, (\d+) failed)? in', log_output)
        
        if summary_match:
            passed = int(summary_match.group(1))
            failed = int(summary_match.group(2)) if summary_match.group(2) else 0
            total = passed + failed
        else:
            passed = 0
            failed = 0 if success else 1
            total = passed + failed
        
        # Extract failures
        failures = []
        if not success:
            failure_matches = re.finditer(r'FAILED ([\\w\\.\\/]+)::([\\w]+)', log_output)
            for match in failure_matches:
                file_path = match.group(1)
                test_name = match.group(2)
                failures.append({
                    "file": file_path,
                    "test": test_name,
                    "message": "Test failure"
                })
        
        return {
            "success": success,
            "total": total,
            "passed": passed,
            "failed": failed,
            "log": log_output,
            "failures": failures
        }
    
    except subprocess.TimeoutExpired:
        return {
            "success": False,
            "total": 0,
            "passed": 0,
            "failed": 1,
            "log": "Test execution timed out after 60 seconds",
            "failures": [{
                "file": "test_runner",
                "test": "execution",
                "message": "Timeout"
            }]
        }
    
    except Exception as e:
        return {
            "success": False,
            "total": 0,
            "passed": 0,
            "failed": 1,
            "log": f"Error running tests: {str(e)}",
            "failures": [{
                "file": "test_runner",
                "test": "execution",
                "message": str(e)
            }]
        }