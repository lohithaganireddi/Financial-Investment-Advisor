import React from 'react';
import { Bot } from 'lucide-react';
import { useFinancial } from '../context/FinancialContext';
import AgentDashboard from '../components/AgentDashboard';

export default function AgentActivity() {
  const { agentActivity, decisionTrace, analysisContext } = useFinancial();

  return (
    <div className="page-container">
      <div className="page-header">
        <div>
          <h2 className="page-title">
            <Bot size={24} color="#06b6d4" />
            Agent Activity & Execution Telemetry
          </h2>
          <p className="page-subtitle">
            Real-time tracking of multi-agent pipeline order, step-by-step execution summaries, decision traces, and telemetry logs.
          </p>
        </div>
      </div>

      <AgentDashboard agentActivity={agentActivity} context={analysisContext} decisionTrace={decisionTrace} />
    </div>
  );
}
