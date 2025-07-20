# T-Developer v1.0

T-Developer is an AI-powered development assistant that automates software development tasks using natural language requests.

## Architecture

T-Developer v1.0 uses a simple architecture:

- **Backend**: FastAPI application running on EC2 as a systemd service
- **Frontend**: React SPA hosted on Amazon S3 as a static website
- **Storage**: DynamoDB for task/project data, S3 for artifacts
- **Integrations**: GitHub for code repositories, Slack for notifications

## Features

- **Natural Language Task Processing**: Submit development tasks in plain English
- **AI-Powered Development**: Automated planning, coding, and testing
- **GitHub Integration**: Automatic branch creation, code commits, and PR creation
- **Slack Integration**: Real-time notifications about task progress
- **Project Management**: Organize tasks by project with specific GitHub repos and Slack channels
- **Test Execution**: Automatic test running and reporting
- **Code Review**: View diffs and test results for completed tasks

## Deployment

See the [Deployment Guide](DEPLOYMENT_GUIDE.md) for detailed instructions on deploying T-Developer v1.0.

### Quick Start

1. **Backend Setup**:
   ```bash
   # Clone the repository
   git clone https://github.com/your-username/T-Developer.git
   cd T-Developer
   
   # Install dependencies
   python3 -m venv venv
   source venv/bin/activate
   pip install -r requirements.txt
   
   # Configure environment
   cp .env.example .env
   # Edit .env with your settings
   
   # Set up infrastructure
   python3 scripts/setup_infrastructure.py
   
   # Install as a service
   sudo ./scripts/install_service.sh
   ```

2. **Frontend Setup**:
   ```bash
   # Build the frontend
   cd frontend
   npm install
   echo "REACT_APP_API_URL=http://<EC2-PUBLIC-IP>:8000" > .env.production
   npm run build
   
   # Deploy to S3
   aws s3 sync build/ s3://tdeveloper-frontend/ --delete
   ```

## Configuration

Key configuration options in `.env`:

- **AWS Settings**: `AWS_REGION`, `DYNAMODB_TABLE_PREFIX`, `S3_BUCKET_NAME`
- **GitHub Integration**: `GITHUB_TOKEN`, `GITHUB_OWNER`, `GITHUB_REPO`, `AUTO_MERGE`
- **Slack Integration**: `SLACK_BOT_TOKEN`, `SLACK_CHANNEL`, `SLACK_SIGNING_SECRET`
- **Lambda Features**: All set to `false` in v1.0 (`USE_LAMBDA_NOTIFIER`, `USE_LAMBDA_TEST_EXECUTOR`)

## Usage

1. **Create a Project**:
   - Open the frontend in a web browser
   - Fill in project details (name, description, GitHub repo, Slack channel)
   - Click "Create Project"

2. **Submit a Task**:
   - Navigate to the "New Task" page
   - Select a project
   - Enter a natural language request (e.g., "Add a login page")
   - Click "Submit"

3. **Monitor Progress**:
   - Watch the task timeline update in real-time
   - Receive notifications in Slack
   - Review the completed task (plan, code changes, test results)
   - Merge the Pull Request on GitHub

## Monitoring and Maintenance

- **Monitor Deployment**: Run `./scripts/monitor_deployment.sh`
- **View Logs**: Check `logs/tdeveloper.out.log`, `logs/tdeveloper.err.log`, and `t-developer.log`
- **Restart Service**: Run `sudo systemctl restart tdeveloper`

## Testing

See the [Testing Checklist](TESTING_CHECKLIST.md) for a comprehensive list of features to test after deployment.

## Future Development

This v1.0 release is designed to run entirely on EC2. Future v1.1+ releases will introduce AWS Lambda support for better scalability.

To upgrade to Lambda-based features in the future:
1. Set `USE_LAMBDA_*` environment variables to `true`
2. Deploy the Lambda functions
3. Restart the service