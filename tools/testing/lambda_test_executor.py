"""
LambdaTestExecutor - Lambda 기반 테스트 실행 모듈

Lambda 함수를 사용하여 테스트를 실행하는 기능을 제공합니다.
"""
import json
import logging
import boto3
import os
import tempfile
import zipfile
from typing import Dict, Any, List, Optional

from config import settings

# 로깅 설정
logger = logging.getLogger(__name__)

class LambdaTestExecutor:
    """
    Lambda 기반 테스트 실행 모듈
    
    Lambda 함수를 사용하여 테스트를 실행하는 기능을 제공합니다.
    """
    
    def __init__(self):
        """LambdaTestExecutor 초기화"""
        self.lambda_client = boto3.client('lambda', region_name=settings.AWS_REGION)
        self.s3_client = boto3.client('s3', region_name=settings.AWS_REGION)
        self.lambda_function_name = "t-developer-test-executor"
        self.s3_bucket = settings.S3_BUCKET_NAME
        logger.info(f"LambdaTestExecutor initialized for function: {self.lambda_function_name}")
    
    def run_tests(self, workspace_dir: str, task_id: str) -> Dict[str, Any]:
        """
        테스트 실행
        
        Args:
            workspace_dir: 작업 디렉토리
            task_id: 작업 ID
            
        Returns:
            테스트 결과
        """
        try:
            # 코드를 ZIP 파일로 패키징
            zip_path = self._package_code(workspace_dir)
            
            # ZIP 파일을 S3에 업로드
            s3_key = f"test_code/{task_id}.zip"
            self.s3_client.upload_file(zip_path, self.s3_bucket, s3_key)
            logger.info(f"Code uploaded to s3://{self.s3_bucket}/{s3_key}")
            
            # Lambda 함수에 전달할 페이로드 구성
            payload = {
                "task_id": task_id,
                "s3_bucket": self.s3_bucket,
                "s3_key": s3_key
            }
            
            # Lambda 함수 호출
            response = self._invoke_lambda(payload)
            
            # 응답 처리
            if "body" in response:
                try:
                    body = json.loads(response["body"]) if isinstance(response["body"], str) else response["body"]
                    if body.get("status") == "success":
                        # S3에서 테스트 결과 가져오기
                        result_key = body.get("result_key")
                        if result_key:
                            result_obj = self.s3_client.get_object(Bucket=self.s3_bucket, Key=result_key)
                            result = json.loads(result_obj["Body"].read().decode())
                            logger.info(f"Test results retrieved from S3: {result}")
                            return result
                        return body.get("result", {"success": False, "error": "No result key in response"})
                    else:
                        logger.error(f"Lambda function execution failed: {body}")
                        return {"success": False, "error": body.get("message", "Unknown error")}
                except Exception as e:
                    logger.error(f"Error processing Lambda response: {e}")
                    return {"success": False, "error": str(e)}
            
            logger.error(f"Invalid Lambda response: {response}")
            return {"success": False, "error": "Invalid Lambda response"}
        
        except Exception as e:
            logger.error(f"Error running tests: {e}")
            return {
                "success": False,
                "total": 0,
                "passed": 0,
                "failed": 1,
                "log": f"Error running tests: {str(e)}",
                "failures": [{
                    "file": "test_executor",
                    "test": "execution",
                    "message": str(e)
                }]
            }
        finally:
            # 임시 파일 정리
            if 'zip_path' in locals() and os.path.exists(zip_path):
                os.remove(zip_path)
    
    def _package_code(self, source_dir: str) -> str:
        """
        코드를 ZIP 파일로 패키징
        
        Args:
            source_dir: 소스 디렉토리
            
        Returns:
            ZIP 파일 경로
        """
        logger.info(f"Packaging code from {source_dir}")
        
        # 임시 ZIP 파일 생성
        fd, zip_path = tempfile.mkstemp(suffix=".zip")
        os.close(fd)
        
        with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
            # 소스 디렉토리의 모든 파일 추가
            for root, _, files in os.walk(source_dir):
                for file in files:
                    # __pycache__ 디렉토리와 .pyc 파일 제외
                    if "__pycache__" in root or file.endswith(".pyc"):
                        continue
                    
                    file_path = os.path.join(root, file)
                    # ZIP 파일 내 상대 경로 계산
                    rel_path = os.path.relpath(file_path, source_dir)
                    zipf.write(file_path, rel_path)
        
        logger.info(f"Code packaged to {zip_path}")
        return zip_path
    
    def _invoke_lambda(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        """
        Lambda 함수 호출
        
        Args:
            payload: Lambda 함수에 전달할 페이로드
            
        Returns:
            Lambda 함수 응답
        """
        try:
            response = self.lambda_client.invoke(
                FunctionName=self.lambda_function_name,
                InvocationType='RequestResponse',
                Payload=json.dumps(payload)
            )
            
            # 응답 처리
            if response['StatusCode'] == 200:
                payload = json.loads(response['Payload'].read().decode())
                logger.info(f"Lambda function invoked successfully: {payload}")
                return payload
            else:
                logger.error(f"Lambda function invocation failed: {response}")
                return {"error": f"Lambda function invocation failed: {response['StatusCode']}"}
        
        except Exception as e:
            logger.error(f"Error invoking Lambda function: {e}")
            return {"error": str(e)}