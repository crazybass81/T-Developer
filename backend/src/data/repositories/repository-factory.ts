import { DynamoDBDocumentClient } from '@aws-sdk/lib-dynamodb';
import { UserRepository } from './user.repository';
import { ProjectRepository } from './project.repository';
import { AgentRepository } from './agent.repository';
import { ComponentRepository } from './component.repository';
import { SessionRepository } from './session.repository';

export class RepositoryFactory {
  private static instance: RepositoryFactory;
  private userRepository?: UserRepository;
  private projectRepository?: ProjectRepository;
  private agentRepository?: AgentRepository;
  private componentRepository?: ComponentRepository;
  private sessionRepository?: SessionRepository;

  constructor(private docClient: DynamoDBDocumentClient) {}

  static getInstance(docClient: DynamoDBDocumentClient): RepositoryFactory {
    if (!RepositoryFactory.instance) {
      RepositoryFactory.instance = new RepositoryFactory(docClient);
    }
    return RepositoryFactory.instance;
  }

  getUserRepository(): UserRepository {
    if (!this.userRepository) {
      this.userRepository = new UserRepository(this.docClient);
    }
    return this.userRepository;
  }

  getProjectRepository(): ProjectRepository {
    if (!this.projectRepository) {
      this.projectRepository = new ProjectRepository(this.docClient);
    }
    return this.projectRepository;
  }

  getAgentRepository(): AgentRepository {
    if (!this.agentRepository) {
      this.agentRepository = new AgentRepository(this.docClient);
    }
    return this.agentRepository;
  }

  getComponentRepository(): ComponentRepository {
    if (!this.componentRepository) {
      this.componentRepository = new ComponentRepository(this.docClient);
    }
    return this.componentRepository;
  }

  getSessionRepository(): SessionRepository {
    if (!this.sessionRepository) {
      this.sessionRepository = new SessionRepository(this.docClient);
    }
    return this.sessionRepository;
  }

  // Convenience method to get all repositories
  getAllRepositories() {
    return {
      users: this.getUserRepository(),
      projects: this.getProjectRepository(),
      agents: this.getAgentRepository(),
      components: this.getComponentRepository(),
      sessions: this.getSessionRepository()
    };
  }
}