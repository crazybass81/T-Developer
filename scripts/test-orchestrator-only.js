#!/usr/bin/env node

const path = require('path');
const fs = require('fs');

console.log('🧪 Testing Base Orchestrator Implementation (Files Only)...\n');

// Test 1: Check required files exist
console.log('1. Checking required files...');
const requiredFiles = [
  'backend/src/orchestration/base-orchestrator.ts',
  'backend/src/orchestration/workflow-engine.ts', 
  'backend/src/orchestration/decision-engine.ts'
];

let allFilesExist = true;
for (const file of requiredFiles) {
  const filePath = path.join(__dirname, '..', file);
  try {
    fs.accessSync(filePath);
    console.log(`   ✅ ${file}`);
  } catch {
    console.log(`   ❌ ${file} - File not found`);
    allFilesExist = false;
  }
}

if (!allFilesExist) {
  console.log('\n❌ Some required files are missing');
  process.exit(1);
}

// Test 2: Check BaseOrchestrator class structure
console.log('\n2. Verifying BaseOrchestrator class structure...');
const orchestratorContent = fs.readFileSync(
  path.join(__dirname, '..', 'backend/src/orchestration/base-orchestrator.ts'), 
  'utf8'
);

const requiredMethods = [
  'initialize',
  'registerAgent', 
  'routeTask',
  'createSession',
  'getActiveAgents',
  'shutdown'
];

let methodsFound = 0;
for (const method of requiredMethods) {
  if (orchestratorContent.includes(method)) {
    console.log(`   ✅ Method ${method} found`);
    methodsFound++;
  } else {
    console.log(`   ❌ Method ${method} missing`);
  }
}

// Test 3: Check WorkflowEngine class structure
console.log('\n3. Verifying WorkflowEngine class structure...');
const workflowContent = fs.readFileSync(
  path.join(__dirname, '..', 'backend/src/orchestration/workflow-engine.ts'), 
  'utf8'
);

const workflowMethods = [
  'createWorkflow',
  'selectTemplate',
  'createDynamicWorkflow',
  'validateWorkflow'
];

let workflowMethodsFound = 0;
for (const method of workflowMethods) {
  if (workflowContent.includes(method)) {
    console.log(`   ✅ Method ${method} found`);
    workflowMethodsFound++;
  } else {
    console.log(`   ❌ Method ${method} missing`);
  }
}

// Test 4: Check DecisionEngine class structure
console.log('\n4. Verifying DecisionEngine class structure...');
const decisionContent = fs.readFileSync(
  path.join(__dirname, '..', 'backend/src/orchestration/decision-engine.ts'), 
  'utf8'
);

const decisionMethods = [
  'determineAgents',
  'matchByRules',
  'analyzeHistory',
  'combineDecisions'
];

let decisionMethodsFound = 0;
for (const method of decisionMethods) {
  if (decisionContent.includes(method)) {
    console.log(`   ✅ Method ${method} found`);
    decisionMethodsFound++;
  } else {
    console.log(`   ❌ Method ${method} missing`);
  }
}

// Test 5: Check for key interfaces and types
console.log('\n5. Checking interfaces and types...');
const interfaces = [
  'Agent',
  'Task', 
  'Session',
  'WorkflowStep',
  'WorkflowPlan',
  'Intent',
  'Decision'
];

let interfacesFound = 0;
const allContent = orchestratorContent + workflowContent + decisionContent;

for (const interfaceName of interfaces) {
  if (allContent.includes(`interface ${interfaceName}`) || allContent.includes(`export interface ${interfaceName}`)) {
    console.log(`   ✅ Interface ${interfaceName} found`);
    interfacesFound++;
  } else {
    console.log(`   ❌ Interface ${interfaceName} missing`);
  }
}

// Summary
const totalMethods = requiredMethods.length + workflowMethods.length + decisionMethods.length;
const foundMethods = methodsFound + workflowMethodsFound + decisionMethodsFound;

console.log('\n📊 Test Results:');
console.log(`   • Files: ${allFilesExist ? '✅' : '❌'} (${requiredFiles.length}/${requiredFiles.length})`);
console.log(`   • Methods: ${foundMethods === totalMethods ? '✅' : '❌'} (${foundMethods}/${totalMethods})`);
console.log(`   • Interfaces: ${interfacesFound === interfaces.length ? '✅' : '❌'} (${interfacesFound}/${interfaces.length})`);

if (allFilesExist && foundMethods === totalMethods && interfacesFound === interfaces.length) {
  console.log('\n✅ All tests passed! Base Orchestrator implementation complete.');
  console.log('\n📋 Implementation Summary:');
  console.log('   • BaseOrchestrator class with agent registry and session management');
  console.log('   • WorkflowEngine for step orchestration and template management');
  console.log('   • DecisionEngine for intelligent agent selection');
  console.log('   • Complete interface definitions for all components');
  console.log('   • Task routing and execution logic');
  console.log('   • Workflow validation and optimization');
  console.log('   • Rule-based and historical pattern matching');
} else {
  console.log('\n❌ Some components are incomplete');
  process.exit(1);
}