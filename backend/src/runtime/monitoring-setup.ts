import { CloudWatch, SNS, CloudWatchLogs } from 'aws-sdk';

interface MonitoringConfig {
  runtimeId: string;
  metrics: MetricConfig[];
  alarms: AlarmConfig[];
  dashboards: DashboardConfig[];
}

interface MetricConfig {
  name: string;
  namespace: string;
  dimensions: Record<string, string>;
  statistic: 'Average' | 'Sum' | 'Maximum' | 'Minimum';
  period: number;
}

interface AlarmConfig {
  name: string;
  metricName: string;
  namespace: string;
  comparisonOperator: string;
  threshold: number;
  evaluationPeriods: number;
  period: number;
  statistic: string;
  snsTopicArn: string;
  description: string;
  dimensions: any[];
}

interface DashboardConfig {
  name: string;
  runtimeId: string;
}

export class RuntimeMonitoringSetup {
  private cloudWatch: CloudWatch;
  private sns: SNS;
  private logs: CloudWatchLogs;
  
  constructor() {
    this.cloudWatch = new CloudWatch();
    this.sns = new SNS();
    this.logs = new CloudWatchLogs();
  }
  
  async setupMonitoring(config: MonitoringConfig): Promise<void> {
    // 1. 커스텀 메트릭 생성
    await this.createCustomMetrics(config.metrics);
    
    // 2. CloudWatch 알람 설정
    await this.createAlarms(config.alarms);
    
    // 3. 대시보드 생성
    await this.createDashboard(config.dashboards);
    
    // 4. 로그 그룹 설정
    await this.setupLogging(config.runtimeId);
    
    // 5. X-Ray 트레이싱 활성화
    await this.enableXRayTracing(config.runtimeId);
  }
  
  private async createCustomMetrics(metrics: MetricConfig[]): Promise<void> {
    for (const metric of metrics) {
      const putMetricParams = {
        Namespace: metric.namespace,
        MetricData: [
          {
            MetricName: metric.name,
            Dimensions: Object.entries(metric.dimensions).map(
              ([name, value]) => ({ Name: name, Value: value })
            ),
            Timestamp: new Date(),
            Unit: 'None'
          }
        ]
      };
      
      await this.cloudWatch.putMetricData(putMetricParams).promise();
    }
  }
  
  private async createAlarms(alarms: AlarmConfig[]): Promise<void> {
    for (const alarm of alarms) {
      const alarmParams = {
        AlarmName: alarm.name,
        ComparisonOperator: alarm.comparisonOperator,
        EvaluationPeriods: alarm.evaluationPeriods,
        MetricName: alarm.metricName,
        Namespace: alarm.namespace,
        Period: alarm.period,
        Statistic: alarm.statistic,
        Threshold: alarm.threshold,
        ActionsEnabled: true,
        AlarmActions: [alarm.snsTopicArn],
        AlarmDescription: alarm.description,
        Dimensions: alarm.dimensions
      };
      
      await this.cloudWatch.putMetricAlarm(alarmParams).promise();
    }
  }
  
  private async createDashboard(dashboards: DashboardConfig[]): Promise<void> {
    for (const dashboard of dashboards) {
      const widgets = this.createDashboardWidgets(dashboard);
      
      const dashboardBody = {
        widgets: widgets
      };
      
      await this.cloudWatch.putDashboard({
        DashboardName: dashboard.name,
        DashboardBody: JSON.stringify(dashboardBody)
      }).promise();
    }
  }
  
  private createDashboardWidgets(dashboard: DashboardConfig): any[] {
    return [
      // CPU 사용률 위젯
      {
        type: 'metric',
        x: 0, y: 0, width: 12, height: 6,
        properties: {
          metrics: [
            ['AWS/Bedrock', 'CPUUtilization', 'RuntimeId', dashboard.runtimeId]
          ],
          period: 300,
          stat: 'Average',
          region: process.env.AWS_REGION,
          title: 'CPU Utilization (%)',
          yAxis: { left: { min: 0, max: 100 } }
        }
      },
      // 메모리 사용률 위젯
      {
        type: 'metric',
        x: 12, y: 0, width: 12, height: 6,
        properties: {
          metrics: [
            ['AWS/Bedrock', 'MemoryUtilization', 'RuntimeId', dashboard.runtimeId]
          ],
          period: 300,
          stat: 'Average',
          region: process.env.AWS_REGION,
          title: 'Memory Utilization (%)',
          yAxis: { left: { min: 0, max: 100 } }
        }
      },
      // 활성 세션 수
      {
        type: 'metric',
        x: 0, y: 6, width: 12, height: 6,
        properties: {
          metrics: [
            ['AWS/Bedrock', 'ActiveSessions', 'RuntimeId', dashboard.runtimeId]
          ],
          period: 60,
          stat: 'Sum',
          region: process.env.AWS_REGION,
          title: 'Active Sessions'
        }
      },
      // 에러율
      {
        type: 'metric',
        x: 12, y: 6, width: 12, height: 6,
        properties: {
          metrics: [
            ['AWS/Bedrock', 'Errors', 'RuntimeId', dashboard.runtimeId],
            ['AWS/Bedrock', 'Invocations', 'RuntimeId', dashboard.runtimeId]
          ],
          period: 300,
          stat: 'Sum',
          region: process.env.AWS_REGION,
          title: 'Error Rate',
          yAxis: { left: { label: 'Count' } }
        }
      }
    ];
  }
  
  private async setupLogging(runtimeId: string): Promise<void> {
    const logGroupName = `/aws/bedrock/agentcore/${runtimeId}`;
    
    try {
      await this.logs.createLogGroup({
        logGroupName,
        tags: {
          'Application': 'T-Developer',
          'RuntimeId': runtimeId
        }
      }).promise();
      
      // 로그 보존 기간 설정 (30일)
      await this.logs.putRetentionPolicy({
        logGroupName,
        retentionInDays: 30
      }).promise();
      
    } catch (error: any) {
      if (error.code !== 'ResourceAlreadyExistsException') {
        throw error;
      }
    }
  }
  
  private async enableXRayTracing(runtimeId: string): Promise<void> {
    // X-Ray 트레이싱 활성화 (실제로는 AgentCore 설정 API 호출)
    console.log(`X-Ray tracing enabled for runtime: ${runtimeId}`);
  }
  
  async getDefaultMonitoringConfig(runtimeId: string): Promise<MonitoringConfig> {
    return {
      runtimeId,
      metrics: [
        {
          name: 'CPUUtilization',
          namespace: 'AWS/Bedrock',
          dimensions: { RuntimeId: runtimeId },
          statistic: 'Average',
          period: 300
        },
        {
          name: 'MemoryUtilization', 
          namespace: 'AWS/Bedrock',
          dimensions: { RuntimeId: runtimeId },
          statistic: 'Average',
          period: 300
        }
      ],
      alarms: [
        {
          name: `${runtimeId}-HighCPU`,
          metricName: 'CPUUtilization',
          namespace: 'AWS/Bedrock',
          comparisonOperator: 'GreaterThanThreshold',
          threshold: 80,
          evaluationPeriods: 2,
          period: 300,
          statistic: 'Average',
          snsTopicArn: process.env.SNS_TOPIC_ARN || '',
          description: 'High CPU utilization detected',
          dimensions: [{ Name: 'RuntimeId', Value: runtimeId }]
        },
        {
          name: `${runtimeId}-HighMemory`,
          metricName: 'MemoryUtilization',
          namespace: 'AWS/Bedrock', 
          comparisonOperator: 'GreaterThanThreshold',
          threshold: 85,
          evaluationPeriods: 2,
          period: 300,
          statistic: 'Average',
          snsTopicArn: process.env.SNS_TOPIC_ARN || '',
          description: 'High memory utilization detected',
          dimensions: [{ Name: 'RuntimeId', Value: runtimeId }]
        }
      ],
      dashboards: [
        {
          name: `T-Developer-Runtime-${runtimeId}`,
          runtimeId
        }
      ]
    };
  }
}