// Task 1.14.1: SQS 큐 설정 및 관리
import { SQSClient, SendMessageCommand, ReceiveMessageCommand, DeleteMessageCommand } from '@aws-sdk/client-sqs';

export class QueueManager {
  private sqsClient: SQSClient;
  private queues: Map<string, string> = new Map();

  constructor(region: string = 'us-east-1') {
    this.sqsClient = new SQSClient({ region });
    this.initializeQueues();
  }

  private initializeQueues(): void {
    this.queues.set('agent-tasks', process.env.AGENT_TASKS_QUEUE_URL!);
    this.queues.set('notifications', process.env.NOTIFICATIONS_QUEUE_URL!);
    this.queues.set('dead-letter', process.env.DLQ_URL!);
  }

  async sendMessage(queueName: string, message: any): Promise<void> {
    const queueUrl = this.queues.get(queueName);
    if (!queueUrl) throw new Error(`Queue not found: ${queueName}`);

    await this.sqsClient.send(new SendMessageCommand({
      QueueUrl: queueUrl,
      MessageBody: JSON.stringify(message),
      MessageAttributes: {
        timestamp: { StringValue: new Date().toISOString(), DataType: 'String' }
      }
    }));
  }

  async receiveMessages(queueName: string, maxMessages: number = 10): Promise<any[]> {
    const queueUrl = this.queues.get(queueName);
    if (!queueUrl) throw new Error(`Queue not found: ${queueName}`);

    const response = await this.sqsClient.send(new ReceiveMessageCommand({
      QueueUrl: queueUrl,
      MaxNumberOfMessages: maxMessages,
      WaitTimeSeconds: 20
    }));

    return response.Messages?.map(msg => ({
      id: msg.MessageId,
      body: JSON.parse(msg.Body!),
      receiptHandle: msg.ReceiptHandle
    })) || [];
  }

  async deleteMessage(queueName: string, receiptHandle: string): Promise<void> {
    const queueUrl = this.queues.get(queueName);
    if (!queueUrl) throw new Error(`Queue not found: ${queueName}`);

    await this.sqsClient.send(new DeleteMessageCommand({
      QueueUrl: queueUrl,
      ReceiptHandle: receiptHandle
    }));
  }
}