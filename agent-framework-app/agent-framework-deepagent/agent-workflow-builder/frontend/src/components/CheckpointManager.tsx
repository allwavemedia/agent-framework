/**
 * Checkpoint Manager Component
 * Manages workflow checkpoints for save/resume functionality
 */
import { useState, useEffect } from 'react';

interface Checkpoint {
  checkpoint_id: string;
  created_at: string;
  metadata: Record<string, any>;
}

interface CheckpointManagerProps {
  workflowId: string;
  onRestore?: (checkpointId?: string) => void;
}

export const CheckpointManager: React.FC<CheckpointManagerProps> = ({ 
  workflowId, 
  onRestore 
}) => {
  const [checkpoints, setCheckpoints] = useState<Checkpoint[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (workflowId) {
      loadCheckpoints();
    }
  }, [workflowId]);

  const loadCheckpoints = async () => {
    setLoading(true);
    setError(null);
    try {
      const response = await fetch(`/api/v1/checkpoints/${workflowId}`);
      if (!response.ok) {
        throw new Error('Failed to load checkpoints');
      }
      const data = await response.json();
      setCheckpoints(data);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to load checkpoints');
      console.error('Failed to load checkpoints:', err);
    } finally {
      setLoading(false);
    }
  };

  const restoreCheckpoint = async (checkpointId?: string) => {
    try {
      const response = await fetch(`/api/v1/checkpoints/${workflowId}/restore`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ checkpoint_id: checkpointId })
      });
      
      if (!response.ok) {
        throw new Error('Failed to restore checkpoint');
      }
      
      const result = await response.json();
      
      if (onRestore) {
        onRestore(checkpointId);
      }
      
      alert(`Workflow restored from checkpoint: ${result.checkpoint_id}`);
    } catch (err) {
      const errorMsg = err instanceof Error ? err.message : 'Failed to restore checkpoint';
      setError(errorMsg);
      console.error('Failed to restore checkpoint:', err);
    }
  };

  const deleteCheckpoint = async (checkpointId: string) => {
    if (!confirm(`Delete checkpoint ${checkpointId}?`)) {
      return;
    }
    
    try {
      const response = await fetch(
        `/api/v1/checkpoints/${workflowId}/${checkpointId}`,
        { method: 'DELETE' }
      );
      
      if (!response.ok) {
        throw new Error('Failed to delete checkpoint');
      }
      
      // Reload checkpoints after deletion
      await loadCheckpoints();
    } catch (err) {
      const errorMsg = err instanceof Error ? err.message : 'Failed to delete checkpoint';
      setError(errorMsg);
      console.error('Failed to delete checkpoint:', err);
    }
  };

  return (
    <div className="border rounded-lg p-4 bg-white shadow-sm">
      <div className="flex justify-between items-center mb-4">
        <h3 className="text-lg font-semibold">Workflow Checkpoints</h3>
        <button
          onClick={loadCheckpoints}
          disabled={loading}
          className="text-sm px-3 py-1 rounded border hover:bg-gray-50 disabled:opacity-50"
        >
          {loading ? 'Loading...' : '🔄 Refresh'}
        </button>
      </div>

      {error && (
        <div className="mb-4 p-3 bg-red-50 border border-red-200 rounded text-red-700 text-sm">
          {error}
        </div>
      )}

      <button
        onClick={() => restoreCheckpoint()}
        className="w-full mb-4 px-4 py-2 bg-blue-600 text-white rounded hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed"
        disabled={checkpoints.length === 0 || loading}
      >
        Restore Latest Checkpoint
      </button>

      <div className="space-y-2">
        {loading ? (
          <div className="text-center py-8 text-gray-500">
            <div className="animate-spin inline-block w-6 h-6 border-2 border-gray-300 border-t-blue-600 rounded-full" />
            <p className="mt-2">Loading checkpoints...</p>
          </div>
        ) : checkpoints.length === 0 ? (
          <div className="text-center py-8 text-gray-500">
            <p className="text-4xl mb-2">📦</p>
            <p>No checkpoints available</p>
            <p className="text-sm mt-1">Checkpoints will be created automatically during workflow execution</p>
          </div>
        ) : (
          checkpoints.map((cp) => (
            <div
              key={cp.checkpoint_id}
              className="border rounded p-3 hover:bg-gray-50 transition-colors"
            >
              <div className="flex justify-between items-start">
                <div className="flex-1">
                  <p className="font-medium text-gray-900">{cp.checkpoint_id}</p>
                  <p className="text-sm text-gray-500">
                    {new Date(cp.created_at).toLocaleString()}
                  </p>
                  {cp.metadata && Object.keys(cp.metadata).length > 0 && (
                    <div className="mt-2 text-xs text-gray-600">
                      {Object.entries(cp.metadata).map(([key, value]) => (
                        <span key={key} className="inline-block mr-2">
                          <strong>{key}:</strong> {String(value)}
                        </span>
                      ))}
                    </div>
                  )}
                </div>
                <div className="flex gap-2 ml-4">
                  <button
                    onClick={() => restoreCheckpoint(cp.checkpoint_id)}
                    className="px-3 py-1 text-sm border border-blue-500 text-blue-600 rounded hover:bg-blue-50 transition-colors"
                  >
                    Restore
                  </button>
                  <button
                    onClick={() => deleteCheckpoint(cp.checkpoint_id)}
                    className="px-3 py-1 text-sm border border-red-500 text-red-600 rounded hover:bg-red-50 transition-colors"
                  >
                    Delete
                  </button>
                </div>
              </div>
            </div>
          ))
        )}
      </div>
    </div>
  );
};

export default CheckpointManager;
