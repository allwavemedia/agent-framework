/**
 * Plan Review Panel Component
 * Displays Magentic One plan review requests for human approval
 */
import { useState, useEffect } from 'react';

interface PlanReviewRequest {
  id: number;
  workflow_id: string;
  execution_id?: number;
  task_text: string;
  facts_text: string;
  plan_text: string;
  round_index: number;
  status: string;
  decision?: string;
  edited_plan_text?: string;
  comments?: string;
  created_at: string;
  reviewed_at?: string;
}

interface PlanReviewPanelProps {
  workflowId?: string;
  onReviewProcessed?: () => void;
}

export const PlanReviewPanel: React.FC<PlanReviewPanelProps> = ({ 
  workflowId, 
  onReviewProcessed 
}) => {
  const [reviews, setReviews] = useState<PlanReviewRequest[]>([]);
  const [selectedReview, setSelectedReview] = useState<PlanReviewRequest | null>(null);
  const [editedPlan, setEditedPlan] = useState('');
  const [comments, setComments] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [filter, setFilter] = useState<'all' | 'pending' | 'approved' | 'revised'>('pending');

  useEffect(() => {
    loadReviews();
    // Poll for new reviews every 5 seconds
    const interval = setInterval(loadReviews, 5000);
    return () => clearInterval(interval);
  }, [workflowId, filter]);

  const loadReviews = async () => {
    try {
      let endpoint = '/api/v1/api/orchestration/plan-reviews';
      const params = new URLSearchParams();
      
      if (workflowId) {
        params.append('workflow_id', workflowId);
      }
      if (filter !== 'all') {
        params.append('status', filter);
      }
      
      const queryString = params.toString();
      if (queryString) {
        endpoint += `?${queryString}`;
      }
      
      const response = await fetch(endpoint);
      if (!response.ok) {
        throw new Error('Failed to load plan reviews');
      }
      const data = await response.json();
      setReviews(data);
      setError(null);
    } catch (err) {
      const errorMsg = err instanceof Error ? err.message : 'Failed to load reviews';
      setError(errorMsg);
      console.error('Failed to load reviews:', err);
    }
  };

  const handleApprove = async (reviewId: number) => {
    setLoading(true);
    try {
      const response = await fetch(`/api/v1/api/orchestration/plan-reviews/${reviewId}/decide`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          decision: 'approve',
          comments: comments || undefined,
          edited_plan_text: editedPlan || undefined
        })
      });
      
      if (!response.ok) {
        throw new Error('Failed to approve plan');
      }
      
      setComments('');
      setEditedPlan('');
      setSelectedReview(null);
      await loadReviews();
      
      if (onReviewProcessed) {
        onReviewProcessed();
      }
    } catch (err) {
      const errorMsg = err instanceof Error ? err.message : 'Failed to approve';
      setError(errorMsg);
      console.error('Failed to approve:', err);
    } finally {
      setLoading(false);
    }
  };

  const handleRevise = async (reviewId: number) => {
    if (!comments) {
      setError('Please provide comments for revision request');
      return;
    }
    
    setLoading(true);
    try {
      const response = await fetch(`/api/v1/api/orchestration/plan-reviews/${reviewId}/decide`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          decision: 'revise',
          comments: comments,
          edited_plan_text: editedPlan || undefined
        })
      });
      
      if (!response.ok) {
        throw new Error('Failed to request revision');
      }
      
      setComments('');
      setEditedPlan('');
      setSelectedReview(null);
      await loadReviews();
      
      if (onReviewProcessed) {
        onReviewProcessed();
      }
    } catch (err) {
      const errorMsg = err instanceof Error ? err.message : 'Failed to request revision';
      setError(errorMsg);
      console.error('Failed to request revision:', err);
    } finally {
      setLoading(false);
    }
  };

  const formatTimestamp = (timestamp: string) => {
    return new Date(timestamp).toLocaleString();
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'pending': return 'bg-yellow-500';
      case 'approved': return 'bg-green-500';
      case 'revised': return 'bg-blue-500';
      default: return 'bg-gray-500';
    }
  };

  const getStatusText = (status: string) => {
    return status.charAt(0).toUpperCase() + status.slice(1);
  };

  return (
    <div className="plan-review-panel bg-white rounded-lg shadow p-4">
      {/* Header */}
      <div className="flex justify-between items-center mb-4">
        <h2 className="text-xl font-bold text-gray-800">
          Plan Reviews
        </h2>
        <div className="flex gap-2">
          <select
            value={filter}
            onChange={(e) => setFilter(e.target.value as any)}
            className="px-3 py-1 border rounded text-sm"
          >
            <option value="all">All</option>
            <option value="pending">Pending</option>
            <option value="approved">Approved</option>
            <option value="revised">Revised</option>
          </select>
          <button
            onClick={loadReviews}
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
          <button
            onClick={() => setError(null)}
            className="text-xs underline mt-1"
          >
            Dismiss
          </button>
        </div>
      )}

      {/* Reviews List */}
      {!selectedReview ? (
        <div className="space-y-3">
          {reviews.length === 0 && !loading && (
            <div className="text-center text-gray-500 py-8">
              <p>No plan reviews found</p>
              {filter !== 'all' && (
                <p className="text-sm mt-2">
                  Try changing the filter to see more reviews
                </p>
              )}
            </div>
          )}

          {reviews.map((review) => (
            <div
              key={review.id}
              className="border rounded-lg p-4 hover:shadow-md cursor-pointer transition-shadow"
              onClick={() => {
                setSelectedReview(review);
                setEditedPlan(review.plan_text);
                setComments(review.comments || '');
              }}
            >
              <div className="flex justify-between items-start mb-2">
                <div className="flex-1">
                  <div className="flex items-center gap-2 mb-1">
                    <h3 className="font-bold text-gray-900 truncate">
                      {review.task_text}
                    </h3>
                    <span className={`px-2 py-1 rounded text-xs text-white ${getStatusColor(review.status)}`}>
                      {getStatusText(review.status)}
                    </span>
                  </div>
                  
                  <p className="text-sm text-gray-600 line-clamp-2">
                    {review.plan_text}
                  </p>
                </div>
                
                <div className="text-right text-sm text-gray-500 ml-4">
                  <p>{formatTimestamp(review.created_at)}</p>
                  <p className="text-xs mt-1">Round: {review.round_index + 1}</p>
                </div>
              </div>
              
              <div className="text-xs text-gray-600 mt-2">
                <p>Workflow: {review.workflow_id}</p>
                {review.reviewed_at && (
                  <p className="mt-1">Reviewed: {formatTimestamp(review.reviewed_at)}</p>
                )}
              </div>
            </div>
          ))}
        </div>
      ) : (
        /* Detail View */
        <div className="space-y-4">
          <button
            onClick={() => {
              setSelectedReview(null);
              setEditedPlan('');
              setComments('');
              setError(null);
            }}
            className="text-blue-500 hover:text-blue-700 text-sm flex items-center gap-1"
          >
            <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M10 19l-7-7m0 0l7-7m-7 7h18" />
            </svg>
            Back to list
          </button>
          
          <div className="bg-gray-50 rounded-lg p-4">
            <div className="flex justify-between items-center mb-4">
              <h3 className="font-bold text-lg">Plan Review Details</h3>
              <span className={`px-3 py-1 rounded text-sm text-white ${getStatusColor(selectedReview.status)}`}>
                {getStatusText(selectedReview.status)}
              </span>
            </div>
            
            <div className="space-y-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Task
                </label>
                <p className="text-gray-900 bg-white p-3 rounded border">
                  {selectedReview.task_text}
                </p>
              </div>
              
              {selectedReview.facts_text && (
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    Gathered Facts
                  </label>
                  <p className="text-gray-900 bg-white p-3 rounded border whitespace-pre-wrap">
                    {selectedReview.facts_text}
                  </p>
                </div>
              )}
              
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Generated Plan
                  {selectedReview.status === 'pending' && (
                    <span className="ml-2 text-xs text-gray-500">(You can edit the plan below)</span>
                  )}
                </label>
                {selectedReview.status === 'pending' ? (
                  <textarea
                    value={editedPlan}
                    onChange={(e) => setEditedPlan(e.target.value)}
                    className="w-full h-40 p-3 border rounded font-mono text-sm"
                    placeholder="Edit the plan..."
                  />
                ) : (
                  <pre className="bg-white p-3 rounded border text-sm whitespace-pre-wrap">
                    {selectedReview.plan_text}
                  </pre>
                )}
              </div>
              
              {selectedReview.decision && (
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    Decision
                  </label>
                  <p className="text-gray-900 capitalize">{selectedReview.decision}</p>
                </div>
              )}
              
              {selectedReview.status === 'pending' ? (
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    Comments / Feedback
                    {selectedReview.status === 'pending' && (
                      <span className="ml-2 text-xs text-gray-500">(Required for revision)</span>
                    )}
                  </label>
                  <textarea
                    value={comments}
                    onChange={(e) => setComments(e.target.value)}
                    className="w-full h-24 p-3 border rounded text-sm"
                    placeholder="Provide feedback or comments..."
                  />
                </div>
              ) : (
                selectedReview.comments && (
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">
                      Comments
                    </label>
                    <p className="text-gray-900 bg-white p-3 rounded border whitespace-pre-wrap">
                      {selectedReview.comments}
                    </p>
                  </div>
                )
              )}
              
              <div className="grid grid-cols-2 gap-4 text-sm">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    Created
                  </label>
                  <p className="text-gray-900">{formatTimestamp(selectedReview.created_at)}</p>
                </div>
                
                {selectedReview.reviewed_at && (
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">
                      Reviewed
                    </label>
                    <p className="text-gray-900">{formatTimestamp(selectedReview.reviewed_at)}</p>
                  </div>
                )}
                
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    Workflow ID
                  </label>
                  <p className="text-gray-900 font-mono text-xs">{selectedReview.workflow_id}</p>
                </div>
                
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    Review Round
                  </label>
                  <p className="text-gray-900">{selectedReview.round_index + 1}</p>
                </div>
              </div>
              
              {/* Action Buttons (only for pending reviews) */}
              {selectedReview.status === 'pending' && (
                <div className="flex gap-3 pt-4 border-t">
                  <button
                    onClick={() => handleApprove(selectedReview.id)}
                    disabled={loading}
                    className="flex-1 px-4 py-2 bg-green-500 text-white rounded hover:bg-green-600 disabled:bg-gray-400 font-medium"
                  >
                    {loading ? 'Processing...' : 'Approve Plan'}
                  </button>
                  <button
                    onClick={() => handleRevise(selectedReview.id)}
                    disabled={loading}
                    className="flex-1 px-4 py-2 bg-blue-500 text-white rounded hover:bg-blue-600 disabled:bg-gray-400 font-medium"
                  >
                    {loading ? 'Processing...' : 'Request Revision'}
                  </button>
                </div>
              )}
            </div>
          </div>
        </div>
      )}
    </div>
  );
};
