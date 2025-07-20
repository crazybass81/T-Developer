# T-Developer v1.0

This is the v1.0 release of T-Developer, a system that automates software development tasks using AI. This version runs entirely on EC2 without AWS Lambda dependencies.

## Architecture

T-Developer v1.0 uses a simple architecture:

- **Backend**: FastAPI application running on EC2 as a systemd service
- **Frontend**: React SPA hosted on Amazon S3 as a static website
- **Storage**: DynamoDB for task/project data, S3 for artifacts
- **Integrations**: GitHub for code repositories, Slack for notifications

## Deployment Instructions

### Backend Deployment

1. **Install Dependencies**:
   ```bash
   cd T-Developer
   python3 -m venv venv
   source venv/bin/activate
   pip install -r requirements.txt
   ```

2. **Configure Environment**:
   ```bash
   cp .env.example .env
   # Edit .env with your settings
   ```

3. **Install as Service**:
   ```bash
   sudo ./scripts/install_service.sh
   ```

4. **Verify Backend**:
   ```bash
   curl http://localhost:8000/health
   ```

### Frontend Deployment

1. **Build and Deploy**:
   ```bash
   ./deploy_frontend.sh
   ```
   
   You can specify a custom backend URL:
   ```bash
   ./deploy_frontend.sh https://your-api-domain.com
   ```

2. **Access the Frontend**:
   Open the S3 website URL in your browser:
   ```
   http://tdeveloper-frontend.s3-website-<region>.amazonaws.com
   ```

## Configuration

Key configuration options in `.env`:

- **AWS Settings**: `AWS_REGION`, `DYNAMODB_TABLE_PREFIX`, `S3_BUCKET_NAME`
- **GitHub Integration**: `GITHUB_TOKEN`, `GITHUB_OWNER`, `GITHUB_REPO`, `AUTO_MERGE`
- **Slack Integration**: `SLACK_BOT_TOKEN`, `SLACK_CHANNEL`, `SLACK_SIGNING_SECRET`
- **Lambda Features**: All set to `false` in v1.0 (`USE_LAMBDA_NOTIFIER`, `USE_LAMBDA_TEST_EXECUTOR`)

## Verification

Run the verification script to check your deployment:

```bash
./scripts/verify_deployment.sh
```

Use the testing checklist to verify all features:

```bash
cat TESTING_CHECKLIST.md
```

## Troubleshooting

- **Backend Issues**: Check logs with `sudo journalctl -u tdeveloper -f`
- **Frontend Issues**: Check browser console and network requests
- **Integration Issues**: Verify credentials in `.env` file

## Future Development

This v1.0 release is designed to run entirely on EC2. Future v1.1+ releases will introduce AWS Lambda support for better scalability.

To upgrade to Lambda-based features in the future:
1. Set `USE_LAMBDA_*` environment variables to `true`
2. Deploy the Lambda functions
3. Restart the service