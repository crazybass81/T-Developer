# T-Developer API Documentation

## Base URL
- Development: `http://localhost:8000`
- Production: `https://api.t-developer.com` (TBD)

## Authentication
현재 개발 단계에서는 인증이 비활성화되어 있습니다.

## Endpoints

### 1. Health Check
```
GET /health
```
**Response:**
```json
{
    "status": "healthy",
    "timestamp": "2025-08-09T12:00:00.000000",
    "service": "t-developer-api"
}
```

### 2. Projects Management

#### Get All Projects
```
GET /api/v1/projects
```
**Response:**
```json
[
    {
        "id": "uuid",
        "name": "프로젝트 이름",
        "description": "프로젝트 설명",
        "framework": "react",
        "template": "blank",
        "status": "draft",
        "userId": "user-1",
        "settings": {
            "theme": "light",
            "language": "typescript",
            "cssFramework": "tailwind",
            "buildTool": "vite",
            "packageManager": "npm",
            "features": ["TypeScript", "Dark Mode"]
        },
        "createdAt": "2025-08-09T12:00:00",
        "updatedAt": "2025-08-09T12:00:00"
    }
]
```

#### Create Project
```
POST /api/v1/projects
```
**Request Body:**
```json
{
    "name": "할일 관리 앱",
    "description": "간단한 할일 관리 애플리케이션",
    "framework": "react",
    "template": "todo",
    "status": "draft",
    "userId": "user-1",
    "settings": {
        "theme": "light",
        "language": "typescript",
        "cssFramework": "tailwind",
        "buildTool": "vite",
        "packageManager": "npm",
        "features": ["TypeScript", "Dark Mode", "Real-time Updates"]
    }
}
```

### 3. Project Generation

#### Generate Project with AI
```
POST /api/v1/generate
```
**Request Body:**
```json
{
    "name": "온라인 쇼핑몰",
    "description": "전자상거래 웹사이트",
    "framework": "nextjs",
    "idea": "사용자가 상품을 검색하고 구매할 수 있는 온라인 쇼핑몰을 만들어주세요. 장바구니, 결제, 주문 추적 기능이 필요합니다.",
    "template": "ecommerce",
    "settings": {
        "theme": "light",
        "language": "typescript",
        "cssFramework": "tailwind",
        "buildTool": "vite",
        "packageManager": "npm",
        "features": [
            "Authentication",
            "Database Integration",
            "Payment Integration",
            "Shopping Cart"
        ]
    }
}
```

**Response:**
```json
{
    "project_id": "project_20250809_120000_abc123",
    "status": "success",
    "message": "프로젝트가 성공적으로 생성되었습니다",
    "download_url": "/api/v1/download/project_20250809_120000_abc123"
}
```

### 4. Download Project

#### Download Generated Project
```
GET /api/v1/download/{project_id}
```
**Response:** ZIP file containing the generated project

### 5. Preview Project

#### Preview Project Structure
```
GET /api/v1/preview/{project_id}
```
**Response:**
```json
{
    "project_id": "project_20250809_120000_abc123",
    "file_structure": [
        {
            "path": "src/App.js",
            "size": 2048,
            "compressed_size": 512
        }
    ],
    "file_contents": {
        "src/App.js": {
            "content": "import React from 'react'...",
            "truncated": false,
            "language": "javascript"
        }
    },
    "stats": {
        "total_files": 25,
        "total_size_bytes": 102400,
        "total_size_mb": 0.1,
        "zip_size_mb": 0.05
    }
}
```

## Framework Support
- **react** - React 18+
- **nextjs** - Next.js 14+
- **vue** - Vue 3+
- **svelte** - SvelteKit

## Template Types
- **blank** - 빈 프로젝트
- **dashboard** - 관리자 대시보드
- **ecommerce** - 전자상거래
- **blog** - 블로그/CMS
- **portfolio** - 포트폴리오
- **todo** - 할일 관리

## Available Features
- TypeScript
- Dark Mode
- Authentication
- Database Integration
- API Integration
- Real-time Updates
- Mobile Responsive
- PWA Support
- Payment Integration
- Shopping Cart
- CMS
- SEO
- Contact Form
- Gallery
- Drag and Drop

## Template Default Features
각 템플릿은 다음과 같은 기본 기능을 포함합니다:

### Dashboard Template
- Authentication
- Database Integration
- API Integration
- Dark Mode

### E-commerce Template
- Authentication
- Database Integration
- Payment Integration
- Shopping Cart

### Blog Template
- Authentication
- Database Integration
- CMS
- SEO

### Portfolio Template
- Dark Mode
- Contact Form
- SEO
- Gallery

### Todo Template
- Database Integration
- Real-time Updates
- Drag and Drop

## Error Responses
모든 에러는 다음 형식으로 반환됩니다:
```json
{
    "success": false,
    "error": "에러 메시지",
    "error_code": "ERROR_CODE",
    "details": {},
    "timestamp": "2025-08-09T12:00:00"
}
```

## Status Codes
- `200` - Success
- `400` - Bad Request (잘못된 입력)
- `404` - Not Found (리소스 없음)
- `422` - Validation Error (유효성 검사 실패)
- `500` - Internal Server Error (서버 오류)

## Rate Limiting
현재 개발 단계에서는 rate limiting이 적용되지 않습니다.

## WebSocket Support (Coming Soon)
실시간 프로젝트 생성 진행 상황 추적을 위한 WebSocket 연결이 계획되어 있습니다.
- Endpoint: `ws://localhost:8000/ws`
- Events: `progress`, `complete`, `error`

## Notes
- 모든 날짜/시간은 ISO 8601 형식입니다
- 프로젝트 생성은 최대 60초가 소요될 수 있습니다
- 생성된 프로젝트는 24시간 후 자동 삭제됩니다