/**
 * T-Developer MVP - Agent Dashboard Component
 * 
 * 에이전트 상태 대시보드
 * 
 * @author T-Developer Team
 * @created 2025-01-31
 */

import React from 'react';

interface AgentDashboardProps {
  agents: Array<{
    id: string;
    name: string;
    status: string;
  }>;
}

const AgentDashboard: React.FC<AgentDashboardProps> = ({ agents }) => {
  return (
    <div className="agent-dashboard">
      <h2>Agent Status</h2>
      {agents.map(agent => (
        <div key={agent.id} className="agent-item">
          <span>{agent.name}</span>
          <span className={`status ${agent.status}`}>{agent.status}</span>
        </div>
      ))}
    </div>
  );
};

export default AgentDashboard;