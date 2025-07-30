// Queue configuration for AWS SQS setup
export const queueConfigurations = {
  'agent-tasks': {
    QueueName: 'T-Developer-AgentTasks',
    Attributes: {
      VisibilityTimeoutSeconds: '300',
      MessageRetentionPeriod: '1209600', // 14 days
      ReceiveMessageWaitTimeSeconds: '20'
    }
  },
  'notifications': {
    QueueName: 'T-Developer-Notifications',
    Attributes: {
      VisibilityTimeoutSeconds: '60',
      MessageRetentionPeriod: '345600' // 4 days
    }
  },
  'dead-letter': {
    QueueName: 'T-Developer-DeadLetter',
    Attributes: {
      MessageRetentionPeriod: '1209600'
    }
  }
};

export const eventBridgeRules = [
  {
    Name: 'AgentStartedRule',
    EventPattern: JSON.stringify({
      source: ['t-developer.agents'],
      'detail-type': ['AgentStarted']
    }),
    Targets: [
      {
        Id: '1',
        Arn: process.env.AGENT_TASKS_QUEUE_ARN
      }
    ]
  }
];