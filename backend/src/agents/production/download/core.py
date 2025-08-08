"""
Download Agent Core Implementation
Phase 4 Tasks 4.81-4.90: 다운로드 및 배포 준비 에이전트
"""

import json
import logging
import os
import time
import asyncio
import zipfile
import tarfile
import shutil
from dataclasses import dataclass, asdict, field
from typing import Dict, List, Optional, Any, Tuple, Set
from enum import Enum
from collections import defaultdict
from pathlib import Path
import hashlib
import uuid
from datetime import datetime, timedelta

import boto3
from aws_lambda_powertools import Logger, Tracer, Metrics
from aws_lambda_powertools.metrics import MetricUnit
from botocore.exceptions import ClientError

# Agno Framework 통합
try:
    from agno.agent import Agent
    from agno.models.aws import AwsBedrock
    from agno.memory import ConversationSummaryMemory
    from agno.tools import Tool
    AGNO_AVAILABLE = True
except ImportError:
    AGNO_AVAILABLE = False

# Production 로깅 설정
logger = Logger()
tracer = Tracer()
metrics = Metrics()

# AWS 클라이언트
ssm = boto3.client('ssm')
secrets = boto3.client('secretsmanager')
dynamodb = boto3.resource('dynamodb')
bedrock = boto3.client('bedrock-runtime')
s3 = boto3.client('s3')
cloudfront = boto3.client('cloudfront')


class DownloadFormat(Enum):
    """다운로드 형식"""
    ZIP = "zip"
    TAR_GZ = "tar.gz"
    TAR_BZ2 = "tar.bz2"
    DOCKER_IMAGE = "docker"
    GIT_BUNDLE = "git-bundle"
    ISO = "iso"
    RAW = "raw"


class DeliveryMethod(Enum):
    """전달 방법"""
    DIRECT_DOWNLOAD = "direct-download"
    S3_PRESIGNED_URL = "s3-presigned-url"
    CLOUDFRONT_URL = "cloudfront-url"
    FTP = "ftp"
    GIT_CLONE = "git-clone"
    DOCKER_REGISTRY = "docker-registry"
    STREAMING = "streaming"


class AccessControl(Enum):
    """접근 제어"""
    PUBLIC = "public"
    AUTHENTICATED = "authenticated"
    TEMPORARY = "temporary"
    RESTRICTED = "restricted"
    PRIVATE = "private"


@dataclass
class DownloadPackage:
    """다운로드 패키지"""
    id: str
    name: str
    format: DownloadFormat
    size: int
    checksum: str
    created_at: datetime
    expires_at: Optional[datetime]
    metadata: Dict[str, Any]


@dataclass
class DownloadLink:
    """다운로드 링크"""
    url: str
    method: DeliveryMethod
    access_control: AccessControl
    expires_at: Optional[datetime]
    download_count: int = 0
    max_downloads: Optional[int] = None
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class DocumentationPackage:
    """문서 패키지"""
    readme: str
    api_docs: Optional[str]
    user_guide: Optional[str]
    developer_guide: Optional[str]
    deployment_guide: Optional[str]
    changelog: Optional[str]
    license: Optional[str]


@dataclass
class DeploymentInstructions:
    """배포 지침"""
    prerequisites: List[str]
    installation_steps: List[str]
    configuration_steps: List[str]
    verification_steps: List[str]
    troubleshooting: Dict[str, str]
    support_contact: Optional[str]


@dataclass
class DownloadMetrics:
    """다운로드 메트릭"""
    total_downloads: int
    unique_downloads: int
    average_download_time: float
    success_rate: float
    bandwidth_used: int
    geographic_distribution: Dict[str, int]


@dataclass
class DownloadResult:
    """다운로드 결과"""
    package_id: str
    download_links: List[DownloadLink]
    documentation: DocumentationPackage
    deployment_instructions: DeploymentInstructions
    file_manifest: Dict[str, Any]
    total_size: int
    checksum: str
    created_at: datetime
    expires_at: Optional[datetime]
    metrics: DownloadMetrics
    metadata: Dict[str, Any]


class PackageCreator(Tool):
    """패키지 생성 도구 (Agno Tool)"""
    
    def __init__(self):
        super().__init__(
            name="package_creator",
            description="Create download packages from assembled projects"
        )
        self.temp_dir = Path("/tmp/downloads")
        self.temp_dir.mkdir(exist_ok=True)
    
    async def run(
        self,
        project_path: str,
        format: DownloadFormat,
        config: Dict[str, Any]
    ) -> DownloadPackage:
        """패키지 생성 실행"""
        package_id = str(uuid.uuid4())
        timestamp = datetime.now()
        
        # 패키지 생성
        if format == DownloadFormat.ZIP:
            package_path = await self._create_zip(project_path, package_id)
        elif format == DownloadFormat.TAR_GZ:
            package_path = await self._create_tar_gz(project_path, package_id)
        else:
            package_path = await self._create_raw(project_path, package_id)
        
        # 체크섬 계산
        checksum = self._calculate_checksum(package_path)
        
        # 크기 계산
        size = package_path.stat().st_size
        
        return DownloadPackage(
            id=package_id,
            name=config.get('name', 'project'),
            format=format,
            size=size,
            checksum=checksum,
            created_at=timestamp,
            expires_at=timestamp + timedelta(days=7),
            metadata={
                'path': str(package_path),
                'config': config
            }
        )
    
    async def _create_zip(self, source_path: str, package_id: str) -> Path:
        """ZIP 패키지 생성"""
        output_path = self.temp_dir / f"{package_id}.zip"
        
        with zipfile.ZipFile(output_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
            source = Path(source_path)
            for file_path in source.rglob('*'):
                if file_path.is_file():
                    arcname = file_path.relative_to(source)
                    zipf.write(file_path, arcname)
        
        return output_path
    
    async def _create_tar_gz(self, source_path: str, package_id: str) -> Path:
        """TAR.GZ 패키지 생성"""
        output_path = self.temp_dir / f"{package_id}.tar.gz"
        
        with tarfile.open(output_path, 'w:gz') as tar:
            tar.add(source_path, arcname=os.path.basename(source_path))
        
        return output_path
    
    async def _create_raw(self, source_path: str, package_id: str) -> Path:
        """RAW 패키지 생성 (디렉토리 복사)"""
        output_path = self.temp_dir / package_id
        shutil.copytree(source_path, output_path)
        return output_path
    
    def _calculate_checksum(self, file_path: Path) -> str:
        """체크섬 계산"""
        sha256_hash = hashlib.sha256()
        
        if file_path.is_file():
            with open(file_path, "rb") as f:
                for byte_block in iter(lambda: f.read(4096), b""):
                    sha256_hash.update(byte_block)
        else:
            # 디렉토리의 경우 모든 파일의 체크섬
            for file in file_path.rglob('*'):
                if file.is_file():
                    with open(file, "rb") as f:
                        for byte_block in iter(lambda: f.read(4096), b""):
                            sha256_hash.update(byte_block)
        
        return sha256_hash.hexdigest()


class DownloadAgent:
    """Production-ready Download Agent with full Task 4.81-4.90 implementation"""
    
    def __init__(self, environment: str = None):
        """
        초기화
        
        Args:
            environment: 실행 환경 (development/staging/production)
        """
        self.environment = environment or os.environ.get('ENVIRONMENT', 'development')
        self.config = self._load_config()
        
        # Agno Agent 초기화
        if AGNO_AVAILABLE:
            self._init_agno_agent()
        else:
            logger.warning("Agno Framework not available, using fallback mode")
            self.agent = None
        
        # 컴포넌트 초기화
        self._init_components()
        
        # 스토리지 초기화
        self._init_storage()
        
        # 메트릭 초기화
        self.download_counts = defaultdict(int)
        self.bandwidth_usage = defaultdict(int)
        
        logger.info(f"Download Agent initialized for {self.environment}")
    
    def _load_config(self) -> Dict[str, Any]:
        """AWS Parameter Store에서 설정 로드"""
        try:
            response = ssm.get_parameters_by_path(
                Path=f'/t-developer/{self.environment}/download-agent/',
                Recursive=True,
                WithDecryption=True
            )
            
            config = {}
            for param in response['Parameters']:
                key = param['Name'].split('/')[-1]
                config[key] = param['Value']
            
            return config
        except ClientError as e:
            logger.error(f"Failed to load config: {e}")
            return {
                'download_bucket': 't-developer-downloads',
                'cdn_distribution_id': None,
                'max_package_size': 5368709120,  # 5GB
                'default_expiry_days': 7,
                'enable_cdn': True,
                'enable_compression': True,
                'enable_encryption': True,
                'workspace_path': '/tmp/download-workspace'
            }
    
    def _init_agno_agent(self):
        """Agno 에이전트 초기화"""
        try:
            self.agent = Agent(
                name="Download-Delivery-Expert",
                model=AwsBedrock(
                    id="anthropic.claude-3-sonnet-v2:0",
                    region="us-east-1"
                ),
                role="Expert in package creation and download delivery",
                instructions=[
                    "Create optimized download packages",
                    "Generate secure download links",
                    "Prepare comprehensive documentation",
                    "Setup CDN distribution",
                    "Implement access controls",
                    "Track download metrics",
                    "Provide deployment instructions"
                ],
                memory=ConversationSummaryMemory(
                    storage_type="dynamodb",
                    table_name=f"t-dev-download-sessions-{self.environment}"
                ),
                tools=[
                    PackageCreator()
                ],
                temperature=0.2,
                max_retries=3
            )
            logger.info("Agno agent initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize Agno agent: {e}")
            self.agent = None
    
    def _init_components(self):
        """컴포넌트 초기화"""
        from .package_optimizer import PackageOptimizer
        from .compression_engine import CompressionEngine
        from .encryption_manager import EncryptionManager
        from .link_generator import LinkGenerator
        from .cdn_configurator import CDNConfigurator
        from .documentation_bundler import DocumentationBundler
        from .deployment_preparer import DeploymentPreparer
        from .access_controller import AccessController
        from .metrics_tracker import MetricsTracker
        from .cleanup_manager import CleanupManager
        
        self.package_optimizer = PackageOptimizer()
        self.compression_engine = CompressionEngine()
        self.encryption_manager = EncryptionManager()
        self.link_generator = LinkGenerator()
        self.cdn_configurator = CDNConfigurator()
        self.documentation_bundler = DocumentationBundler()
        self.deployment_preparer = DeploymentPreparer()
        self.access_controller = AccessController()
        self.metrics_tracker = MetricsTracker()
        self.cleanup_manager = CleanupManager()
    
    def _init_storage(self):
        """스토리지 초기화"""
        self.workspace = Path(self.config['workspace_path'])
        self.workspace.mkdir(parents=True, exist_ok=True)
        
        # S3 버킷 확인
        try:
            s3.head_bucket(Bucket=self.config['download_bucket'])
        except ClientError:
            logger.warning(f"Bucket {self.config['download_bucket']} not accessible")
    
    @tracer.capture_method
    @metrics.log_metrics(capture_cold_start_metric=True)
    async def prepare_download(
        self,
        assembly_result: Dict[str, Any],
        download_config: Optional[Dict[str, Any]] = None
    ) -> DownloadResult:
        """
        다운로드 준비 수행 (Tasks 4.81-4.90)
        
        Args:
            assembly_result: 조립 결과
            download_config: 다운로드 설정
            
        Returns:
            DownloadResult: 다운로드 결과
        """
        start_time = time.time()
        
        try:
            # 설정 준비
            if not download_config:
                download_config = self._create_default_config()
            
            # 1. 패키지 생성 (Task 4.81)
            download_package = await self._create_package(
                assembly_result, download_config
            )
            
            # 2. 압축 및 최적화 (Task 4.82)
            if self.config.get('enable_compression', True):
                optimized_package = await self._optimize_package(download_package)
            else:
                optimized_package = download_package
            
            # 3. 암호화 (Task 4.83)
            if self.config.get('enable_encryption', True):
                encrypted_package = await self._encrypt_package(optimized_package)
            else:
                encrypted_package = optimized_package
            
            # 4. S3 업로드 (Task 4.84)
            s3_location = await self._upload_to_s3(encrypted_package)
            
            # 5. 다운로드 링크 생성 (Task 4.85)
            download_links = await self._generate_download_links(
                s3_location, download_config
            )
            
            # 6. CDN 설정 (Task 4.86)
            if self.config.get('enable_cdn', True):
                cdn_links = await self._setup_cdn(s3_location, download_links)
                download_links.extend(cdn_links)
            
            # 7. 문서 번들링 (Task 4.87)
            documentation = await self._bundle_documentation(
                assembly_result, download_package
            )
            
            # 8. 배포 지침 생성 (Task 4.88)
            deployment_instructions = await self._create_deployment_instructions(
                assembly_result, download_package
            )
            
            # 9. 접근 제어 설정 (Task 4.89)
            access_controls = await self._setup_access_controls(
                download_links, download_config
            )
            
            # 10. 메트릭 및 정리 (Task 4.90)
            final_result = await self._finalize_download(
                download_package,
                download_links,
                documentation,
                deployment_instructions,
                access_controls
            )
            
            # 메트릭 기록
            processing_time = time.time() - start_time
            
            metrics.add_metric(
                name="DownloadPreparationTime",
                unit=MetricUnit.Seconds,
                value=processing_time
            )
            metrics.add_metric(
                name="PackageSize",
                unit=MetricUnit.Bytes,
                value=final_result.total_size
            )
            
            logger.info(
                "Successfully prepared download",
                extra={
                    "package_id": final_result.package_id,
                    "total_size": final_result.total_size,
                    "links_count": len(final_result.download_links),
                    "processing_time": processing_time
                }
            )
            
            return final_result
            
        except Exception as e:
            logger.error(f"Error preparing download: {e}")
            metrics.add_metric(name="DownloadError", unit=MetricUnit.Count, value=1)
            raise
    
    async def _create_package(
        self,
        assembly_result: Dict[str, Any],
        config: Dict[str, Any]
    ) -> DownloadPackage:
        """Task 4.81: 패키지 생성"""
        # 패키지 ID 생성
        package_id = str(uuid.uuid4())
        
        # 패키지 경로 준비
        package_path = self.workspace / package_id
        package_path.mkdir(exist_ok=True)
        
        # 프로젝트 파일 복사
        project_path = Path(assembly_result['assembled_path'])
        if project_path.exists():
            shutil.copytree(project_path, package_path / 'project', dirs_exist_ok=True)
        
        # 메타데이터 추가
        metadata = {
            'project_name': assembly_result.get('project_manifest', {}).get('project_name'),
            'version': assembly_result.get('project_manifest', {}).get('version'),
            'created_at': datetime.now().isoformat(),
            'assembly_result': assembly_result
        }
        
        metadata_file = package_path / 'metadata.json'
        metadata_file.write_text(json.dumps(metadata, indent=2))
        
        # 패키지 형식 결정
        format = DownloadFormat(config.get('format', 'zip'))
        
        # PackageCreator 도구 사용
        if self.agent:
            package = await PackageCreator().run(
                str(package_path),
                format,
                config
            )
        else:
            # Fallback
            package = await self._create_package_fallback(
                package_path, package_id, format, config
            )
        
        return package
    
    async def _optimize_package(
        self,
        package: DownloadPackage
    ) -> DownloadPackage:
        """Task 4.82: 압축 및 최적화"""
        return await self.package_optimizer.optimize(package)
    
    async def _encrypt_package(
        self,
        package: DownloadPackage
    ) -> DownloadPackage:
        """Task 4.83: 암호화"""
        return await self.encryption_manager.encrypt(package)
    
    async def _upload_to_s3(
        self,
        package: DownloadPackage
    ) -> Dict[str, Any]:
        """Task 4.84: S3 업로드"""
        bucket = self.config['download_bucket']
        key = f"downloads/{package.id}/{package.name}.{package.format.value}"
        
        # 파일 업로드
        package_path = Path(package.metadata['path'])
        
        if package_path.is_file():
            with open(package_path, 'rb') as f:
                s3.upload_fileobj(
                    f, bucket, key,
                    ExtraArgs={
                        'Metadata': {
                            'package-id': package.id,
                            'checksum': package.checksum
                        }
                    }
                )
        else:
            # 디렉토리의 경우 tar로 압축 후 업로드
            tar_path = package_path.parent / f"{package.id}.tar.gz"
            with tarfile.open(tar_path, 'w:gz') as tar:
                tar.add(package_path, arcname=package.name)
            
            with open(tar_path, 'rb') as f:
                s3.upload_fileobj(f, bucket, key)
        
        return {
            'bucket': bucket,
            'key': key,
            'region': 'us-east-1',
            'size': package.size
        }
    
    async def _generate_download_links(
        self,
        s3_location: Dict[str, Any],
        config: Dict[str, Any]
    ) -> List[DownloadLink]:
        """Task 4.85: 다운로드 링크 생성"""
        return await self.link_generator.generate(s3_location, config)
    
    async def _setup_cdn(
        self,
        s3_location: Dict[str, Any],
        download_links: List[DownloadLink]
    ) -> List[DownloadLink]:
        """Task 4.86: CDN 설정"""
        if not self.config.get('cdn_distribution_id'):
            return []
        
        return await self.cdn_configurator.setup(
            s3_location,
            self.config['cdn_distribution_id']
        )
    
    async def _bundle_documentation(
        self,
        assembly_result: Dict[str, Any],
        package: DownloadPackage
    ) -> DocumentationPackage:
        """Task 4.87: 문서 번들링"""
        return await self.documentation_bundler.bundle(assembly_result, package)
    
    async def _create_deployment_instructions(
        self,
        assembly_result: Dict[str, Any],
        package: DownloadPackage
    ) -> DeploymentInstructions:
        """Task 4.88: 배포 지침 생성"""
        return await self.deployment_preparer.prepare(assembly_result, package)
    
    async def _setup_access_controls(
        self,
        download_links: List[DownloadLink],
        config: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Task 4.89: 접근 제어 설정"""
        return await self.access_controller.setup(download_links, config)
    
    async def _finalize_download(
        self,
        package: DownloadPackage,
        download_links: List[DownloadLink],
        documentation: DocumentationPackage,
        deployment_instructions: DeploymentInstructions,
        access_controls: Dict[str, Any]
    ) -> DownloadResult:
        """Task 4.90: 메트릭 및 정리"""
        # 파일 매니페스트 생성
        file_manifest = await self._create_file_manifest(package)
        
        # 메트릭 초기화
        metrics = DownloadMetrics(
            total_downloads=0,
            unique_downloads=0,
            average_download_time=0.0,
            success_rate=1.0,
            bandwidth_used=0,
            geographic_distribution={}
        )
        
        # 메트릭 추적 시작
        await self.metrics_tracker.start_tracking(package.id)
        
        # 임시 파일 정리
        await self.cleanup_manager.cleanup_temp_files(package)
        
        return DownloadResult(
            package_id=package.id,
            download_links=download_links,
            documentation=documentation,
            deployment_instructions=deployment_instructions,
            file_manifest=file_manifest,
            total_size=package.size,
            checksum=package.checksum,
            created_at=package.created_at,
            expires_at=package.expires_at,
            metrics=metrics,
            metadata={
                'access_controls': access_controls,
                'package_metadata': package.metadata
            }
        )
    
    def _create_default_config(self) -> Dict[str, Any]:
        """기본 다운로드 설정 생성"""
        return {
            'format': 'zip',
            'compression_level': 6,
            'encrypt': False,
            'access_control': 'public',
            'expiry_days': self.config.get('default_expiry_days', 7),
            'max_downloads': None
        }
    
    async def _create_package_fallback(
        self,
        package_path: Path,
        package_id: str,
        format: DownloadFormat,
        config: Dict[str, Any]
    ) -> DownloadPackage:
        """Fallback 패키지 생성"""
        # ZIP 생성
        if format == DownloadFormat.ZIP:
            output_path = self.workspace / f"{package_id}.zip"
            shutil.make_archive(
                str(output_path.with_suffix('')),
                'zip',
                package_path
            )
        else:
            output_path = package_path
        
        # 체크섬 계산
        checksum = self._calculate_checksum(output_path)
        
        return DownloadPackage(
            id=package_id,
            name=config.get('name', 'project'),
            format=format,
            size=self._get_size(output_path),
            checksum=checksum,
            created_at=datetime.now(),
            expires_at=datetime.now() + timedelta(days=config.get('expiry_days', 7)),
            metadata={'path': str(output_path)}
        )
    
    def _calculate_checksum(self, path: Path) -> str:
        """체크섬 계산"""
        sha256_hash = hashlib.sha256()
        
        if path.is_file():
            with open(path, "rb") as f:
                for byte_block in iter(lambda: f.read(4096), b""):
                    sha256_hash.update(byte_block)
        
        return sha256_hash.hexdigest()
    
    def _get_size(self, path: Path) -> int:
        """파일/디렉토리 크기 계산"""
        if path.is_file():
            return path.stat().st_size
        else:
            total = 0
            for file in path.rglob('*'):
                if file.is_file():
                    total += file.stat().st_size
            return total
    
    async def _create_file_manifest(
        self,
        package: DownloadPackage
    ) -> Dict[str, Any]:
        """파일 매니페스트 생성"""
        manifest = {
            'package_id': package.id,
            'format': package.format.value,
            'files': [],
            'directories': [],
            'total_files': 0,
            'total_size': package.size
        }
        
        package_path = Path(package.metadata['path'])
        
        if package_path.is_dir():
            for item in package_path.rglob('*'):
                if item.is_file():
                    rel_path = item.relative_to(package_path)
                    manifest['files'].append({
                        'path': str(rel_path),
                        'size': item.stat().st_size,
                        'modified': item.stat().st_mtime
                    })
                elif item.is_dir():
                    rel_path = item.relative_to(package_path)
                    manifest['directories'].append(str(rel_path))
            
            manifest['total_files'] = len(manifest['files'])
        
        return manifest


def lambda_handler(event: Dict[str, Any], context: Any) -> Dict[str, Any]:
    """
    AWS Lambda 핸들러
    
    Args:
        event: Lambda 이벤트
        context: Lambda 컨텍스트
        
    Returns:
        API Gateway 응답
    """
    import asyncio
    
    try:
        # 요청 파싱
        body = json.loads(event.get('body', '{}'))
        assembly_result = body.get('assembly_result', {})
        download_config = body.get('download_config')
        
        # Agent 실행
        agent = DownloadAgent()
        
        # 비동기 함수를 동기적으로 실행
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        download_result = loop.run_until_complete(
            agent.prepare_download(assembly_result, download_config)
        )
        
        # 응답 구성
        return {
            'statusCode': 200,
            'headers': {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*'
            },
            'body': json.dumps(asdict(download_result), ensure_ascii=False, default=str)
        }
        
    except ValueError as e:
        logger.error(f"Validation error: {e}")
        return {
            'statusCode': 400,
            'body': json.dumps({
                'error': {
                    'code': 'VALIDATION_ERROR',
                    'message': str(e)
                }
            }, ensure_ascii=False)
        }
        
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        return {
            'statusCode': 500,
            'body': json.dumps({
                'error': {
                    'code': 'INTERNAL_ERROR',
                    'message': 'Error preparing download'
                }
            }, ensure_ascii=False)
        }