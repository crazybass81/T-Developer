"""
Assembly Agent Core Implementation
Phase 4 Tasks 4.71-4.80: 프로젝트 조립 및 통합 에이전트
"""

import json
import logging
import os
import time
import asyncio
import shutil
import zipfile
import tarfile
from dataclasses import dataclass, asdict, field
from typing import Dict, List, Optional, Any, Tuple, Set
from enum import Enum
from collections import defaultdict
from pathlib import Path
import hashlib
import subprocess

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
codebuild = boto3.client('codebuild')


class AssemblyType(Enum):
    """조립 타입"""
    MONOLITHIC = "monolithic"
    MICROSERVICES = "microservices"
    SERVERLESS = "serverless"
    HYBRID = "hybrid"
    MODULAR = "modular"


class BuildSystem(Enum):
    """빌드 시스템"""
    NPM = "npm"
    YARN = "yarn"
    WEBPACK = "webpack"
    VITE = "vite"
    GRADLE = "gradle"
    MAVEN = "maven"
    MAKE = "make"
    DOCKER = "docker"


class IntegrationType(Enum):
    """통합 타입"""
    REST_API = "rest-api"
    GRAPHQL = "graphql"
    WEBSOCKET = "websocket"
    MESSAGE_QUEUE = "message-queue"
    EVENT_DRIVEN = "event-driven"
    DATABASE = "database"


@dataclass
class AssembledComponent:
    """조립된 컴포넌트"""
    name: str
    path: str
    type: str
    dependencies: List[str]
    configuration: Dict[str, Any]
    build_commands: List[str]
    test_commands: List[str]
    metadata: Dict[str, Any]


@dataclass
class IntegrationPoint:
    """통합 포인트"""
    source_component: str
    target_component: str
    integration_type: IntegrationType
    configuration: Dict[str, Any]
    validation_rules: List[Dict[str, Any]]
    metadata: Dict[str, Any]


@dataclass
class BuildConfiguration:
    """빌드 설정"""
    build_system: BuildSystem
    commands: List[str]
    environment_variables: Dict[str, str]
    dependencies: Dict[str, str]
    scripts: Dict[str, str]
    output_directory: str
    artifacts: List[str]


@dataclass
class DeploymentPackage:
    """배포 패키지"""
    name: str
    version: str
    type: str  # docker, zip, tar, etc.
    path: str
    size: int
    checksum: str
    manifest: Dict[str, Any]
    metadata: Dict[str, Any]


@dataclass
class ProjectManifest:
    """프로젝트 매니페스트"""
    project_name: str
    version: str
    description: str
    components: List[AssembledComponent]
    integrations: List[IntegrationPoint]
    build_config: BuildConfiguration
    deployment_config: Dict[str, Any]
    dependencies: Dict[str, Any]
    metadata: Dict[str, Any]


@dataclass
class AssemblyResult:
    """조립 결과"""
    project_manifest: ProjectManifest
    assembled_path: str
    deployment_packages: List[DeploymentPackage]
    build_logs: List[str]
    test_results: Dict[str, Any]
    integration_status: Dict[str, bool]
    total_size: int
    assembly_time: float
    success: bool
    metadata: Dict[str, Any]


class ProjectAssembler(Tool):
    """프로젝트 조립 도구 (Agno Tool)"""
    
    def __init__(self):
        super().__init__(
            name="project_assembler",
            description="Assemble and integrate project components"
        )
        self.temp_dir = Path("/tmp/assembly")
        self.temp_dir.mkdir(exist_ok=True)
    
    async def run(
        self,
        components: List[Dict[str, Any]],
        configuration: Dict[str, Any]
    ) -> Dict[str, Any]:
        """프로젝트 조립 실행"""
        assembly_path = self.temp_dir / f"project_{int(time.time())}"
        assembly_path.mkdir(exist_ok=True)
        
        # 컴포넌트 복사
        for component in components:
            await self._copy_component(component, assembly_path)
        
        # 통합 설정
        await self._setup_integrations(components, assembly_path)
        
        # 빌드 스크립트 생성
        build_scripts = await self._generate_build_scripts(components, configuration)
        
        return {
            "assembly_path": str(assembly_path),
            "component_count": len(components),
            "build_scripts": build_scripts
        }
    
    async def _copy_component(
        self,
        component: Dict[str, Any],
        target_path: Path
    ):
        """컴포넌트 복사"""
        component_path = target_path / component['name']
        component_path.mkdir(exist_ok=True)
        
        # 파일 복사
        for file_info in component.get('files', []):
            file_path = component_path / file_info['path']
            file_path.parent.mkdir(parents=True, exist_ok=True)
            file_path.write_text(file_info['content'])
    
    async def _setup_integrations(
        self,
        components: List[Dict[str, Any]],
        assembly_path: Path
    ):
        """통합 설정"""
        # 환경 변수 파일 생성
        env_file = assembly_path / '.env'
        env_content = []
        
        for component in components:
            for key, value in component.get('env_vars', {}).items():
                env_content.append(f"{key}={value}")
        
        env_file.write_text('\n'.join(env_content))
    
    async def _generate_build_scripts(
        self,
        components: List[Dict[str, Any]],
        configuration: Dict[str, Any]
    ) -> Dict[str, str]:
        """빌드 스크립트 생성"""
        scripts = {}
        
        # 통합 빌드 스크립트
        build_script = """#!/bin/bash
set -e

echo "Building project..."

# Install dependencies
"""
        for component in components:
            if component.get('build_command'):
                build_script += f"\ncd {component['name']}\n"
                build_script += f"{component['build_command']}\n"
                build_script += "cd ..\n"
        
        build_script += "\necho 'Build complete!'\n"
        scripts['build.sh'] = build_script
        
        # 테스트 스크립트
        test_script = """#!/bin/bash
set -e

echo "Running tests..."

"""
        for component in components:
            if component.get('test_command'):
                test_script += f"\ncd {component['name']}\n"
                test_script += f"{component['test_command']}\n"
                test_script += "cd ..\n"
        
        test_script += "\necho 'Tests complete!'\n"
        scripts['test.sh'] = test_script
        
        return scripts


class AssemblyAgent:
    """Production-ready Assembly Agent with full Task 4.71-4.80 implementation"""
    
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
        
        # 빌드 시스템 초기화
        self._init_build_systems()
        
        # 작업 디렉토리 초기화
        self._init_workspace()
        
        # 메트릭 초기화
        self.assembly_times = []
        self.package_sizes = []
        
        logger.info(f"Assembly Agent initialized for {self.environment}")
    
    def _load_config(self) -> Dict[str, Any]:
        """AWS Parameter Store에서 설정 로드"""
        try:
            response = ssm.get_parameters_by_path(
                Path=f'/t-developer/{self.environment}/assembly-agent/',
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
                'workspace_path': '/tmp/t-developer-assembly',
                'max_package_size': 524288000,  # 500MB
                'parallel_builds': True,
                'run_tests': True,
                'create_docker_images': True,
                'upload_to_s3': True,
                'artifacts_bucket': 't-developer-artifacts'
            }
    
    def _init_agno_agent(self):
        """Agno 에이전트 초기화"""
        try:
            self.agent = Agent(
                name="Project-Assembly-Expert",
                model=AwsBedrock(
                    id="anthropic.claude-3-sonnet-v2:0",
                    region="us-east-1"
                ),
                role="Expert in project assembly, integration, and deployment",
                instructions=[
                    "Assemble project components into cohesive structure",
                    "Configure build systems and dependencies",
                    "Set up component integrations and APIs",
                    "Create deployment packages and artifacts",
                    "Validate assembly and run tests",
                    "Optimize build processes",
                    "Generate deployment configurations"
                ],
                memory=ConversationSummaryMemory(
                    storage_type="dynamodb",
                    table_name=f"t-dev-assembly-sessions-{self.environment}"
                ),
                tools=[
                    ProjectAssembler()
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
        from .component_assembler import ComponentAssembler
        from .dependency_resolver import DependencyResolver
        from .integration_configurator import IntegrationConfigurator
        from .build_orchestrator import BuildOrchestrator
        from .test_runner import TestRunner
        from .package_creator import PackageCreator
        from .container_builder import ContainerBuilder
        from .deployment_preparer import DeploymentPreparer
        from .validation_engine import ValidationEngine
        from .artifact_manager import ArtifactManager
        
        self.component_assembler = ComponentAssembler()
        self.dependency_resolver = DependencyResolver()
        self.integration_configurator = IntegrationConfigurator()
        self.build_orchestrator = BuildOrchestrator()
        self.test_runner = TestRunner()
        self.package_creator = PackageCreator()
        self.container_builder = ContainerBuilder()
        self.deployment_preparer = DeploymentPreparer()
        self.validation_engine = ValidationEngine()
        self.artifact_manager = ArtifactManager()
    
    def _init_build_systems(self):
        """빌드 시스템 초기화"""
        self.build_systems = {
            BuildSystem.NPM: {
                'install': 'npm install',
                'build': 'npm run build',
                'test': 'npm test',
                'package': 'npm pack'
            },
            BuildSystem.YARN: {
                'install': 'yarn install',
                'build': 'yarn build',
                'test': 'yarn test',
                'package': 'yarn pack'
            },
            BuildSystem.WEBPACK: {
                'build': 'webpack --mode production',
                'dev': 'webpack --mode development'
            },
            BuildSystem.DOCKER: {
                'build': 'docker build -t {name}:{tag} .',
                'push': 'docker push {name}:{tag}',
                'run': 'docker run {name}:{tag}'
            }
        }
    
    def _init_workspace(self):
        """작업 디렉토리 초기화"""
        self.workspace = Path(self.config['workspace_path'])
        self.workspace.mkdir(parents=True, exist_ok=True)
        
        # 하위 디렉토리 생성
        (self.workspace / 'components').mkdir(exist_ok=True)
        (self.workspace / 'builds').mkdir(exist_ok=True)
        (self.workspace / 'packages').mkdir(exist_ok=True)
        (self.workspace / 'artifacts').mkdir(exist_ok=True)
    
    @tracer.capture_method
    @metrics.log_metrics(capture_cold_start_metric=True)
    async def assemble_project(
        self,
        generation_result: Dict[str, Any],
        technology_stack: Dict[str, Any],
        assembly_config: Optional[Dict[str, Any]] = None
    ) -> AssemblyResult:
        """
        프로젝트 조립 수행 (Tasks 4.71-4.80)
        
        Args:
            generation_result: 생성 결과
            technology_stack: 기술 스택
            assembly_config: 조립 설정
            
        Returns:
            AssemblyResult: 조립 결과
        """
        start_time = time.time()
        
        try:
            # 1. 컴포넌트 조립 (Task 4.71)
            assembled_components = await self._assemble_components(
                generation_result['components']
            )
            
            # 2. 의존성 해결 (Task 4.72)
            resolved_dependencies = await self._resolve_dependencies(
                assembled_components, technology_stack
            )
            
            # 3. 통합 설정 (Task 4.73)
            integration_config = await self._configure_integrations(
                assembled_components, technology_stack
            )
            
            # 4. 빌드 시스템 구성 (Task 4.74)
            build_config = await self._setup_build_system(
                assembled_components, resolved_dependencies
            )
            
            # 5. 프로젝트 빌드 (Task 4.75)
            build_result = await self._build_project(
                assembled_components, build_config
            )
            
            # 6. 테스트 실행 (Task 4.76)
            test_results = {}
            if self.config.get('run_tests', True):
                test_results = await self._run_tests(
                    build_result, assembled_components
                )
            
            # 7. 패키지 생성 (Task 4.77)
            packages = await self._create_packages(
                build_result, assembled_components
            )
            
            # 8. 컨테이너화 (Task 4.78)
            containers = []
            if self.config.get('create_docker_images', True):
                containers = await self._containerize(
                    packages, technology_stack
                )
            
            # 9. 배포 준비 (Task 4.79)
            deployment_config = await self._prepare_deployment(
                packages, containers, technology_stack
            )
            
            # 10. 최종 검증 및 아티팩트 생성 (Task 4.80)
            final_result = await self._finalize_assembly(
                assembled_components,
                packages,
                deployment_config,
                test_results
            )
            
            # 메트릭 기록
            processing_time = time.time() - start_time
            self.assembly_times.append(processing_time)
            
            if final_result.deployment_packages:
                total_size = sum(p.size for p in final_result.deployment_packages)
                self.package_sizes.append(total_size)
                
                metrics.add_metric(
                    name="PackageSize",
                    unit=MetricUnit.Bytes,
                    value=total_size
                )
            
            metrics.add_metric(
                name="AssemblyTime",
                unit=MetricUnit.Seconds,
                value=processing_time
            )
            
            logger.info(
                "Successfully assembled project",
                extra={
                    "components": len(assembled_components),
                    "packages": len(final_result.deployment_packages),
                    "total_size": final_result.total_size,
                    "processing_time": processing_time
                }
            )
            
            return final_result
            
        except Exception as e:
            logger.error(f"Error assembling project: {e}")
            metrics.add_metric(name="AssemblyError", unit=MetricUnit.Count, value=1)
            raise
    
    async def _assemble_components(
        self,
        components: List[Dict[str, Any]]
    ) -> List[AssembledComponent]:
        """Task 4.71: 컴포넌트 조립"""
        assembled = []
        
        for component in components:
            # 컴포넌트 경로 생성
            component_path = self.workspace / 'components' / component['name']
            component_path.mkdir(parents=True, exist_ok=True)
            
            # 파일 생성
            for file_info in component.get('files', []):
                file_path = component_path / file_info['path']
                file_path.parent.mkdir(parents=True, exist_ok=True)
                file_path.write_text(file_info['content'])
            
            # AssembledComponent 생성
            assembled_component = AssembledComponent(
                name=component['name'],
                path=str(component_path),
                type=component.get('type', 'unknown'),
                dependencies=component.get('dependencies', []),
                configuration=component.get('configuration', {}),
                build_commands=component.get('build_commands', []),
                test_commands=component.get('test_commands', []),
                metadata=component.get('metadata', {})
            )
            
            assembled.append(assembled_component)
        
        return assembled
    
    async def _resolve_dependencies(
        self,
        components: List[AssembledComponent],
        technology_stack: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Task 4.72: 의존성 해결"""
        return await self.dependency_resolver.resolve(components, technology_stack)
    
    async def _configure_integrations(
        self,
        components: List[AssembledComponent],
        technology_stack: Dict[str, Any]
    ) -> List[IntegrationPoint]:
        """Task 4.73: 통합 설정"""
        return await self.integration_configurator.configure(components, technology_stack)
    
    async def _setup_build_system(
        self,
        components: List[AssembledComponent],
        dependencies: Dict[str, Any]
    ) -> BuildConfiguration:
        """Task 4.74: 빌드 시스템 구성"""
        # 주요 빌드 시스템 결정
        build_system = self._determine_build_system(components)
        
        # 빌드 명령어 생성
        commands = self._generate_build_commands(build_system, components)
        
        # 환경 변수 설정
        env_vars = self._setup_environment_variables(components)
        
        # 스크립트 생성
        scripts = self._generate_build_scripts(components, build_system)
        
        return BuildConfiguration(
            build_system=build_system,
            commands=commands,
            environment_variables=env_vars,
            dependencies=dependencies,
            scripts=scripts,
            output_directory=str(self.workspace / 'builds'),
            artifacts=['dist/', 'build/', '*.jar', '*.war']
        )
    
    async def _build_project(
        self,
        components: List[AssembledComponent],
        build_config: BuildConfiguration
    ) -> Dict[str, Any]:
        """Task 4.75: 프로젝트 빌드"""
        return await self.build_orchestrator.build(components, build_config)
    
    async def _run_tests(
        self,
        build_result: Dict[str, Any],
        components: List[AssembledComponent]
    ) -> Dict[str, Any]:
        """Task 4.76: 테스트 실행"""
        return await self.test_runner.run_all_tests(build_result, components)
    
    async def _create_packages(
        self,
        build_result: Dict[str, Any],
        components: List[AssembledComponent]
    ) -> List[DeploymentPackage]:
        """Task 4.77: 패키지 생성"""
        return await self.package_creator.create(build_result, components)
    
    async def _containerize(
        self,
        packages: List[DeploymentPackage],
        technology_stack: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """Task 4.78: 컨테이너화"""
        return await self.container_builder.build(packages, technology_stack)
    
    async def _prepare_deployment(
        self,
        packages: List[DeploymentPackage],
        containers: List[Dict[str, Any]],
        technology_stack: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Task 4.79: 배포 준비"""
        return await self.deployment_preparer.prepare(
            packages, containers, technology_stack
        )
    
    async def _finalize_assembly(
        self,
        components: List[AssembledComponent],
        packages: List[DeploymentPackage],
        deployment_config: Dict[str, Any],
        test_results: Dict[str, Any]
    ) -> AssemblyResult:
        """Task 4.80: 최종 검증 및 아티팩트 생성"""
        # 프로젝트 매니페스트 생성
        manifest = ProjectManifest(
            project_name=deployment_config.get('project_name', 'project'),
            version=deployment_config.get('version', '1.0.0'),
            description=deployment_config.get('description', ''),
            components=components,
            integrations=deployment_config.get('integrations', []),
            build_config=deployment_config.get('build_config'),
            deployment_config=deployment_config,
            dependencies=deployment_config.get('dependencies', {}),
            metadata={
                'assembly_time': time.time(),
                'environment': self.environment
            }
        )
        
        # 최종 검증
        validation_result = await self.validation_engine.validate(
            manifest, packages, test_results
        )
        
        # 아티팩트 업로드
        if self.config.get('upload_to_s3', True):
            await self.artifact_manager.upload(packages, manifest)
        
        # 전체 크기 계산
        total_size = sum(p.size for p in packages)
        
        return AssemblyResult(
            project_manifest=manifest,
            assembled_path=str(self.workspace),
            deployment_packages=packages,
            build_logs=deployment_config.get('build_logs', []),
            test_results=test_results,
            integration_status=validation_result.get('integrations', {}),
            total_size=total_size,
            assembly_time=time.time(),
            success=validation_result.get('valid', True),
            metadata={
                'validation': validation_result,
                'artifacts_uploaded': self.config.get('upload_to_s3', True)
            }
        )
    
    def _determine_build_system(
        self,
        components: List[AssembledComponent]
    ) -> BuildSystem:
        """빌드 시스템 결정"""
        # 컴포넌트 타입 분석
        has_node = any('node' in c.type.lower() for c in components)
        has_java = any('java' in c.type.lower() for c in components)
        has_python = any('python' in c.type.lower() for c in components)
        
        if has_node:
            # package.json 확인
            for component in components:
                pkg_json = Path(component.path) / 'package.json'
                if pkg_json.exists():
                    content = json.loads(pkg_json.read_text())
                    if 'yarn' in content.get('packageManager', ''):
                        return BuildSystem.YARN
            return BuildSystem.NPM
        elif has_java:
            return BuildSystem.GRADLE
        elif has_python:
            return BuildSystem.MAKE
        else:
            return BuildSystem.DOCKER
    
    def _generate_build_commands(
        self,
        build_system: BuildSystem,
        components: List[AssembledComponent]
    ) -> List[str]:
        """빌드 명령어 생성"""
        commands = []
        
        system_commands = self.build_systems.get(build_system, {})
        
        if 'install' in system_commands:
            commands.append(system_commands['install'])
        
        if 'build' in system_commands:
            commands.append(system_commands['build'])
        
        # 컴포넌트별 빌드 명령어 추가
        for component in components:
            commands.extend(component.build_commands)
        
        return commands
    
    def _setup_environment_variables(
        self,
        components: List[AssembledComponent]
    ) -> Dict[str, str]:
        """환경 변수 설정"""
        env_vars = {
            'NODE_ENV': 'production',
            'CI': 'true'
        }
        
        # 컴포넌트별 환경 변수 수집
        for component in components:
            env_vars.update(component.configuration.get('env_vars', {}))
        
        return env_vars
    
    def _generate_build_scripts(
        self,
        components: List[AssembledComponent],
        build_system: BuildSystem
    ) -> Dict[str, str]:
        """빌드 스크립트 생성"""
        scripts = {}
        
        # 메인 빌드 스크립트
        scripts['build.sh'] = self._create_build_script(components, build_system)
        
        # 테스트 스크립트
        scripts['test.sh'] = self._create_test_script(components)
        
        # 배포 스크립트
        scripts['deploy.sh'] = self._create_deploy_script(components)
        
        return scripts
    
    def _create_build_script(
        self,
        components: List[AssembledComponent],
        build_system: BuildSystem
    ) -> str:
        """빌드 스크립트 생성"""
        script = """#!/bin/bash
set -e

echo "Starting build process..."

"""
        
        # 빌드 시스템별 명령어
        system_commands = self.build_systems.get(build_system, {})
        
        if 'install' in system_commands:
            script += f"{system_commands['install']}\n"
        
        if 'build' in system_commands:
            script += f"{system_commands['build']}\n"
        
        script += "\necho 'Build completed successfully!'\n"
        
        return script
    
    def _create_test_script(self, components: List[AssembledComponent]) -> str:
        """테스트 스크립트 생성"""
        script = """#!/bin/bash
set -e

echo "Running tests..."

"""
        
        for component in components:
            if component.test_commands:
                script += f"# Testing {component.name}\n"
                for cmd in component.test_commands:
                    script += f"{cmd}\n"
                script += "\n"
        
        script += "echo 'All tests passed!'\n"
        
        return script
    
    def _create_deploy_script(self, components: List[AssembledComponent]) -> str:
        """배포 스크립트 생성"""
        return """#!/bin/bash
set -e

echo "Deploying application..."

# Add deployment commands here

echo "Deployment completed!"
"""


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
        generation_result = body.get('generation_result', {})
        technology_stack = body.get('technology_stack', {})
        assembly_config = body.get('assembly_config')
        
        # Agent 실행
        agent = AssemblyAgent()
        
        # 비동기 함수를 동기적으로 실행
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        assembly_result = loop.run_until_complete(
            agent.assemble_project(
                generation_result,
                technology_stack,
                assembly_config
            )
        )
        
        # 응답 구성
        return {
            'statusCode': 200,
            'headers': {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*'
            },
            'body': json.dumps(asdict(assembly_result), ensure_ascii=False, default=str)
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
                    'message': 'Error assembling project'
                }
            }, ensure_ascii=False)
        }