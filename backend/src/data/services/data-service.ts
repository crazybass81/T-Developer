import { DynamoDBClient } from '@aws-sdk/client-dynamodb';
import { DynamoDBDocumentClient } from '@aws-sdk/lib-dynamodb';
import { Repository } from '../repositories/repository';
import { UserEntity, ProjectEntity, AgentEntity } from '../entities/entities';

export class DataService {
  private repository: Repository;
  
  constructor() {
    const client = new DynamoDBClient({ region: process.env.AWS_REGION || 'us-east-1' });
    const docClient = DynamoDBDocumentClient.from(client);
    this.repository = new Repository(docClient);
  }
  
  // User operations
  async createUser(userId: string, email: string, username: string): Promise<void> {
    const user = new UserEntity(userId);
    user.Email = email;
    user.Username = username;
    user.GSI1PK = `EMAIL#${email}`;
    user.GSI1SK = userId;
    await this.repository.put(user);
  }
  
  async getUser(userId: string): Promise<UserEntity | null> {
    return await this.repository.get(`USER#${userId}`, 'METADATA');
  }
  
  // Project operations
  async createProject(projectId: string, ownerId: string, name: string): Promise<void> {
    const project = new ProjectEntity(projectId, ownerId);
    project.ProjectName = name;
    project.GSI1PK = `USER#${ownerId}`;
    project.GSI1SK = `PROJECT#${project.CreatedAt}#${projectId}`;
    await this.repository.put(project);
  }
  
  async getProject(projectId: string): Promise<ProjectEntity | null> {
    return await this.repository.get(`PROJECT#${projectId}`, 'METADATA');
  }
  
  async getUserProjects(userId: string): Promise<ProjectEntity[]> {
    return await this.repository.queryGSI('GSI1', `USER#${userId}`, 'PROJECT#');
  }
  
  // Agent operations
  async createAgent(agentId: string, projectId: string, agentType: string): Promise<void> {
    const agent = new AgentEntity(agentId, projectId, agentType);
    agent.GSI2PK = `AGENT#${agentId}`;
    agent.GSI2SK = `STATUS#${agent.Status}`;
    await this.repository.put(agent);
  }
  
  async getProjectAgents(projectId: string): Promise<AgentEntity[]> {
    return await this.repository.query(`PROJECT#${projectId}`, 'AGENT#');
  }
}