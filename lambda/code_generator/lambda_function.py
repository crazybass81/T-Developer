import json
import os
import boto3
import logging
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
    Lambda handler for code generation
    
    Args:
        event: Lambda event containing code generation details
        context: Lambda context
        
    Returns:
        Response with generated code
    """
    logger.info(f"Received event: {json.dumps(event)}")
    
    try:
        # Extract details
        task_id = event.get('task_id')
        s3_bucket = event.get('s3_bucket')
        instruction = event.get('instruction', {})
        
        if not task_id or not s3_bucket:
            raise ValueError("Missing required parameters: task_id or s3_bucket")
        
        # Create a temporary directory for the code
        with tempfile.TemporaryDirectory() as temp_dir:
            # Check if there's a template to download
            if 'template_s3_key' in event:
                # Download the template from S3
                template_s3_key = event['template_s3_key']
                logger.info(f"Downloading template from s3://{s3_bucket}/{template_s3_key}")
                s3_response = s3_client.get_object(Bucket=s3_bucket, Key=template_s3_key)
                zip_content = s3_response['Body'].read()
                
                # Extract the ZIP file
                with zipfile.ZipFile(BytesIO(zip_content)) as zip_ref:
                    zip_ref.extractall(temp_dir)
            
            # Generate code based on instruction
            result = generate_code(instruction, temp_dir)
            
            # Package the generated code
            zip_file = os.path.join('/tmp', f"{task_id}_code.zip")
            with zipfile.ZipFile(zip_file, 'w', zipfile.ZIP_DEFLATED) as zipf:
                for root, _, files in os.walk(temp_dir):
                    for file in files:
                        file_path = os.path.join(root, file)
                        rel_path = os.path.relpath(file_path, temp_dir)
                        zipf.write(file_path, rel_path)
            
            # Upload the ZIP file to S3
            code_s3_key = f"generated_code/{task_id}.zip"
            s3_client.upload_file(zip_file, s3_bucket, code_s3_key)
            
            # Upload result metadata to S3
            result_s3_key = f"code_results/{task_id}.json"
            s3_client.put_object(
                Bucket=s3_bucket,
                Key=result_s3_key,
                Body=json.dumps(result),
                ContentType='application/json'
            )
            
            logger.info(f"Code generation completed for task {task_id}")
            
            return {
                'statusCode': 200,
                'body': json.dumps({
                    'status': 'success',
                    'task_id': task_id,
                    'code_s3_key': code_s3_key,
                    'result_s3_key': result_s3_key
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

def generate_code(instruction, output_dir):
    """
    Generate code based on instruction
    
    Args:
        instruction: Code generation instruction
        output_dir: Directory to write generated code
        
    Returns:
        Result metadata
    """
    # This is a placeholder for actual code generation logic
    # In a real implementation, this would use Amazon Q, OpenAI, or another code generation service
    
    # For demonstration, we'll create some sample files
    feature_name = instruction.get('feature_name', 'unknown')
    description = instruction.get('description', '')
    
    # Create a simple Python file
    with open(os.path.join(output_dir, f"{feature_name.lower().replace(' ', '_')}.py"), 'w') as f:
        f.write(f'''"""
{feature_name}

{description}
"""

def main():
    """Main function"""
    print("Implementing {feature_name}")
    
if __name__ == "__main__":
    main()
''')
    
    # Create a test file
    with open(os.path.join(output_dir, f"test_{feature_name.lower().replace(' ', '_')}.py"), 'w') as f:
        f.write(f'''"""
Tests for {feature_name}
"""
import unittest

class Test{feature_name.replace(" ", "")}(unittest.TestCase):
    """Test cases for {feature_name}"""
    
    def test_basic_functionality(self):
        """Test basic functionality"""
        self.assertTrue(True)
        
if __name__ == "__main__":
    unittest.main()
''')
    
    # Return metadata about the generated code
    return {
        'success': True,
        'modified_files': [],
        'created_files': [
            f"{feature_name.lower().replace(' ', '_')}.py",
            f"test_{feature_name.lower().replace(' ', '_')}.py"
        ]
    }