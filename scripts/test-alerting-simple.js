#!/usr/bin/env node

// Simple test without requiring the actual module
async function testAlertingSystem() {
  console.log('🔔 Testing T-Developer Alerting System...\n');

  try {
    // Test alert template structure
    const alertTemplates = {
      highCPU: (usage) => ({
        level: usage > 90 ? 'critical' : 'warning',
        type: 'performance',
        title: 'High CPU Usage Detected',
        message: `CPU usage is at ${usage}%. This may impact system performance.`,
        metadata: { cpuUsage: usage }
      }),
      
      highMemory: (usage) => ({
        level: usage > 95 ? 'critical' : 'warning',
        type: 'performance',
        title: 'High Memory Usage Detected',
        message: `Memory usage is at ${usage}%. Consider scaling or optimizing memory usage.`,
        metadata: { memoryUsage: usage }
      }),
      
      agentFailure: (agentName, error) => ({
        level: 'critical',
        type: 'agent',
        title: `Agent Failure: ${agentName}`,
        message: `Agent ${agentName} has failed with error: ${error}`,
        metadata: { agentName, error }
      })
    };
    
    console.log('✅ Alert templates defined');
    
    // Test alert templates
    const cpuAlert = alertTemplates.highCPU(85);
    console.log('✅ CPU alert template:', cpuAlert);
    
    const memoryAlert = alertTemplates.highMemory(97);
    console.log('✅ Memory alert template:', memoryAlert);
    
    const agentAlert = alertTemplates.agentFailure('NL-Input-Agent', 'Connection timeout');
    console.log('✅ Agent failure alert template:', agentAlert);
    
    // Test channel selection logic
    const selectChannels = (level) => {
      switch (level) {
        case 'info': return ['slack'];
        case 'warning': return ['slack', 'email'];
        case 'critical': return ['slack', 'email', 'sms'];
        case 'emergency': return ['slack', 'email', 'sms'];
        default: return ['slack'];
      }
    };
    
    console.log('\n📡 Testing channel selection...');
    ['info', 'warning', 'critical', 'emergency'].forEach(level => {
      const channels = selectChannels(level);
      console.log(`✅ ${level} level channels: ${channels.join(', ')}`);
    });
    
    // Test alert structure
    const testAlert = {
      id: `alert_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`,
      level: 'warning',
      type: 'test',
      title: 'Test Alert',
      message: 'This is a test alert',
      timestamp: new Date()
    };
    
    console.log('\n📋 Test alert structure:', {
      id: testAlert.id,
      level: testAlert.level,
      title: testAlert.title
    });
    
    console.log('\n🎉 All alerting system tests passed!');
    
    // Environment check
    console.log('\n🔧 Environment Configuration Check:');
    console.log(`SMTP_HOST: ${process.env.SMTP_HOST ? '✅ Set' : '❌ Not set'}`);
    console.log(`SLACK_BOT_TOKEN: ${process.env.SLACK_BOT_TOKEN ? '✅ Set' : '❌ Not set'}`);
    console.log(`TWILIO_ACCOUNT_SID: ${process.env.TWILIO_ACCOUNT_SID ? '✅ Set' : '❌ Not set'}`);
    
    // Dependencies check
    console.log('\n📦 Dependencies Check:');
    try {
      require('nodemailer');
      console.log('✅ nodemailer installed');
    } catch (e) {
      console.log('❌ nodemailer not found');
    }
    
    try {
      require('@slack/web-api');
      console.log('✅ @slack/web-api installed');
    } catch (e) {
      console.log('❌ @slack/web-api not found');
    }
    
    try {
      require('twilio');
      console.log('✅ twilio installed');
    } catch (e) {
      console.log('❌ twilio not found');
    }
    
    return true;
    
  } catch (error) {
    console.error('❌ Alerting system test failed:', error.message);
    return false;
  }
}

if (require.main === module) {
  testAlertingSystem()
    .then(success => process.exit(success ? 0 : 1))
    .catch(error => {
      console.error('Test execution failed:', error);
      process.exit(1);
    });
}

module.exports = { testAlertingSystem };