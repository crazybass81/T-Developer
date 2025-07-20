# T-Developer Architecture

## Overview

T-Developer is designed with a modular architecture that allows it to run the core FastAPI backend continuously on EC2 while offloading specific functions to AWS Lambda for better scalability and resource utilization.

## Components

### Core Backend (EC2)

The main FastAPI application runs continuously on EC2 as a systemd service. This ensures:
- Consistent availability of the API endpoints
- Reliable processing of incoming requests
- Central orchestration of the development workflow

### Modular Lambda Functions

Specific resource-intensive or asynchronous tasks are offloaded to AWS Lambda:

1. **Slack Notifications (t-developer-slack-notifier)**
   - Handles all Slack messaging
   - Reduces API latency by processing notifications asynchronously
   - Scales independently based on notification volume

2. **Test Execution (t-developer-test-executor)**
   - Runs tests in an isolated environment
   - Provides consistent test results regardless of EC2 load
   - Can handle multiple test runs in parallel

## Architecture Diagram

```
┌─────────────────────────────────────┐
│                                     │
│  T-Developer Backend (EC2)          │
│  ┌─────────────────────────────┐    │
│  │                             │    │
│  │  FastAPI Application        │    │
│  │  ┌─────────────────────┐    │    │
│  │  │                     │    │    │
│  │  │  MAO Orchestrator   │    │    │
│  │  │                     │    │    │
│  │  └─────────────────────┘    │    │
│  │                             │    │
│  └─────────────────────────────┘    │
│                                     │
└───────────────┬─────────────────────┘
                │
                ▼
┌───────────────┴─────────────────────┐
│                                     │
│  AWS Lambda Functions               │
│  ┌─────────────────────────────┐    │
│  │                             │    │
│  │  Slack Notifier             │    │
│  │                             │    │
│  └─────────────────────────────┘    │
│                                     │
│  ┌─────────────────────────────┐    │
│  │                             │    │
│  │  Test Executor              │    │
│  │                             │    │
│  └─────────────────────────────┘    │
│                                     │
└─────────────────────────────────────┘
```

## Factory Pattern

The system uses a factory pattern to switch between local and Lambda implementations:

- `SlackNotifierFactory` - Creates either a local `SlackNotifier` or a Lambda-based `LambdaSlackNotifier`
- `TestExecutorFactory` - Creates either a local test executor or a Lambda-based `LambdaTestExecutor`

This allows for easy switching between local and Lambda execution based on configuration.

## Configuration

The system can be configured to use either local or Lambda implementations via environment variables:

```
USE_LAMBDA_NOTIFIER=true
USE_LAMBDA_TEST_EXECUTOR=true
```

## Deployment

### EC2 Backend

The FastAPI backend is deployed as a systemd service:

```bash
sudo /home/ec2-user/T-Developer/scripts/install_service.sh
```

### Lambda Functions

Lambda functions are deployed using the deployment script:

```bash
/home/ec2-user/T-Developer/lambda/deploy_lambdas.sh
```

To enable Lambda functions:

```bash
/home/ec2-user/T-Developer/scripts/enable_lambda_functions.sh
```