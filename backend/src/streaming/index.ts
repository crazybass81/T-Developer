export { 
  EventStream, 
  DynamoDBStreamProcessor, 
  EventStreamManager,
  type StreamEvent,
  type StreamConfig 
} from './event-stream';

export { 
  EventProcessor, 
  ProjectEventProcessor, 
  AgentEventProcessor,
  EventProcessorManager,
  type ProcessorConfig 
} from './event-processor';

export { 
  RealtimeUpdateService, 
  StreamToRealtimeAdapter,
  RealtimeMetrics,
  type RealtimeConfig 
} from './real-time-updates';

export { 
  StreamAnalytics, 
  StreamHealthMonitor,
  type AnalyticsConfig,
  type StreamMetrics 
} from './stream-analytics';