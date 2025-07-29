import { dynamoDBMock } from './test-utils';
import { PutCommand, GetCommand, QueryCommand } from '@aws-sdk/lib-dynamodb';

export class DatabaseTestHelpers {
  static setupMocks() {
    // Reset all mocks
    dynamoDBMock.reset();
    
    // Default successful responses
    dynamoDBMock.on(PutCommand).resolves({});
    dynamoDBMock.on(GetCommand).resolves({ Item: undefined });
    dynamoDBMock.on(QueryCommand).resolves({ Items: [], Count: 0 });
  }

  static mockPutItem(response?: any) {
    dynamoDBMock.on(PutCommand).resolves(response || {});
  }

  static mockGetItem(item: any) {
    dynamoDBMock.on(GetCommand).resolves({ Item: item });
  }

  static mockQueryItems(items: any[]) {
    dynamoDBMock.on(QueryCommand).resolves({
      Items: items,
      Count: items.length
    });
  }

  static mockDynamoError(errorCode: string, message: string) {
    const error = new Error(message);
    error.name = errorCode;
    dynamoDBMock.on(PutCommand).rejects(error);
    dynamoDBMock.on(GetCommand).rejects(error);
    dynamoDBMock.on(QueryCommand).rejects(error);
  }

  static verifyPutCalled(tableName: string, item: any) {
    const putCalls = dynamoDBMock.commandCalls(PutCommand);
    const matchingCall = putCalls.find(call => 
      call.args[0].input.TableName === tableName &&
      JSON.stringify(call.args[0].input.Item) === JSON.stringify(item)
    );
    return !!matchingCall;
  }

  static verifyGetCalled(tableName: string, key: any) {
    const getCalls = dynamoDBMock.commandCalls(GetCommand);
    const matchingCall = getCalls.find(call =>
      call.args[0].input.TableName === tableName &&
      JSON.stringify(call.args[0].input.Key) === JSON.stringify(key)
    );
    return !!matchingCall;
  }
}