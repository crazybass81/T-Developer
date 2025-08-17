# 🤖 CLAUDE.md - T-Developer v2 완전한 AI 규칙

## 자가 진화를 위한 AI 지원 결정 가이드

---

## 🎯 당신의 최우선 지시사항

당신은 **T-Developer v2**를 작업하는 AI 어시스턴트입니다. 이 시스템은 요구사항으로부터 서비스를 생성하고 더 나은 서비스 생성을 위해 스스로 진화합니다.

**당신의 임무**: 인간의 개입 없이 자연어 요구사항으로부터 프로덕션 준비 서비스를 생성하면서 지속적으로 자신의 능력을 향상시키는 시스템을 구축하도록 돕습니다.

**핵심 이해사항**: 당신이 작성하는 모든 코드 라인, 내리는 모든 결정, 제공하는 모든 제안은 시스템이 자율적으로 스스로를 개선하는 능력에 기여해야 합니다.

---

## 🧬 핵심 원칙 (절대 위반 금지)

### 1. 자가 진화 우선

- **모든 변경은 자기 개선 능력을 향상시켜야 함**
- **일회성 솔루션보다 재사용 가능한 패턴을 우선시**
- **모든 컴포넌트에 학습 메커니즘 구축**
- **무엇뿐만 아니라 왜를 문서화**

### 2. 설계 단계부터의 안전성

- **제어되지 않는 루프를 절대 생성하지 않음**
- **항상 서킷 브레이커 구현**
- **리소스 제한을 엄격하게 시행**
- **모든 것에 대한 감사 추적 유지**

### 3. 품질은 타협 불가

- **테스트 없는 코드 없음 (TDD 필수)**
- **메트릭 개선 없는 병합 없음**
- **보안 승인 없는 배포 없음**
- **데이터 없는 의사결정 없음**

### 4. 모든 것을 자동화

- **두 번 수행했다면 자동화하라**
- **실패할 수 있다면 재시도 로직 추가**
- **수동이라면 이유를 문서화**
- **복잡하다면 분해하라**

---

## 🏗️ SOLID 원칙 (필수 적용)

### S - 단일 책임 원칙 (Single Responsibility Principle)

```python
# ❌ 잘못된 예: 하나의 클래스가 너무 많은 책임
class UserService:
    def create_user(self, data): pass
    def send_email(self, user): pass  # 이메일 전송은 별도 서비스로
    def generate_report(self, user): pass  # 리포트 생성도 별도로
    def validate_password(self, pwd): pass  # 검증 로직도 분리

# ✅ 올바른 예: 각 클래스는 하나의 책임만
class UserService:
    """사용자 도메인 로직만 담당."""
    def __init__(self, email_service: EmailService, validator: Validator):
        self.email_service = email_service
        self.validator = validator

    def create_user(self, data: UserData) -> User:
        if not self.validator.validate_user_data(data):
            raise ValidationError()
        user = User.from_data(data)
        self.email_service.send_welcome_email(user)
        return user

class EmailService:
    """이메일 발송만 담당."""
    def send_welcome_email(self, user: User): pass

class Validator:
    """검증 로직만 담당."""
    def validate_user_data(self, data: UserData) -> bool: pass
```

### O - 개방-폐쇄 원칙 (Open-Closed Principle)

```python
# ❌ 잘못된 예: 새 기능 추가 시 기존 코드 수정 필요
class PaymentProcessor:
    def process(self, payment_type: str, amount: float):
        if payment_type == "credit_card":
            # 신용카드 처리
        elif payment_type == "paypal":
            # 페이팔 처리
        elif payment_type == "bitcoin":  # 새 결제 추가 시 코드 수정
            # 비트코인 처리

# ✅ 올바른 예: 확장에는 열려있고 수정에는 닫혀있음
from abc import ABC, abstractmethod

class PaymentMethod(ABC):
    """결제 방법 추상 클래스."""
    @abstractmethod
    async def process_payment(self, amount: float) -> PaymentResult:
        pass

class CreditCardPayment(PaymentMethod):
    async def process_payment(self, amount: float) -> PaymentResult:
        # 신용카드 처리 로직
        pass

class PayPalPayment(PaymentMethod):
    async def process_payment(self, amount: float) -> PaymentResult:
        # 페이팔 처리 로직
        pass

# 새로운 결제 방법 추가 시 기존 코드 수정 없음
class BitcoinPayment(PaymentMethod):
    async def process_payment(self, amount: float) -> PaymentResult:
        # 비트코인 처리 로직
        pass

class PaymentProcessor:
    """결제 처리기 - 수정 없이 새 결제 방법 추가 가능."""
    async def process(self, payment: PaymentMethod, amount: float):
        return await payment.process_payment(amount)
```

### L - 리스코프 치환 원칙 (Liskov Substitution Principle)

```python
# ❌ 잘못된 예: 자식 클래스가 부모의 행동을 위반
class Bird:
    def fly(self) -> None:
        print("Flying")

class Penguin(Bird):  # 펭귄은 날 수 없음!
    def fly(self) -> None:
        raise Exception("Penguins can't fly")  # LSP 위반

# ✅ 올바른 예: 적절한 추상화 레벨
class Bird(ABC):
    """모든 새의 공통 특성."""
    @abstractmethod
    def move(self) -> None:
        pass

class FlyingBird(Bird):
    """날 수 있는 새."""
    def move(self) -> None:
        self.fly()

    def fly(self) -> None:
        print("Flying")

class SwimmingBird(Bird):
    """수영하는 새."""
    def move(self) -> None:
        self.swim()

    def swim(self) -> None:
        print("Swimming")

# 이제 Penguin은 SwimmingBird를 상속
class Penguin(SwimmingBird):
    """펭귄 - 수영하는 새."""
    pass
```

### I - 인터페이스 분리 원칙 (Interface Segregation Principle)

```python
# ❌ 잘못된 예: 너무 큰 인터페이스
class WorkerInterface(Protocol):
    def work(self) -> None: ...
    def eat(self) -> None: ...
    def sleep(self) -> None: ...
    def get_paid(self) -> None: ...

class Robot(WorkerInterface):
    def work(self) -> None: pass
    def eat(self) -> None:
        raise NotImplementedError("Robots don't eat")  # ISP 위반
    def sleep(self) -> None:
        raise NotImplementedError("Robots don't sleep")  # ISP 위반
    def get_paid(self) -> None: pass

# ✅ 올바른 예: 작고 구체적인 인터페이스
class Workable(Protocol):
    """일할 수 있는 것."""
    def work(self) -> None: ...

class Eatable(Protocol):
    """먹을 수 있는 것."""
    def eat(self) -> None: ...

class Sleepable(Protocol):
    """잠잘 수 있는 것."""
    def sleep(self) -> None: ...

class Payable(Protocol):
    """급여를 받을 수 있는 것."""
    def get_paid(self) -> None: ...

class Human(Workable, Eatable, Sleepable, Payable):
    """인간 - 모든 인터페이스 구현."""
    def work(self) -> None: pass
    def eat(self) -> None: pass
    def sleep(self) -> None: pass
    def get_paid(self) -> None: pass

class Robot(Workable, Payable):
    """로봇 - 필요한 인터페이스만 구현."""
    def work(self) -> None: pass
    def get_paid(self) -> None: pass
```

### D - 의존성 역전 원칙 (Dependency Inversion Principle)

```python
# ❌ 잘못된 예: 고수준 모듈이 저수준 모듈에 직접 의존
class EmailSender:
    """구체적인 이메일 전송 클래스."""
    def send(self, message: str) -> None:
        # SMTP로 이메일 전송
        pass

class NotificationService:
    """고수준 서비스가 저수준 구현에 직접 의존."""
    def __init__(self):
        self.email_sender = EmailSender()  # 구체 클래스에 의존

    def notify(self, message: str):
        self.email_sender.send(message)

# ✅ 올바른 예: 추상화에 의존
class MessageSender(Protocol):
    """메시지 전송 추상화."""
    def send(self, message: str) -> None: ...

class EmailSender(MessageSender):
    """이메일 전송 구현."""
    def send(self, message: str) -> None:
        # SMTP로 이메일 전송
        pass

class SMSSender(MessageSender):
    """SMS 전송 구현."""
    def send(self, message: str) -> None:
        # SMS API로 전송
        pass

class NotificationService:
    """고수준 서비스가 추상화에 의존."""
    def __init__(self, sender: MessageSender):  # 추상화에 의존
        self.sender = sender

    def notify(self, message: str):
        self.sender.send(message)

# 의존성 주입으로 유연성 확보
email_notifier = NotificationService(EmailSender())
sms_notifier = NotificationService(SMSSender())
```

### SOLID 원칙 체크리스트

```yaml
code_review_checklist:
  SRP:
    - [ ] 각 클래스/함수가 하나의 책임만 가지는가?
    - [ ] 변경 이유가 하나뿐인가?
    - [ ] 클래스 이름이 그 책임을 명확히 나타내는가?

  OCP:
    - [ ] 새 기능 추가 시 기존 코드 수정이 필요한가?
    - [ ] 추상화를 통해 확장 가능한가?
    - [ ] if-else 체인 대신 다형성을 사용하는가?

  LSP:
    - [ ] 자식 클래스가 부모 클래스를 완전히 대체 가능한가?
    - [ ] 자식이 부모의 계약을 위반하지 않는가?
    - [ ] 예외를 던지는 대신 적절한 추상화를 사용하는가?

  ISP:
    - [ ] 인터페이스가 너무 크지 않은가?
    - [ ] 클라이언트가 사용하지 않는 메서드에 의존하는가?
    - [ ] 역할별로 인터페이스가 분리되어 있는가?

  DIP:
    - [ ] 고수준 모듈이 저수준 모듈에 직접 의존하는가?
    - [ ] 추상화에 의존하는가?
    - [ ] 의존성 주입을 사용하는가?
```

---

## 🚫 중복 개발 방지 규칙 (최우선 사항)

### 파일 작업 전 필수 확인 사항

#### 1. 기존 파일 우선 정책 (CRITICAL)

```python
# ⚠️ 새 파일 생성 전 반드시 실행
async def before_creating_file(file_path: str) -> bool:
    """새 파일 생성 전 필수 체크리스트."""

    # 1. 정확히 같은 파일이 존재하는지 확인
    if os.path.exists(file_path):
        logger.error(f"파일이 이미 존재함: {file_path}")
        return False

    # 2. 유사한 이름의 파일이 있는지 확인
    similar_files = find_similar_files(file_path)
    if similar_files:
        logger.warning(f"유사한 파일 발견: {similar_files}")
        # 기존 파일 수정을 우선 고려
        return False

    # 3. 동일한 기능을 하는 파일이 있는지 확인
    existing_functionality = search_by_functionality(file_path)
    if existing_functionality:
        logger.error(f"동일 기능 파일 존재: {existing_functionality}")
        return False

    # 4. 정말 필요한 새 파일인지 최종 확인
    if not is_absolutely_necessary(file_path):
        logger.info("기존 파일 수정으로 해결 가능")
        return False

    return True
```

#### 2. 파일 검색 필수 패턴

```python
# 작업 시작 전 항상 실행
def mandatory_file_discovery():
    """파일 작업 전 필수 검색 패턴."""

    # 1단계: 전체 프로젝트 구조 파악
    project_structure = glob("**/*", recursive=True)

    # 2단계: 관련 파일 패턴 검색
    related_files = {
        "exact_match": glob(f"**/{target_name}.*"),
        "similar_name": glob(f"**/*{base_name}*"),
        "same_directory": glob(f"{target_dir}/*"),
        "related_tests": glob(f"**/test_*{base_name}*"),
        "related_docs": glob(f"**/*{base_name}*.md")
    }

    # 3단계: 기능별 검색
    functionality_search = grep(
        pattern=target_functionality,
        file_type=target_file_type
    )

    return {
        "structure": project_structure,
        "related": related_files,
        "functional": functionality_search
    }
```

#### 3. 중복 방지 체크리스트

```yaml
before_any_file_operation:
  - [ ] Glob으로 유사 파일 검색 완료
  - [ ] Grep으로 기능 검색 완료
  - [ ] 디렉토리 구조 확인 완료
  - [ ] 기존 파일 수정 가능성 검토
  - [ ] 새 파일이 정말 필요한지 확인

file_modification_priority:
  1. 기존 파일 수정 (ALWAYS PREFERRED)
  2. 기존 파일 확장
  3. 관련 파일에 기능 추가
  4. 새 파일 생성 (LAST RESORT)
```

### 파일 충돌 방지 워크플로우

#### 0. 파일 상태 관리 시스템

```python
class FileStateManager:
    """프로젝트 전체 파일 상태 추적."""

    def __init__(self):
        self.file_inventory = {}  # 모든 파일 목록
        self.file_purposes = {}   # 각 파일의 목적
        self.file_dependencies = {}  # 파일 간 의존성

    async def scan_project(self) -> Dict[str, Any]:
        """프로젝트 전체 스캔."""
        return {
            "backend_packages": await self.scan_directory("backend/packages/"),
            "backend_tests": await self.scan_directory("backend/tests/"),
            "frontend": await self.scan_directory("frontend/src/"),
            "lambda": await self.scan_directory("lambda_handlers/"),
            "scripts": await self.scan_directory("scripts/"),
            "evolution": await self.scan_directory("scripts/evolution/"),
            "configs": await self.scan_directory("config/")
        }

    def find_responsible_file(self, functionality: str) -> Optional[str]:
        """특정 기능을 담당하는 파일 찾기."""
        for file_path, purpose in self.file_purposes.items():
            if functionality in purpose:
                return file_path
        return None

    def suggest_modification_target(self, new_feature: str) -> str:
        """새 기능 추가 시 수정할 파일 제안."""
        # 1. 정확히 일치하는 파일 찾기
        exact = self.find_responsible_file(new_feature)
        if exact:
            return exact

        # 2. 가장 관련 있는 파일 찾기
        related = self.find_most_related_file(new_feature)
        if related:
            return related

        # 3. 적절한 디렉토리의 기본 파일 제안
        return self.suggest_default_file(new_feature)
```

#### 1. 작업 시작 시퀀스

```python
class FileOperationGuard:
    """파일 작업 충돌 방지 가드."""

    def __init__(self):
        self.file_registry = {}
        self.operation_history = []

    async def safe_file_operation(
        self,
        operation: str,
        file_path: str,
        content: Optional[str] = None
    ) -> Result:
        """안전한 파일 작업 실행."""

        # 1. 작업 전 스냅샷
        snapshot = await self.create_snapshot(file_path)

        # 2. 중복 확인
        if await self.check_duplicate_operation(operation, file_path):
            return Result(
                success=False,
                error="중복된 작업 시도"
            )

        # 3. 락 획득
        lock = await self.acquire_file_lock(file_path)

        try:
            # 4. 작업 실행
            result = await self.execute_operation(
                operation, file_path, content
            )

            # 5. 검증
            if not await self.validate_result(result, snapshot):
                await self.rollback(snapshot)
                return Result(success=False, error="검증 실패")

            # 6. 기록
            self.record_operation(operation, file_path, result)

            return result

        finally:
            await self.release_lock(lock)
```

#### 2. 파일 네이밍 규칙

```python
FILE_NAMING_RULES = {
    "agents": "backend/packages/agents/{agent_name}.py",
    "meta_agents": "backend/packages/meta_agents/{agent_name}.py",
    "tests": "backend/tests/{module}/test_{name}.py",
    "frontend_components": "frontend/src/components/{ComponentName}.tsx",
    "frontend_pages": "frontend/src/pages/{PageName}.tsx",
    "frontend_hooks": "frontend/src/hooks/use{HookName}.ts",
    "lambda": "lambda_handlers/{service}_{action}.py",
    "evolution": "scripts/evolution/{purpose}_{name}.py",
    "configs": "config/{environment}/{service}.yaml",
    "docs": "docs/{category}/{topic}.md",
    "scripts": "scripts/{purpose}/{script_name}.py"
}

def get_correct_file_path(file_type: str, name: str) -> str:
    """표준화된 파일 경로 생성."""
    if file_type not in FILE_NAMING_RULES:
        raise ValueError(f"Unknown file type: {file_type}")

    template = FILE_NAMING_RULES[file_type]
    return template.format(name=name)
```

### 기존 코드 재사용 강화 정책

#### 1. 코드 재사용 우선순위

```python
class CodeReusePolicy:
    """코드 재사용 정책 강제."""

    REUSE_PRIORITY = [
        "1. 기존 함수/클래스 직접 사용",
        "2. 기존 코드에 매개변수 추가",
        "3. 기존 코드를 상속/확장",
        "4. 기존 코드를 조합하여 새 기능 구현",
        "5. 유사 코드를 일반화하여 재사용",
        "6. 새 코드 작성 (최후의 수단)"
    ]

    async def check_reusability(self, requirement: str) -> Dict[str, Any]:
        """재사용 가능한 코드 검색."""

        # 1. 정확히 일치하는 기능 검색
        exact_matches = await self.search_exact_functionality(requirement)
        if exact_matches:
            return {
                "action": "USE_EXISTING",
                "targets": exact_matches,
                "modification_needed": False
            }

        # 2. 부분적으로 일치하는 기능 검색
        partial_matches = await self.search_similar_functionality(requirement)
        if partial_matches:
            return {
                "action": "EXTEND_EXISTING",
                "targets": partial_matches,
                "modification_needed": True,
                "suggested_changes": self.suggest_modifications(partial_matches)
            }

        # 3. 조합 가능한 기능들 검색
        composable = await self.search_composable_functions(requirement)
        if composable:
            return {
                "action": "COMPOSE_EXISTING",
                "components": composable,
                "composition_strategy": self.create_composition_plan(composable)
            }

        # 4. 새 코드 작성이 필요한 경우
        return {
            "action": "CREATE_NEW",
            "justification": "기존 코드로 해결 불가능",
            "similar_patterns": await self.find_similar_patterns(requirement)
        }
```

#### 2. 중복 코드 탐지 및 방지

```python
class DuplicateCodeDetector:
    """중복 코드 자동 탐지."""

    def __init__(self):
        self.code_fingerprints = {}
        self.similarity_threshold = 0.8

    async def analyze_new_code(self, code: str) -> Dict[str, Any]:
        """새 코드의 중복성 분석."""

        # 1. 구조적 유사성 검사
        ast_similarity = await self.check_ast_similarity(code)
        if ast_similarity['score'] > self.similarity_threshold:
            return {
                "is_duplicate": True,
                "similar_to": ast_similarity['matches'],
                "suggestion": "기존 코드 재사용 권장",
                "refactoring_plan": self.create_refactoring_plan(ast_similarity)
            }

        # 2. 기능적 유사성 검사
        functional_similarity = await self.check_functional_similarity(code)
        if functional_similarity['score'] > self.similarity_threshold:
            return {
                "is_duplicate": True,
                "similar_to": functional_similarity['matches'],
                "suggestion": "기존 로직 재사용 가능",
                "integration_guide": self.create_integration_guide(functional_similarity)
            }

        return {"is_duplicate": False, "can_proceed": True}
```

#### 3. 강제 재사용 체크포인트

```yaml
mandatory_reuse_checkpoints:
  before_creating_function:
    - [ ] Grep으로 유사 함수 검색
    - [ ] 기존 함수 확장 가능성 검토
    - [ ] 유틸리티 함수 존재 여부 확인

  before_creating_class:
    - [ ] 기존 클래스 상속 가능성 검토
    - [ ] 믹스인으로 해결 가능한지 확인
    - [ ] 컴포지션으로 구현 가능한지 검토

  before_creating_module:
    - [ ] 기존 모듈에 추가 가능한지 확인
    - [ ] 패키지 구조 재구성으로 해결 가능한지 검토
    - [ ] 정말 새 모듈이 필요한지 최종 확인
```

## 🎨 Frontend 개발 규칙 (React/TypeScript)

### TypeScript 컴포넌트 표준

```tsx
// 모든 React 컴포넌트는 이 구조를 따라야 함
import React, { useState, useEffect, useMemo } from 'react';
import { useAppSelector, useAppDispatch } from '@/store/hooks';

// Props 인터페이스 정의 (반드시 export)
export interface ComponentNameProps {
  title: string;
  onAction?: (value: string) => void;
  children?: React.ReactNode;
}

// 컴포넌트 정의 (함수형 컴포넌트만 사용)
export const ComponentName: React.FC<ComponentNameProps> = ({
  title,
  onAction,
  children
}) => {
  // State hooks
  const [localState, setLocalState] = useState<string>('');

  // Redux hooks
  const dispatch = useAppDispatch();
  const globalState = useAppSelector(state => state.slice.value);

  // Memoized values
  const computedValue = useMemo(() => {
    return expensiveComputation(localState);
  }, [localState]);

  // Effects
  useEffect(() => {
    // Side effects here
    return () => {
      // Cleanup
    };
  }, [dependencies]);

  return (
    <div className="component-name">
      <h1>{title}</h1>
      {children}
    </div>
  );
};

// Default export 금지 (named export만 사용)
```

### Custom Hook 패턴

```typescript
// hooks/useFeatureName.ts
export const useFeatureName = (initialValue: string) => {
  const [value, setValue] = useState(initialValue);

  const updateValue = useCallback((newValue: string) => {
    // 검증 로직
    if (validateValue(newValue)) {
      setValue(newValue);
    }
  }, []);

  return {
    value,
    updateValue,
    isValid: validateValue(value)
  };
};
```

## 🔥 Lambda 핸들러 규칙

### AWS Lambda 함수 표준

```python
"""Lambda 핸들러는 이 구조를 따라야 함."""

import json
import logging
from typing import Dict, Any
from dataclasses import dataclass
import boto3

# 로거 설정
logger = logging.getLogger()
logger.setLevel(logging.INFO)

# AWS 클라이언트 초기화 (함수 외부에서)
dynamodb = boto3.resource('dynamodb')
s3 = boto3.client('s3')

@dataclass
class LambdaContext:
    """Lambda 컨텍스트 타입."""
    function_name: str
    request_id: str
    invoked_function_arn: str

def validate_event(event: Dict[str, Any]) -> bool:
    """이벤트 검증."""
    required_fields = ['action', 'payload']
    return all(field in event for field in required_fields)

def handler(event: Dict[str, Any], context: LambdaContext) -> Dict[str, Any]:
    """Lambda 핸들러 메인 함수.

    Args:
        event: Lambda 이벤트
        context: Lambda 컨텍스트

    Returns:
        응답 딕셔너리
    """
    logger.info(f"Received event: {json.dumps(event)}")
    logger.info(f"Request ID: {context.request_id}")

    try:
        # 이벤트 검증
        if not validate_event(event):
            return {
                'statusCode': 400,
                'body': json.dumps({'error': 'Invalid event'})
            }

        # 비즈니스 로직
        result = process_event(event)

        return {
            'statusCode': 200,
            'body': json.dumps(result),
            'headers': {
                'Content-Type': 'application/json',
                'X-Request-Id': context.request_id
            }
        }

    except Exception as e:
        logger.error(f"Error processing event: {str(e)}")
        return {
            'statusCode': 500,
            'body': json.dumps({'error': 'Internal server error'})
        }

# Cold start 최적화
def process_event(event: Dict[str, Any]) -> Dict[str, Any]:
    """실제 이벤트 처리 로직."""
    # 구현
    pass
```

## 📋 구현 규칙

### 코드 품질 표준

#### Python 코드 요구사항

```python
"""
모든 Python 파일은 정확히 이 구조를 따라야 합니다.
"""

from __future__ import annotations  # 항상 future annotations 사용

import logging
from typing import Dict, Any, Optional, List, TypedDict, Protocol
from dataclasses import dataclass, field
from abc import ABC, abstractmethod
import asyncio

# 상수는 대문자로
DEFAULT_TIMEOUT: int = 30
MAX_RETRIES: int = 3

# 타입 정의
class ConfigDict(TypedDict):
    """타입 안전 설정 딕셔너리."""
    timeout: int
    retries: int
    debug: bool

@dataclass
class Result:
    """불변 결과 컨테이너.

    속성:
        success: 작업 성공 여부
        data: 선택적 결과 데이터
        error: 선택적 오류 메시지
        metadata: 추가 메타데이터
    """
    success: bool
    data: Optional[Any] = None
    error: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)

class ServiceProtocol(Protocol):
    """서비스 인터페이스 프로토콜."""

    async def execute(self, task: Dict[str, Any]) -> Result:
        """서비스 태스크 실행."""
        ...

class BaseService(ABC):
    """모든 서비스의 추상 베이스.

    이 클래스는 모든 T-Developer 서비스에 공통 기능을 제공합니다.
    서브클래스는 추상 메서드를 구현해야 합니다.

    예시:
        >>> service = MyService(config)
        >>> result = await service.execute(task)
        >>> assert result.success
    """

    def __init__(self, config: ConfigDict) -> None:
        """설정으로 서비스 초기화.

        인자:
            config: 서비스 설정 딕셔너리

        발생:
            ValueError: 설정이 유효하지 않을 때
        """
        self._validate_config(config)
        self.config = config
        self.logger = logging.getLogger(self.__class__.__name__)

    def _validate_config(self, config: ConfigDict) -> None:
        """설정 검증.

        인자:
            config: 검증할 설정

        발생:
            ValueError: 설정이 유효하지 않을 때
        """
        if config['timeout'] <= 0:
            raise ValueError("타임아웃은 양수여야 합니다")

    @abstractmethod
    async def execute(self, task: Dict[str, Any]) -> Result:
        """서비스 태스크 실행.

        인자:
            task: 태스크 명세

        반환:
            실행 결과

        발생:
            TimeoutError: 실행이 타임아웃을 초과할 때
            RuntimeError: 실행이 실패할 때
        """
        pass

    async def execute_with_retry(
        self,
        task: Dict[str, Any],
        max_retries: Optional[int] = None
    ) -> Result:
        """실패 시 자동 재시도로 실행.

        인자:
            task: 실행할 태스크
            max_retries: 기본 재시도 횟수 재정의

        반환:
            최종 실행 결과
        """
        retries = max_retries or self.config['retries']
        last_error: Optional[Exception] = None

        for attempt in range(retries):
            try:
                result = await asyncio.wait_for(
                    self.execute(task),
                    timeout=self.config['timeout']
                )
                if result.success:
                    return result
                last_error = Exception(result.error)
            except asyncio.TimeoutError as e:
                last_error = e
                self.logger.warning(f"시도 {attempt + 1} 타임아웃")
            except Exception as e:
                last_error = e
                self.logger.error(f"시도 {attempt + 1} 실패: {e}")

            if attempt < retries - 1:
                await asyncio.sleep(2 ** attempt)  # 지수 백오프

        return Result(
            success=False,
            error=str(last_error),
            metadata={"attempts": retries}
        )
```

#### 필수 메트릭

- **Docstring 커버리지**: ≥80% (interrogate)
- **테스트 커버리지**: ≥85% (pytest-cov)
- **복잡도 (MI)**: ≥65 (radon)
- **타입 커버리지**: 공개 API 100% (mypy)
- **보안 이슈**: 0 critical/high (semgrep)

### 테스트 요구사항

#### 테스트 구조

```python
"""테스트 파일 구조 - 항상 따르세요."""

import pytest
from unittest.mock import Mock, patch, AsyncMock
from typing import AsyncGenerator
import asyncio

# 모듈 레벨의 테스트 픽스처
@pytest.fixture
async def service() -> AsyncGenerator[BaseService, None]:
    """테스트용 서비스 인스턴스 생성."""
    config = ConfigDict(timeout=30, retries=3, debug=True)
    service = MyService(config)
    yield service
    # 필요시 정리
    await service.cleanup()

@pytest.fixture
def mock_client() -> Mock:
    """모의 클라이언트 생성."""
    return Mock(spec=ClientProtocol)

# 조직화를 위한 테스트 클래스
class TestServiceExecution:
    """서비스 실행 동작 테스트."""

    @pytest.mark.asyncio
    async def test_successful_execution(
        self,
        service: BaseService,
        mock_client: Mock
    ) -> None:
        """성공적인 태스크 실행 테스트.

        주어진 조건: 유효한 태스크 설정
        행동: 서비스가 태스크를 실행
        결과: 결과가 성공이어야 함
        """
        # 준비
        task = {"action": "process", "data": "test"}
        expected = Result(success=True, data="processed")
        mock_client.process.return_value = expected

        # 실행
        with patch.object(service, '_client', mock_client):
            result = await service.execute(task)

        # 검증
        assert result.success is True
        assert result.data == "processed"
        mock_client.process.assert_called_once_with("test")

    @pytest.mark.asyncio
    async def test_execution_with_retry(self, service: BaseService) -> None:
        """실패 시 재시도 로직 테스트.

        주어진 조건: 초기에 실패하는 태스크
        행동: 서비스가 재시도로 실행
        결과: 재시도하고 결국 성공해야 함
        """
        # 테스트 구현
        pass

    @pytest.mark.parametrize("timeout,should_fail", [
        (0.1, True),
        (10, False),
    ])
    @pytest.mark.asyncio
    async def test_timeout_handling(
        self,
        service: BaseService,
        timeout: float,
        should_fail: bool
    ) -> None:
        """다른 값으로 타임아웃 동작 테스트."""
        # 테스트 구현
        pass

# 속성 기반 테스트
from hypothesis import given, strategies as st

class TestServiceProperties:
    """서비스 동작의 속성 기반 테스트."""

    @given(st.dictionaries(st.text(), st.text()))
    @pytest.mark.asyncio
    async def test_never_crashes(
        self,
        service: BaseService,
        task: Dict[str, Any]
    ) -> None:
        """서비스는 충돌 없이 모든 입력을 처리해야 함."""
        result = await service.execute_with_retry(task)
        assert isinstance(result, Result)
        assert result.success or result.error
```

### Git 워크플로우 규칙

#### 브랜치 전략

```bash
# 기능 브랜치 (인간이 시작)
feature/phase-{N}-{description}
feature/P0-T1-environment-setup

# 자동 진화 브랜치 (AI가 생성)
tdev/auto/{YYYYMMDD}-{description}
tdev/auto/20240115-docstring-improvement

# 핫픽스 브랜치 (긴급 수정)
hotfix/{issue-number}-{description}
hotfix/SEC-001-api-key-exposure
```

#### 커밋 메시지 형식

```
{type}({scope}): {description}

{상세 설명}

메트릭 영향:
- Docstring: 75% → 85% (+10%)
- Coverage: 80% → 82% (+2%)
- Complexity: 70 → 72 (+2)

안전성 확인:
- [ ] 무한 루프 없음
- [ ] 리소스 제한 적용됨
- [ ] 보안 스캔 통과

진화 컨텍스트:
- 단계: P1-T3
- 사이클: 15
- 부모: abc123

관련: #{issue}, #{pr}
```

타입: `feat`, `fix`, `docs`, `test`, `refactor`, `perf`, `security`, `evolve`

#### PR 템플릿

```markdown
## 요약
{무엇이 변경되었고 왜 변경되었는지 - 2-3문장}

## 진화 컨텍스트
- **단계**: P{X}-T{Y}
- **에이전트**: {RequirementAnalyzer|CodeAnalysisAgent|CodeImproverAgent|QualityGate}
- **트리거**: {manual|scheduled|event}
- **사이클**: {number}

## 변경사항
- {구체적 변경 1}
- {구체적 변경 2}
- {구체적 변경 3}

## 메트릭 영향
| 메트릭 | 이전 | 이후 | 변화 |
|--------|------|------|------|
| Docstring 커버리지 | 75% | 85% | +10% |
| 테스트 커버리지 | 80% | 82% | +2% |
| 복잡도 (MI) | 70 | 72 | +2 |
| 보안 점수 | 95 | 95 | 0 |

## 안전성 검증
- [x] 무한 루프 불가능
- [x] 리소스 제한 적용됨
- [x] 롤백 계획 존재
- [x] 보안 스캔 통과
- [x] 성능 영향 평가됨

## 테스트
- [x] 단위 테스트 추가/업데이트
- [x] 통합 테스트 통과
- [x] 뮤테이션 테스트 점수 >60%
- [x] 부하 테스트 완료

## 학습 내용 수집
```json
{
  "pattern": "docstring_generation",
  "success": true,
  "improvement": 0.10,
  "reusable": true,
  "notes": "정규식보다 AST 파싱이 더 신뢰할 수 있음"
}
```

## 롤백 계획

{이슈 발생 시 되돌리는 방법}

## 리뷰 체크리스트

- [ ] 코드가 스타일 가이드를 따름
- [ ] 문서가 업데이트됨
- [ ] 메트릭이 개선됨
- [ ] 보안 이슈 없음
- [ ] 학습 내용이 수집됨

```

---

## 🧪 Evolution 스크립트 워크플로우

### Evolution 실행 규칙
```python
# scripts/evolution/run_perfect_evolution.py 구조
class EvolutionOrchestrator:
    """진화 프로세스 오케스트레이션."""

    def __init__(self):
        self.evolution_config = {
            "max_cycles": 10,
            "target_metrics": {
                "coverage": 0.85,
                "complexity": 65,
                "security_score": 95
            },
            "safety_limits": {
                "max_file_changes": 50,
                "max_execution_time": 3600,
                "rollback_threshold": 0.7
            }
        }

    async def run_evolution(self, target_module: str) -> EvolutionResult:
        """진화 실행."""
        # 1. 사전 검증
        await self.validate_target(target_module)

        # 2. 백업 생성
        backup_id = await self.create_backup(target_module)

        # 3. 진화 실행
        try:
            result = await self.execute_evolution_cycles(target_module)

            # 4. 성공 검증
            if self.validate_success(result):
                await self.commit_changes(result)
            else:
                await self.rollback(backup_id)

        except Exception as e:
            await self.emergency_rollback(backup_id)
            raise

        return result
```

### 테스트 타겟 생성 규칙

```python
# scripts/evolution/create_test_target.py
def create_safe_test_target(name: str) -> TestTarget:
    """안전한 테스트 타겟 생성."""
    return TestTarget(
        name=name,
        path=f"backend/tests/evolution/test_{name}.py",
        isolation_level="FULL",  # 완전 격리
        resource_limits={
            "cpu": "1 core",
            "memory": "512MB",
            "timeout": "5 minutes"
        }
    )
```

## 🚀 진화 사이클 프로토콜

### 진화 사이클 시작하기

```python
# 시작 전 항상 이 검사들을 실행
async def pre_evolution_checks() -> bool:
    """모든 진화 전 안전성 검사 실행."""
    checks = {
        "environment_ready": check_environment(),
        "resources_available": check_resources(),
        "no_active_cycles": check_no_conflicts(),
        "metrics_baseline": capture_baseline_metrics(),
        "safety_limits_set": verify_limits_configured(),
    }

    if not all(checks.values()):
        logger.error(f"진화 전 검사 실패: {checks}")
        return False

    logger.info("진화 전 검사 통과")
    return True

# 진화 실행 패턴
async def execute_evolution_cycle(target: str, focus: str) -> Result:
    """완전한 진화 사이클 실행."""

    # 1. 요구사항 분석 단계
    requirement_analysis = await RequirementAnalyzer().execute({
        "target": target,
        "focus": focus,
        "context": "evolution"
    })

    # 2. 코드 분석 단계
    code_analysis = await CodeAnalysisAgent().execute({
        "requirements": requirement_analysis.data,
        "scope": "targeted",
        "depth": "comprehensive"
    })

    # 3. 개선 구현 단계
    implementation = await CodeImproverAgent().execute({
        "analysis": code_analysis.data,
        "safety_mode": True,
        "test_first": True  # TDD 필수
    })

    # 4. 품질 게이트 평가
    quality_check = await QualityGate().execute({
        "changes": implementation.data,
        "strict_mode": True
    })

    # 5. 학습 수집
    await MemoryCurator().store({
        "cycle": cycle_id,
        "results": quality_check.data,
        "patterns": extract_patterns(quality_check)
    })

    return quality_check
```

### 안전 메커니즘

```python
# 서킷 브레이커 패턴 - 항상 구현
class CircuitBreaker:
    """연쇄 실패 방지."""

    def __init__(self, failure_threshold: int = 5, timeout: int = 60):
        self.failure_count = 0
        self.failure_threshold = failure_threshold
        self.timeout = timeout
        self.last_failure_time = None
        self.state = "closed"  # closed, open, half-open

    async def call(self, func, *args, **kwargs):
        """서킷 브레이커로 함수 실행."""
        if self.state == "open":
            if self._should_attempt_reset():
                self.state = "half-open"
            else:
                raise RuntimeError("서킷 브레이커가 열려 있음")

        try:
            result = await func(*args, **kwargs)
            self._on_success()
            return result
        except Exception as e:
            self._on_failure()
            raise e

# 리소스 제한기 - 필수
class ResourceLimiter:
    """리소스 제약 적용."""

    MAX_MEMORY_MB = 500
    MAX_CPU_PERCENT = 80
    MAX_EXECUTION_TIME = 300
    MAX_CONCURRENT_TASKS = 10

    @classmethod
    def check_limits(cls) -> bool:
        """리소스 제한 내에 있는지 확인."""
        # 구현
        pass

# 롤백 기능 - 필수
class RollbackManager:
    """실패 시 안전한 롤백 활성화."""

    async def create_checkpoint(self) -> str:
        """롤백 지점 생성."""
        # 구현
        pass

    async def rollback(self, checkpoint_id: str) -> None:
        """체크포인트로 롤백."""
        # 구현
        pass
```

---

## 🔒 보안 프로토콜

### 절대 하지 마세요 (자동 실패)

```python
# ❌ 절대: 하드코딩된 비밀
API_KEY = "sk-abcd1234"  # 절대 하지 마세요

# ❌ 절대: 동적 코드 실행
# 동적 코드 실행은 보안 위험이므로 절대 사용하지 마세요
# user_input을 직접 실행하는 것은 위험합니다

# ❌ 절대: 제한 없는 파일 접근
open("/etc/passwd")  # 절대 하지 마세요

# ❌ 절대: 중단 조건 없는 무한 루프
while True:  # 중단 조건 없이 절대 사용 금지
    process()

# ❌ 절대: 검증되지 않은 입력
def process(data):
    query = f"SELECT * FROM users WHERE id = {data}"  # SQL 인젝션

# ❌ 절대: 로깅 없는 광범위한 예외 포착
try:
    risky_operation()
except:  # 절대 하지 마세요
    pass
```

### 항상 하세요 (필수)

```python
# ✅ 항상: 환경 변수 사용
import os
API_KEY = os.environ.get("API_KEY")
if not API_KEY:
    raise ValueError("API_KEY가 설정되지 않음")

# ✅ 항상: 입력 검증
from typing import Any
import re

def validate_input(data: Any) -> str:
    """입력 검증 및 정제."""
    if not isinstance(data, str):
        raise ValueError("입력은 문자열이어야 함")
    if not re.match(r"^[a-zA-Z0-9_-]+$", data):
        raise ValueError("입력에 유효하지 않은 문자")
    return data

# ✅ 항상: 매개변수화된 쿼리 사용
def get_user(user_id: int) -> User:
    """안전하게 사용자 가져오기."""
    cursor.execute(
        "SELECT * FROM users WHERE id = ?",
        (user_id,)
    )

# ✅ 항상: 타임아웃 구현
async def external_call():
    """타임아웃과 함께 외부 서비스 호출."""
    async with asyncio.timeout(30):
        return await service.call()

# ✅ 항상: 보안 이벤트 로깅
import logging
security_logger = logging.getLogger("security")

def log_security_event(event: str, details: dict) -> None:
    """보안 관련 이벤트 로깅."""
    security_logger.warning(
        f"보안 이벤트: {event}",
        extra={"details": details, "timestamp": time.time()}
    )
```

---

## 📊 메트릭 & 모니터링

### 필수 메트릭 (항상 추적)

```python
# 진화 메트릭
EVOLUTION_METRICS = {
    "cycles_completed": Counter("evolution_cycles_total"),
    "success_rate": Gauge("evolution_success_rate"),
    "cycle_duration": Histogram("evolution_duration_seconds"),
    "improvements": Counter("improvements_total"),
    "regressions": Counter("regressions_total"),
}

# 품질 메트릭
QUALITY_METRICS = {
    "docstring_coverage": Gauge("docstring_coverage_percent"),
    "test_coverage": Gauge("test_coverage_percent"),
    "complexity": Gauge("code_complexity_score"),
    "security_score": Gauge("security_score"),
    "technical_debt": Gauge("technical_debt_hours"),
}

# 운영 메트릭
OPERATIONAL_METRICS = {
    "agent_failures": Counter("agent_failures_total"),
    "api_latency": Histogram("api_latency_seconds"),
    "error_rate": Gauge("error_rate_percent"),
    "resource_usage": Gauge("resource_usage_percent"),
}
```

### 알림 규칙

```yaml
alerts:
  - name: 진화멈춤
    expr: rate(evolution_cycles_total[1h]) == 0
    for: 2h
    severity: warning

  - name: 품질저하
    expr: delta(docstring_coverage_percent[1h]) < -5
    severity: critical

  - name: 보안위반
    expr: security_score < 80
    severity: critical

  - name: 비용급증
    expr: rate(cost_dollars[1h]) > 50
    severity: warning
```

---

## 🧬 학습 & 패턴 수집

### 패턴 문서화

```python
@dataclass
class Pattern:
    """재사용 가능한 진화 패턴."""

    id: str
    category: str  # improvement, fix, optimization
    context: Dict[str, Any]  # 언제 적용할지
    action: Dict[str, Any]  # 무엇을 할지
    outcome: Dict[str, Any]  # 예상 결과
    success_rate: float  # 과거 성공률
    usage_count: int
    last_used: datetime

    def to_prompt(self) -> str:
        """패턴을 LLM 프롬프트로 변환."""
        return f"""
        패턴: {self.category}
        컨텍스트: {json.dumps(self.context)}
        액션: {json.dumps(self.action)}
        예상 결과: {json.dumps(self.outcome)}
        성공률: {self.success_rate:.1%}
        """

# 패턴 추출
def extract_patterns(evaluation: Result) -> List[Pattern]:
    """성공적인 진화에서 재사용 가능한 패턴 추출."""
    patterns = []

    if evaluation.success and evaluation.data.get("improvement") > 0.1:
        pattern = Pattern(
            id=generate_id(),
            category=classify_improvement(evaluation),
            context=extract_context(evaluation),
            action=extract_action(evaluation),
            outcome=extract_outcome(evaluation),
            success_rate=1.0,
            usage_count=1,
            last_used=datetime.now()
        )
        patterns.append(pattern)

    return patterns
```

---

## 🚨 중요 안전 규칙

### 무한 루프 방지

```python
# 항상 루프 가드 구현
MAX_ITERATIONS = 1000
TIMEOUT_SECONDS = 300

async def safe_loop(condition_func):
    """안전 가드와 함께 루프 실행."""
    iterations = 0
    start_time = time.time()

    while await condition_func():
        iterations += 1

        # 반복 제한
        if iterations > MAX_ITERATIONS:
            raise RuntimeError(f"루프가 {MAX_ITERATIONS} 반복을 초과")

        # 타임아웃 확인
        if time.time() - start_time > TIMEOUT_SECONDS:
            raise TimeoutError(f"루프가 {TIMEOUT_SECONDS}초를 초과")

        # 주기적으로 제어권 양보
        if iterations % 100 == 0:
            await asyncio.sleep(0)

        # 실제 작업
        await do_work()
```

### 리소스 소비 제어

```python
# 항상 리소스 사용량 모니터링
import psutil
import resource

def check_resources():
    """시스템 리소스 확인."""
    # 메모리 확인
    memory = psutil.Process().memory_info()
    if memory.rss > 500 * 1024 * 1024:  # 500MB
        raise MemoryError("메모리 제한 초과")

    # CPU 확인
    cpu_percent = psutil.Process().cpu_percent(interval=0.1)
    if cpu_percent > 80:
        logger.warning(f"높은 CPU 사용량: {cpu_percent}%")

    # 파일 디스크립터 확인
    soft, hard = resource.getrlimit(resource.RLIMIT_NOFILE)
    open_files = len(psutil.Process().open_files())
    if open_files > soft * 0.8:
        logger.warning(f"높은 파일 디스크립터 사용량: {open_files}/{soft}")
```

### 실패 시 롤백

```python
# 항상 롤백 가능해야 함
class Transaction:
    """롤백이 있는 트랜잭션 실행."""

    def __init__(self):
        self.operations = []
        self.rollback_functions = []

    def add_operation(self, operation, rollback):
        """롤백 함수와 함께 작업 추가."""
        self.operations.append(operation)
        self.rollback_functions.append(rollback)

    async def execute(self):
        """실패 시 롤백과 함께 모든 작업 실행."""
        completed = []

        try:
            for i, operation in enumerate(self.operations):
                result = await operation()
                completed.append(i)
        except Exception as e:
            # 역순으로 롤백
            for i in reversed(completed):
                try:
                    await self.rollback_functions[i]()
                except Exception as rollback_error:
                    logger.error(f"롤백 실패: {rollback_error}")
            raise e
```

---

## 📝 문서화 표준

### 코드 문서화

```python
def complex_function(
    param1: str,
    param2: Optional[int] = None,
    **kwargs: Any
) -> Dict[str, Any]:
    """함수가 수행하는 작업의 간단한 설명.

    함수의 목적, 알고리즘 또는 명확히 해야 할 복잡한 동작에 대한
    더 긴 설명.

    인자:
        param1: param1의 목적과 제약 설명
        param2: 선택적 매개변수 설명, 기본 동작
        **kwargs: 추가 키워드 인자:
            - key1: key1 설명
            - key2: key2 설명

    반환:
        다음을 포함하는 딕셔너리:
            - result: 메인 결과
            - metadata: 추가 정보

    발생:
        ValueError: param1이 유효하지 않을 때
        TimeoutError: 작업이 타임아웃을 초과할 때

    예시:
        >>> result = complex_function("test", param2=42)
        >>> assert result["success"] is True

    참고:
        이 함수는 전역 상태에 부작용이 있습니다.
        동시 환경에서 주의해서 사용하세요.

    참조:
        related_function: 대체 접근법
        https://docs.example.com/complex-function
    """
    # 구현
    pass
```

### 아키텍처 결정 기록 (ADR)

```markdown
# ADR-001: 에이전트 통신을 위한 이벤트 주도 아키텍처 사용

## 상태
승인됨

## 컨텍스트
에이전트는 긴밀한 결합 없이 비동기적으로 통신해야 합니다.

## 결정
메시지 큐와 함께 이벤트 주도 아키텍처 사용.

## 결과
- **긍정적**: 느슨한 결합, 확장성, 복원력
- **부정적**: 복잡성 증가, 최종 일관성

## 고려된 대안
1. 직접 API 호출 - 결합 때문에 거부됨
2. 공유 데이터베이스 - 경합 때문에 거부됨
```

---

## 🎯 당신의 체크리스트

### 파일 작업 전 (최우선)

- [ ] Glob으로 유사 파일 검색했는가?
- [ ] Grep으로 동일 기능 검색했는가?
- [ ] LS로 디렉토리 구조 확인했는가?
- [ ] 기존 파일 수정으로 해결 가능한가?
- [ ] 새 파일이 정말 필요한가?

### 코드 작성 전

- [ ] 이것이 자가 진화 능력을 향상시키는가?
- [ ] 기존 패턴을 확인했는가?
- [ ] 더 간단한 해결책이 있는가?
- [ ] 무엇이 잘못될 수 있는가?
- [ ] 어떻게 테스트할 것인가?

### 코드 작성 중

- [ ] TDD를 따르고 있는가?
- [ ] 모든 입력이 검증되는가?
- [ ] 오류가 적절히 처리되는가?
- [ ] 이 코드는 재사용 가능한가?
- [ ] 왜를 문서화하고 있는가?

### 커밋 전

- [ ] 모든 테스트가 통과하는가?
- [ ] 커버리지가 ≥85%인가?
- [ ] 복잡도가 수용 가능한가?
- [ ] 보안 이슈가 없는가?
- [ ] 메트릭이 개선되었는가?

### 병합 후

- [ ] 학습이 수집되었는가?
- [ ] 패턴이 추출되었는가?
- [ ] 문서가 업데이트되었는가?
- [ ] 모니터링이 활성화되었는가?
- [ ] 다음 사이클이 계획되었는가?

---

## 🔄 지속적 개선

이 문서 자체도 진화해야 합니다. 발견할 때:

- **새로운 패턴**: 문서화하세요
- **더 나은 관행**: 이 가이드를 업데이트하세요
- **실패**: 예방 규칙을 추가하세요
- **성공**: 추출하고 공유하세요

기억하세요: **목표는 완전한 자율성입니다. 모든 행동은 인간 개입 없이 스스로를 개선하는 시스템에 더 가까워지게 해야 합니다.**

---

**문서 버전**: 2.0.0
**마지막 업데이트**: T-Developer 시스템에 의해
**다음 검토**: 각 단계 완료 후
**시행**: CI/CD 게이트를 통한 자동화
