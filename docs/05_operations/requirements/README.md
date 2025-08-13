# 📦 Requirements Documentation

## Python Dependencies

This directory contains documentation about the Python dependencies used in the T-Developer project.

### Main Requirements Files

1. **requirements.txt** - Core production dependencies
2. **requirements-dev.txt** - Development and testing dependencies
3. **requirements-enterprise.txt** - Enterprise features dependencies
4. **requirements-compatible.txt** - Compatible versions for specific environments

### Dependency Categories

#### Core Dependencies
- FastAPI - Web framework
- Boto3 - AWS SDK
- Redis - Caching and message queue
- Pydantic - Data validation
- Cryptography - Security features

#### AI/ML Dependencies
- OpenAI - GPT integration
- Anthropic - Claude integration
- LangChain - AI orchestration
- Transformers - NLP models

#### Database Dependencies
- Motor - Async MongoDB driver
- AsyncPG - PostgreSQL async driver
- SQLAlchemy - ORM

#### Testing Dependencies
- Pytest - Testing framework
- Coverage - Code coverage
- Black - Code formatting
- Flake8 - Linting
- Mypy - Type checking

### Version Management

All dependencies are pinned to specific versions to ensure reproducibility:
- Production dependencies use exact versions
- Development dependencies use compatible version ranges
- Security updates are applied monthly

### Installation

```bash
# Production
pip install -r requirements.txt

# Development
pip install -r requirements-dev.txt

# Using UV (recommended)
uv pip install -r requirements.txt
```

### Security

Dependencies are regularly scanned for vulnerabilities using:
- Safety
- Bandit
- Trivy
- GitHub Dependabot

---

*Last Updated: 2025-08-13*