import { DevelopmentDataGenerator } from '../../src/utils/data-generator';
import { DynamoDBDocumentClient } from '@aws-sdk/lib-dynamodb';

// Mock DynamoDB client
const mockDocClient = {
  send: jest.fn()
} as unknown as DynamoDBDocumentClient;

describe('DevelopmentDataGenerator', () => {
  let generator: DevelopmentDataGenerator;

  beforeEach(() => {
    generator = new DevelopmentDataGenerator(mockDocClient);
    jest.clearAllMocks();
  });

  describe('generateProjects', () => {
    it('should generate specified number of projects', async () => {
      const count = 5;
      await generator.generateProjects(count);
      
      expect(mockDocClient.send).toHaveBeenCalledTimes(count);
    });

    it('should generate projects with required fields', async () => {
      await generator.generateProjects(1);
      
      const call = (mockDocClient.send as jest.Mock).mock.calls[0][0];
      const project = call.input.Item;
      
      expect(project).toHaveProperty('id');
      expect(project).toHaveProperty('name');
      expect(project).toHaveProperty('description');
      expect(project).toHaveProperty('projectType');
      expect(project).toHaveProperty('status');
      expect(project).toHaveProperty('techStack');
    });
  });

  describe('generateComponents', () => {
    it('should generate specified number of components', async () => {
      const count = 3;
      await generator.generateComponents(count);
      
      expect(mockDocClient.send).toHaveBeenCalledTimes(count);
    });
  });
});