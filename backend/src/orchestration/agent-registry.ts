import { DynamoDBClient, PutItemCommand, GetItemCommand, ScanCommand } from '@aws-sdk/client-dynamodb';
import { marshall, unmarshall } from '@aws-sdk/util-dynamodb';

interface AgentMetadata {
  name: string;
  version: string;
  capabilities: string[];
  maxConcurrent: number;
  timeout: number;
  status?: 'active' | 'inactive' | 'error';
  lastHealthCheck?: Date;
}

interface AgentInstance {
  metadata: AgentMetadata;
  instance: any;
  activeConnections: number;
}

export class AgentRegistry {
  private agents: Map<string, AgentMetadata> = new Map();
  private instances: Map<string, AgentInstance> = new Map();
  private dynamodb: DynamoDBClient;
  private tableName: string;

  constructor(tableName: string = 't-developer-agents') {
    this.dynamodb = new DynamoDBClient({ region: process.env.AWS_REGION });
    this.tableName = tableName;
  }

  async register(metadata: AgentMetadata): Promise<void> {
    // Store in memory
    this.agents.set(metadata.name, metadata);
    
    // Persist to DynamoDB
    await this.persistToDatabase(metadata);
  }

  async getAgent(name: string): Promise<any> {
    if (!this.instances.has(name)) {
      await this.instantiateAgent(name);
    }
    
    const instance = this.instances.get(name);
    if (!instance) throw new Error(`Agent ${name} not available`);
    
    return instance.instance;
  }

  async listAgents(): Promise<AgentMetadata[]> {
    return Array.from(this.agents.values());
  }

  async unregister(name: string): Promise<void> {
    this.agents.delete(name);
    this.instances.delete(name);
    
    // Remove from DynamoDB
    await this.dynamodb.send(new PutItemCommand({
      TableName: this.tableName,
      Item: marshall({ name, status: 'inactive' })
    }));
  }

  private async instantiateAgent(name: string): Promise<void> {
    const metadata = this.agents.get(name);
    if (!metadata) throw new Error(`Agent ${name} not found`);

    try {
      // Dynamic import based on agent name
      const AgentClass = await import(`../agents/implementations/${name}`);
      const instance = new AgentClass.default(metadata);
      
      this.instances.set(name, {
        metadata,
        instance,
        activeConnections: 0
      });
    } catch (error) {
      throw new Error(`Failed to instantiate agent ${name}: ${error.message}`);
    }
  }

  private async persistToDatabase(metadata: AgentMetadata): Promise<void> {
    const item = {
      ...metadata,
      registeredAt: new Date().toISOString(),
      status: 'active'
    };

    await this.dynamodb.send(new PutItemCommand({
      TableName: this.tableName,
      Item: marshall(item)
    }));
  }

  async loadFromDatabase(): Promise<void> {
    const result = await this.dynamodb.send(new ScanCommand({
      TableName: this.tableName,
      FilterExpression: '#status = :status',
      ExpressionAttributeNames: { '#status': 'status' },
      ExpressionAttributeValues: marshall({ ':status': 'active' })
    }));

    if (result.Items) {
      for (const item of result.Items) {
        const metadata = unmarshall(item) as AgentMetadata;
        this.agents.set(metadata.name, metadata);
      }
    }
  }

  getAgentStatus(name: string): AgentMetadata | null {
    return this.agents.get(name) || null;
  }

  async updateAgentStatus(name: string, status: 'active' | 'inactive' | 'error'): Promise<void> {
    const metadata = this.agents.get(name);
    if (metadata) {
      metadata.status = status;
      metadata.lastHealthCheck = new Date();
      await this.persistToDatabase(metadata);
    }
  }
}