/**
 * Orchestration Panel Component
 * Displays agent-to-agent handoffs and collaboration state
 */
import { useState, useEffect } from 'react';

interface HandoffState {
  id: number;
  workflow_id: string;
  execution_id?: number;
  current_agent_id: string;
  previous_agent_id?: string;
  handoff_reason?: string;
  context_data: Record<string, any>;
  created_at: string;
  updated_at?: string;
}

interface OrchestrationPanelProps {
  workflowId?: string;
  onRefresh?: () => void;
}

export const OrchestrationPanel: React.FC<OrchestrationPanelProps> = ({ 
  workflowId, 
  onRefresh 
}) => {
  const [handoffs, setHandoffs] = useState<HandoffState[]>([]);
  const [selectedHandoff, setSelectedHandoff] = useState<HandoffState | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [autoRefresh, setAutoRefresh] = useState(true);

  useEffect(() => {
    loadHandoffs();
    
    // Auto-refresh every 5 seconds if enabled
    if (autoRefresh) {
      const interval = setInterval(loadHandoffs, 5000);
      return () => clearInterval(interval);
    }
  }, [workflowId, autoRefresh]);

  const loadHandoffs = async () => {
    try {
      setLoading(true);
      const endpoint = workflowId 
        ? `/api/v1/api/orchestration/handoffs?workflow_id=${workflowId}`
        : '/api/v1/api/orchestration/handoffs';
      
      const response = await fetch(endpoint);
      if (!response.ok) {
        throw new Error('Failed to load handoffs');
      }
      const data = await response.json();
      setHandoffs(data);
      setError(null);
      
      if (onRefresh) {
        onRefresh();
      }
    } catch (err) {
      const errorMsg = err instanceof Error ? err.message : 'Failed to load handoffs';
      setError(errorMsg);
      console.error('Failed to load handoffs:', err);
    } finally {
      setLoading(false);
    }
  };

  const formatTimestamp = (timestamp: string) => {
    return new Date(timestamp).toLocaleString();
  };

  const getHandoffTypeColor = (reason?: string) => {
    if (!reason) return 'bg-gray-500';
    const lowerReason = reason.toLowerCase();
    if (lowerReason.includes('escalat')) return 'bg-red-500';
    if (lowerReason.includes('special')) return 'bg-blue-500';
    if (lowerReason.includes('collaborat')) return 'bg-green-500';
    if (lowerReason.includes('delegat')) return 'bg-purple-500';
    return 'bg-gray-500';
  };

  return (
    <div className="orchestration-panel bg-white rounded-lg shadow p-4">
      {/* Header */}
      <div className="flex justify-between items-center mb-4">
        <h2 className="text-xl font-bold text-gray-800">
          Agent Handoffs
        </h2>
        <div className="flex gap-2">
          <label className="flex items-center gap-2 text-sm">
            <input
              type="checkbox"
              checked={autoRefresh}
              onChange={(e) => setAutoRefresh(e.target.checked)}
              className="rounded"
            />
            Auto-refresh
          </label>
          <button
            onClick={loadHandoffs}
            disabled={loading}
            className="px-3 py-1 bg-blue-500 text-white rounded hover:bg-blue-600 disabled:bg-gray-400 text-sm"
          >
            {loading ? 'Loading...' : 'Refresh'}
          </button>
        </div>
      </div>

      {/* Error Message */}
      {error && (
        <div className="bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded mb-4">
          <p className="text-sm">{error}</p>
        </div>
      )}

      {/* Handoffs List */}
      {!selectedHandoff ? (
        <div className="space-y-3">
          {handoffs.length === 0 && !loading && (
            <div className="text-center text-gray-500 py-8">
              <p>No handoffs recorded</p>
              {workflowId && (
                <p className="text-sm mt-2">
                  Handoffs will appear here when agents transfer control during workflow execution
                </p>
              )}
            </div>
          )}

          {handoffs.map((handoff) => (
            <div
              key={handoff.id}
              className="border rounded-lg p-4 hover:shadow-md cursor-pointer transition-shadow"
              onClick={() => setSelectedHandoff(handoff)}
            >
              <div className="flex justify-between items-start mb-2">
                <div className="flex-1">
                  <div className="flex items-center gap-2 mb-1">
                    {handoff.previous_agent_id && (
                      <>
                        <span className="font-medium text-gray-700">
                          {handoff.previous_agent_id}
                        </span>
                        <svg className="w-5 h-5 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 7l5 5m0 0l-5 5m5-5H6" />
                        </svg>
                      </>
                    )}
                    <span className="font-bold text-gray-900">
                      {handoff.current_agent_id}
                    </span>
                  </div>
                  
                  {handoff.handoff_reason && (
                    <div className="flex items-center gap-2 mt-2">
                      <span className={`px-2 py-1 rounded text-xs text-white ${getHandoffTypeColor(handoff.handoff_reason)}`}>
                        {handoff.handoff_reason}
                      </span>
                    </div>
                  )}
                </div>
                
                <div className="text-right text-sm text-gray-500">
                  <p>{formatTimestamp(handoff.created_at)}</p>
                  <p className="text-xs mt-1">ID: {handoff.id}</p>
                </div>
              </div>
              
              <div className="text-xs text-gray-600 mt-2">
                <p>Workflow: {handoff.workflow_id}</p>
                {handoff.execution_id && <p>Execution: {handoff.execution_id}</p>}
              </div>
            </div>
          ))}
        </div>
      ) : (
        /* Detail View */
        <div className="space-y-4">
          <button
            onClick={() => setSelectedHandoff(null)}
            className="text-blue-500 hover:text-blue-700 text-sm flex items-center gap-1"
          >
            <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M10 19l-7-7m0 0l7-7m-7 7h18" />
            </svg>
            Back to list
          </button>
          
          <div className="bg-gray-50 rounded-lg p-4">
            <h3 className="font-bold text-lg mb-4">Handoff Details</h3>
            
            <div className="space-y-3">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Handoff ID
                </label>
                <p className="text-gray-900">{selectedHandoff.id}</p>
              </div>
              
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Workflow ID
                </label>
                <p className="text-gray-900">{selectedHandoff.workflow_id}</p>
              </div>
              
              {selectedHandoff.execution_id && (
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    Execution ID
                  </label>
                  <p className="text-gray-900">{selectedHandoff.execution_id}</p>
                </div>
              )}
              
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Agent Flow
                </label>
                <div className="flex items-center gap-2 bg-white p-3 rounded border">
                  {selectedHandoff.previous_agent_id && (
                    <>
                      <span className="px-3 py-1 bg-gray-200 rounded font-medium">
                        {selectedHandoff.previous_agent_id}
                      </span>
                      <svg className="w-6 h-6 text-gray-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 7l5 5m0 0l-5 5m5-5H6" />
                      </svg>
                    </>
                  )}
                  <span className="px-3 py-1 bg-blue-500 text-white rounded font-medium">
                    {selectedHandoff.current_agent_id}
                  </span>
                </div>
              </div>
              
              {selectedHandoff.handoff_reason && (
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    Handoff Reason
                  </label>
                  <p className="text-gray-900">{selectedHandoff.handoff_reason}</p>
                </div>
              )}
              
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Timestamp
                </label>
                <p className="text-gray-900">{formatTimestamp(selectedHandoff.created_at)}</p>
              </div>
              
              {Object.keys(selectedHandoff.context_data).length > 0 && (
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    Context Data
                  </label>
                  <pre className="bg-white p-3 rounded border text-xs overflow-auto max-h-64">
                    {JSON.stringify(selectedHandoff.context_data, null, 2)}
                  </pre>
                </div>
              )}
            </div>
          </div>
        </div>
      )}
    </div>
  );
};
