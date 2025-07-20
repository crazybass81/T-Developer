# T-Developer v1.0 Testing Checklist

Use this checklist to verify that all features of T-Developer v1.0 are working correctly after deployment.

## Backend Verification

- [ ] **Backend Service Running**
  - [ ] Systemd service is active (`systemctl status tdeveloper`)
  - [ ] Health endpoint returns 200 (`curl http://localhost:8000/health`)
  - [ ] Detailed health endpoint shows correct information

- [ ] **AWS Resources**
  - [ ] DynamoDB tables exist with correct prefix
  - [ ] S3 bucket exists and is accessible
  - [ ] AWS credentials have proper permissions

- [ ] **Lambda Features Disabled**
  - [ ] `USE_LAMBDA_NOTIFIER=false` in .env
  - [ ] `USE_LAMBDA_TEST_EXECUTOR=false` in .env
  - [ ] `USE_LAMBDA_CODE_GENERATOR=false` in .env

## Frontend Verification

- [ ] **S3 Hosting**
  - [ ] Frontend bucket exists
  - [ ] Static website hosting is enabled
  - [ ] index.html exists in the bucket
  - [ ] Website is accessible via S3 website URL

- [ ] **Frontend Functionality**
  - [ ] App loads without JavaScript errors (check browser console)
  - [ ] All static assets load correctly (CSS, images)
  - [ ] API calls to backend succeed (check Network tab)
  - [ ] Responsive design works on different screen sizes

## Feature Testing

### Project Management

- [ ] **Project Creation**
  - [ ] Create a new project with name and description
  - [ ] Add GitHub repository information
  - [ ] Add Slack channel information
  - [ ] Project appears in project list after creation
  - [ ] Project details can be viewed

### Task Management

- [ ] **Task Creation**
  - [ ] Create a new task with a natural language request
  - [ ] Select a project for the task
  - [ ] Task is submitted successfully
  - [ ] Redirects to task monitoring page

- [ ] **Task Monitoring**
  - [ ] Task status updates in real-time
  - [ ] Timeline shows progression through stages
  - [ ] Status changes from "received" to "planning"
  - [ ] Status changes from "planning" to "coding"
  - [ ] Status changes from "coding" to "testing"
  - [ ] Status changes from "testing" to "deploying"
  - [ ] Status changes to "completed" or "deployed"

- [ ] **Task Review**
  - [ ] Plan details can be viewed
  - [ ] Modified files list is displayed
  - [ ] Created files list is displayed
  - [ ] Diff for each file can be viewed
  - [ ] Test results are displayed
  - [ ] Test log can be viewed
  - [ ] PR URL is displayed and works

### Integrations

- [ ] **Slack Integration**
  - [ ] Task acknowledgment message sent to Slack
  - [ ] Planning started notification sent
  - [ ] Plan created notification sent
  - [ ] Coding started notification sent
  - [ ] Coding completed notification sent
  - [ ] Testing started notification sent
  - [ ] Tests passed notification sent
  - [ ] Deployment notification sent
  - [ ] Completion notification sent
  - [ ] Messages appear in the correct channel
  - [ ] Task can be created via Slack mention

- [ ] **GitHub Integration**
  - [ ] Branch is created for the task
  - [ ] Code changes are committed
  - [ ] Pull request is created
  - [ ] PR has correct title and description
  - [ ] PR is merged automatically (if AUTO_MERGE=true)
  - [ ] PR remains open for review (if AUTO_MERGE=false)

## Error Handling

- [ ] **Graceful Error Handling**
  - [ ] Invalid task requests show appropriate error
  - [ ] Network errors are handled gracefully
  - [ ] Missing credentials show helpful messages
  - [ ] Error states in task timeline are displayed correctly

## Performance

- [ ] **Response Times**
  - [ ] API endpoints respond within acceptable time
  - [ ] Frontend loads quickly
  - [ ] Task polling doesn't cause performance issues

- [ ] **Resource Usage**
  - [ ] Backend CPU usage remains reasonable during tasks
  - [ ] Backend memory usage remains stable
  - [ ] No memory leaks during extended operation

## Notes

- Record any issues or observations here
- Document workarounds for any known issues
- Note any features that need improvement in future versions