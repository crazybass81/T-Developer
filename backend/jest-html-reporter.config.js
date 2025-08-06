module.exports = {
  pageTitle: 'T-Developer Test Report',
  outputPath: 'test-reports/index.html',
  includeFailureMsg: true,
  includeConsoleLog: true,
  dateFormat: 'yyyy-mm-dd HH:MM:ss',
  theme: 'darkTheme',
  executionTimeWarningThreshold: 5000,
  
  customInfos: [
    {label: 'Environment', value: process.env.NODE_ENV || 'test'},
    {label: 'Node Version', value: process.version},
    {label: 'Test Runner', value: 'Jest'}
  ]
};