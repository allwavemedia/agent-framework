/**
 * Approval Panel Component
 * Displays pending approval requests for human-in-the-loop workflows
 */
import { useState, useEffect } from 'react';

interface ApprovalRequest {
  id: number;
  workflow_id: string;
  request_type: string;
  request_data: Record<string, any>;
  status: string;
  created_at: string;
  updated_at?: string;
}

interface ApprovalPanelProps {
  workflowId?: string;
  onApprovalProcessed?: () => void;
}

export const ApprovalPanel: React.FC<ApprovalPanelProps> = ({ 
  workflowId, 
  onApprovalProcessed 
}) => {
  const [pendingApprovals, setPendingApprovals] = useState<ApprovalRequest[]>([]);
  const [selectedRequest, setSelectedRequest] = useState<ApprovalRequest | null>(null);
  const [feedback, setFeedback] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    loadPendingApprovals();
    // Poll for new approvals every 5 seconds
    const interval = setInterval(loadPendingApprovals, 5000);
    return () => clearInterval(interval);
  }, [workflowId]);

  const loadPendingApprovals = async () => {
    try {
      const endpoint = workflowId 
        ? `/api/v1/approvals/workflow/${workflowId}`
        : '/api/v1/approvals/pending';
      
      const response = await fetch(endpoint);
      if (!response.ok) {
        throw new Error('Failed to load approvals');
      }
      const data = await response.json();
      setPendingApprovals(data);
      setError(null);
    } catch (err) {
      const errorMsg = err instanceof Error ? err.message : 'Failed to load approvals';
      setError(errorMsg);
      console.error('Failed to load approvals:', err);
    }
  };

  const handleApprove = async (requestId: number) => {
    setLoading(true);
    try {
      const response = await fetch(`/api/v1/approvals/${requestId}/respond`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          approved: true,
          feedback: feedback || undefined
        })
      });
      
      if (!response.ok) {
        throw new Error('Failed to approve request');
      }
      
      setFeedback('');
      setSelectedRequest(null);
      await loadPendingApprovals();
      
      if (onApprovalProcessed) {
        onApprovalProcessed();
      }
    } catch (err) {
      const errorMsg = err instanceof Error ? err.message : 'Failed to approve';
      setError(errorMsg);
      console.error('Failed to approve:', err);
    } finally {
      setLoading(false);
    }
  };

  const handleReject = async (requestId: number) => {
    if (!feedback) {
      setError('Please provide feedback for rejection');
      return;
    }
    
    setLoading(true);
    try {
      const response = await fetch(`/api/v1/approvals/${requestId}/respond`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          approved: false,
          feedback: feedback
        })
      });
      
      if (!response.ok) {
        throw new Error('Failed to reject request');
      }
      
      setFeedback('');
      setSelectedRequest(null);
      await loadPendingApprovals();
      
      if (onApprovalProcessed) {
        onApprovalProcessed();
      }
    } catch (err) {
      const errorMsg = err instanceof Error ? err.message : 'Failed to reject';
      setError(errorMsg);
      console.error('Failed to reject:', err);
    } finally {
      setLoading(false);
    }
  };

  const cancelRequest = async (requestId: number) => {
    if (!confirm('Cancel this approval request?')) {
      return;
    }
    
    setLoading(true);
    try {
      const response = await fetch(`/api/v1/approvals/${requestId}/cancel`, {
        method: 'POST'
      });
      
      if (!response.ok) {
        throw new Error('Failed to cancel request');
      }
      
      await loadPendingApprovals();
    } catch (err) {
      const errorMsg = err instanceof Error ? err.message : 'Failed to cancel';
      setError(errorMsg);
      console.error('Failed to cancel:', err);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="border rounded-lg p-4 bg-white shadow-sm">
      <div className="flex justify-between items-center mb-4">
        <h3 className="text-lg font-semibold">Approval Requests</h3>
        <div className="flex items-center gap-2">
          <span className="text-sm text-gray-500">
            {pendingApprovals.length} pending
          </span>
          <button
            onClick={loadPendingApprovals}
            disabled={loading}
            className="text-sm px-3 py-1 rounded border hover:bg-gray-50 disabled:opacity-50"
          >
            🔄 Refresh
          </button>
        </div>
      </div>

      {error && (
        <div className="mb-4 p-3 bg-red-50 border border-red-200 rounded text-red-700 text-sm">
          {error}
        </div>
      )}

      {selectedRequest ? (
        <div className="space-y-4">
          {/* Approval Detail View */}
          <div className="border rounded p-3 bg-gray-50">
            <div className="flex justify-between items-start mb-3">
              <div>
                <div className="font-medium text-lg">Request #{selectedRequest.id}</div>
                <div className="text-sm text-gray-500">
                  Type: {selectedRequest.request_type}
                </div>
                <div className="text-sm text-gray-500">
                  Workflow: {selectedRequest.workflow_id}
                </div>
                <div className="text-sm text-gray-500">
                  Created: {new Date(selectedRequest.created_at).toLocaleString()}
                </div>
              </div>
              <button
                onClick={() => {
                  setSelectedRequest(null);
                  setFeedback('');
                  setError(null);
                }}
                className="text-gray-500 hover:text-gray-700"
              >
                ✕
              </button>
            </div>

            <div className="mb-4">
              <div className="font-medium mb-2">Request Data:</div>
              <pre className="text-xs bg-white p-3 rounded border overflow-auto max-h-40">
                {JSON.stringify(selectedRequest.request_data, null, 2)}
              </pre>
            </div>

            <div className="mb-4">
              <label className="block font-medium mb-2">
                Feedback / Comments:
              </label>
              <textarea
                value={feedback}
                onChange={(e) => setFeedback(e.target.value)}
                className="w-full p-2 border rounded text-sm"
                rows={4}
                placeholder="Add your feedback or comments..."
              />
            </div>

            <div className="flex gap-2">
              <button
                onClick={() => handleApprove(selectedRequest.id)}
                disabled={loading}
                className="flex-1 px-4 py-2 bg-green-600 text-white rounded hover:bg-green-700 disabled:opacity-50"
              >
                ✓ Approve
              </button>
              <button
                onClick={() => handleReject(selectedRequest.id)}
                disabled={loading || !feedback}
                className="flex-1 px-4 py-2 bg-red-600 text-white rounded hover:bg-red-700 disabled:opacity-50"
              >
                ✗ Reject
              </button>
            </div>
          </div>
        </div>
      ) : (
        <div className="space-y-2">
          {/* Approval List View */}
          {loading && pendingApprovals.length === 0 ? (
            <div className="text-center py-8 text-gray-500">
              <div className="animate-spin inline-block w-6 h-6 border-2 border-gray-300 border-t-blue-600 rounded-full" />
              <p className="mt-2">Loading approvals...</p>
            </div>
          ) : pendingApprovals.length === 0 ? (
            <div className="text-center py-8 text-gray-500">
              <p className="text-4xl mb-2">✓</p>
              <p>No pending approvals</p>
              <p className="text-sm mt-1">All caught up!</p>
            </div>
          ) : (
            pendingApprovals.map((request) => (
              <div
                key={request.id}
                className="border rounded p-3 hover:bg-gray-50 transition-colors cursor-pointer"
              >
                <div className="flex justify-between items-start">
                  <div 
                    className="flex-1"
                    onClick={() => setSelectedRequest(request)}
                  >
                    <div className="font-medium">
                      Request #{request.id}
                      <span className="ml-2 text-xs px-2 py-1 bg-yellow-100 text-yellow-800 rounded-full">
                        {request.request_type}
                      </span>
                    </div>
                    <div className="text-sm text-gray-500">
                      Workflow: {request.workflow_id}
                    </div>
                    <div className="text-xs text-gray-400">
                      {new Date(request.created_at).toLocaleString()}
                    </div>
                  </div>
                  <div className="flex gap-2 ml-4">
                    <button
                      onClick={(e) => {
                        e.stopPropagation();
                        setSelectedRequest(request);
                      }}
                      className="px-3 py-1 text-sm border border-blue-500 text-blue-600 rounded hover:bg-blue-50"
                    >
                      Review
                    </button>
                    <button
                      onClick={(e) => {
                        e.stopPropagation();
                        cancelRequest(request.id);
                      }}
                      className="px-3 py-1 text-sm border border-gray-500 text-gray-600 rounded hover:bg-gray-50"
                    >
                      Cancel
                    </button>
                  </div>
                </div>
              </div>
            ))
          )}
        </div>
      )}
    </div>
  );
};

export default ApprovalPanel;
