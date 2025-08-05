# Quick Start Guide

## Prerequisites
- Node.js 18+
- Python 3.9+
- AWS Account
- Docker

## Installation

### 1. Clone Repository
```bash
git clone https://github.com/your-org/t-developer.git
cd t-developer
```

### 2. Install Dependencies
```bash
# Backend (Python with uv)
curl -LsSf https://astral.sh/uv/install.sh | sh
uv venv
source .venv/bin/activate
uv pip install -r requirements.txt

# Frontend
npm install
```

### 3. Environment Setup
```bash
cp .env.example .env
# Edit .env with your AWS credentials and API keys
```

### 4. Start Development
```bash
# Backend
npm run dev:backend

# Frontend
npm run dev:frontend
```

## First Project
1. Open http://localhost:3000
2. Enter project description
3. Watch agents work
4. Download generated project