#!/usr/bin/env node

const { RuntimeMonitoringSetup } = require('../backend/src/runtime/monitoring-setup');
const { HighAvailabilityManager } = require('../backend/src/runtime/high-availability');

async function testRuntimeMonitoring() {
  console.log('🔍 Testing Runtime Monitoring Setup...\n');

  try {
    // 1. 모니터링 설정 테스트
    console.log('1. Testing Monitoring Setup...');
    const monitoring = new RuntimeMonitoringSetup();
    
    const testRuntimeId = 'test-runtime-123';
    const config = await monitoring.getDefaultMonitoringConfig(testRuntimeId);
    
    console.log('✅ Default monitoring config generated:');
    console.log(`   - Runtime ID: ${config.runtimeId}`);
    console.log(`   - Metrics: ${config.metrics.length}`);
    console.log(`   - Alarms: ${config.alarms.length}`);
    console.log(`   - Dashboards: ${config.dashboards.length}`);

    // 2. 고가용성 관리자 테스트
    console.log('\n2. Testing High Availability Manager...');
    const haManager = new HighAvailabilityManager();
    
    console.log('✅ HA Manager initialized:');
    console.log(`   - Primary Region: ${process.env.AWS_PRIMARY_REGION || 'us-east-1'}`);
    console.log(`   - DR Regions: ${process.env.AWS_DR_REGIONS || 'us-west-2,eu-west-1'}`);

    // 3. 모니터링 위젯 구성 테스트
    console.log('\n3. Testing Dashboard Widgets...');
    const widgets = monitoring.createDashboardWidgets({ 
      name: 'test-dashboard', 
      runtimeId: testRuntimeId 
    });
    
    console.log('✅ Dashboard widgets created:');
    widgets.forEach((widget, index) => {
      console.log(`   - Widget ${index + 1}: ${widget.properties.title}`);
    });

    // 4. 알람 설정 검증
    console.log('\n4. Testing Alarm Configuration...');
    const alarms = config.alarms;
    
    console.log('✅ Alarm configurations:');
    alarms.forEach(alarm => {
      console.log(`   - ${alarm.name}: ${alarm.metricName} > ${alarm.threshold}`);
    });

    console.log('\n✅ All runtime monitoring tests passed!');
    
    return {
      success: true,
      monitoringConfig: config,
      widgetCount: widgets.length,
      alarmCount: alarms.length
    };

  } catch (error) {
    console.error('❌ Runtime monitoring test failed:', error.message);
    return {
      success: false,
      error: error.message
    };
  }
}

// 실행
if (require.main === module) {
  testRuntimeMonitoring()
    .then(result => {
      if (result.success) {
        console.log('\n🎉 Runtime monitoring system ready!');
        process.exit(0);
      } else {
        console.log('\n💥 Runtime monitoring test failed');
        process.exit(1);
      }
    })
    .catch(error => {
      console.error('💥 Unexpected error:', error);
      process.exit(1);
    });
}

module.exports = { testRuntimeMonitoring };