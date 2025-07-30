// backend/src/data/access/data-access-factory.ts
import { DynamoDBDocumentClient } from '@aws-sdk/lib-dynamodb';
import { IDataSource } from './data-source.interface';
import { DynamoDBDataSource } from './dynamodb-data-source';
import { DataAccessLayer, DataAccessConfig } from './data-access-layer';
import { UnitOfWork } from './unit-of-work';
import { CacheService } from '../../cache/cache.service';

export interface DataAccessFactoryConfig {
  dataSource: {
    type: 'dynamodb';
    tableName: string;
    client: DynamoDBDocumentClient;
  };
  cache?: CacheService;
  config?: DataAccessConfig;
}

export class DataAccessFactory {
  private static instance: DataAccessFactory;
  private dataSources = new Map<string, IDataSource>();
  private dataAccessLayers = new Map<string, DataAccessLayer>();

  private constructor() {}

  static getInstance(): DataAccessFactory {
    if (!DataAccessFactory.instance) {
      DataAccessFactory.instance = new DataAccessFactory();
    }
    return DataAccessFactory.instance;
  }

  createDataSource(config: DataAccessFactoryConfig): IDataSource {
    const key = `${config.dataSource.type}:${config.dataSource.tableName}`;
    
    if (this.dataSources.has(key)) {
      return this.dataSources.get(key)!;
    }

    let dataSource: IDataSource;

    switch (config.dataSource.type) {
      case 'dynamodb':
        dataSource = new DynamoDBDataSource(
          config.dataSource.client,
          config.dataSource.tableName
        );
        break;
      default:
        throw new Error(`Unsupported data source type: ${config.dataSource.type}`);
    }

    this.dataSources.set(key, dataSource);
    return dataSource;
  }

  createDataAccessLayer(config: DataAccessFactoryConfig): DataAccessLayer {
    const key = `${config.dataSource.type}:${config.dataSource.tableName}`;
    
    if (this.dataAccessLayers.has(key)) {
      return this.dataAccessLayers.get(key)!;
    }

    const dataSource = this.createDataSource(config);
    const dataAccessLayer = new DataAccessLayer(
      dataSource,
      config.cache,
      config.config
    );

    this.dataAccessLayers.set(key, dataAccessLayer);
    return dataAccessLayer;
  }

  createUnitOfWork(config: DataAccessFactoryConfig): UnitOfWork {
    const dataSource = this.createDataSource(config);
    return new UnitOfWork(dataSource);
  }

  // Convenience methods for common configurations
  static createForDynamoDB(
    client: DynamoDBDocumentClient,
    tableName: string,
    cache?: CacheService,
    config?: DataAccessConfig
  ): DataAccessLayer {
    const factory = DataAccessFactory.getInstance();
    return factory.createDataAccessLayer({
      dataSource: { type: 'dynamodb', tableName, client },
      cache,
      config
    });
  }

  static createUnitOfWorkForDynamoDB(
    client: DynamoDBDocumentClient,
    tableName: string
  ): UnitOfWork {
    const factory = DataAccessFactory.getInstance();
    return factory.createUnitOfWork({
      dataSource: { type: 'dynamodb', tableName, client }
    });
  }
}