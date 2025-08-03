# T-Developer Documentation

## 📚 Core Documentation

### Architecture
- [System Architecture](./architecture.md) - Overall system design and components
- [AWS Configuration](./aws-config-setup.md) - AWS services setup guide

### Development
- [Migration Guide](./migration-guide.md) - pip to uv migration instructions
- [Testing Guide](./testing-guide.md) - Testing strategies and best practices
- [UV Developer Guide](./uv-developer-guide.md) - Using UV package manager

### Implementation Status
- [Implementation Status](./implementation-status.md) - Current progress of 9 core agents

## 🤖 Agent Documentation

### Core Agents
- [Component Decision Agent](./agents/component-decision-agent.md)
- [Match Rate Agent](./agents/matching_rate_agent.md)
- [Search Agent](./agents/search_agent.md)

## 🚀 Quick Start

1. **Setup Environment**
   ```bash
   # Install UV package manager
   curl -LsSf https://astral.sh/uv/install.sh | sh
   
   # Install dependencies
   uv pip install -r requirements.txt
   ```

2. **Configure AWS**
   - Follow [AWS Configuration Guide](./aws-config-setup.md)
   - Set up Bedrock model access
   - Configure Secrets Manager

3. **Run Development Server**
   ```bash
   npm run dev
   ```

## 📋 Project Status

- **Phase 0**: Environment Setup ✅ Complete
- **Phase 1**: Core Infrastructure ✅ Complete  
- **Phase 2**: Data Layer ✅ Complete
- **Phase 3**: Agent Framework ✅ Complete
- **Phase 4**: 9 Core Agents 🔄 53.5% Complete

See [Implementation Status](./implementation-status.md) for detailed progress.

## 🔧 Development Guidelines

- Use UV instead of pip for package management
- Follow the agent framework patterns established in Phase 3
- Implement comprehensive error handling
- Add unit tests for all new components
- Use type hints and dataclasses consistently

## 📞 Support

For questions or issues:
1. Check existing documentation
2. Review implementation status
3. Consult the testing guide for debugging