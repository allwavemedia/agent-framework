/**
 * Custom hooks for Agent Workflow Builder
 */
import { useState, useEffect } from 'react';
import { apiClient } from '../api/client';
import type { Agent, Workflow, WorkflowExecution } from '../types';

export function useAgents() {
  const [agents, setAgents] = useState<Agent[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const fetchAgents = async () => {
    try {
      setLoading(true);
      const data = await apiClient.getAgents();
      setAgents(data);
      setError(null);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to fetch agents');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchAgents();
  }, []);

  return { agents, loading, error, refetch: fetchAgents };
}

export function useWorkflows() {
  const [workflows, setWorkflows] = useState<Workflow[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const fetchWorkflows = async () => {
    try {
      setLoading(true);
      const data = await apiClient.getWorkflows();
      setWorkflows(data);
      setError(null);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to fetch workflows');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchWorkflows();
  }, []);

  return { workflows, loading, error, refetch: fetchWorkflows };
}

export function useWorkflow(id: number | null) {
  const [workflow, setWorkflow] = useState<Workflow | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const fetchWorkflow = async () => {
    if (!id) {
      setWorkflow(null);
      setLoading(false);
      return;
    }

    try {
      setLoading(true);
      const data = await apiClient.getWorkflow(id);
      setWorkflow(data);
      setError(null);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to fetch workflow');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchWorkflow();
  }, [id]);

  return { workflow, loading, error, refetch: fetchWorkflow };
}

export function useExecutions(workflowId?: number) {
  const [executions, setExecutions] = useState<WorkflowExecution[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const fetchExecutions = async () => {
    try {
      setLoading(true);
      const data = await apiClient.getExecutions(workflowId);
      setExecutions(data);
      setError(null);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to fetch executions');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchExecutions();
  }, [workflowId]);

  return { executions, loading, error, refetch: fetchExecutions };
}

export function useWebSocket(url: string) {
  const [socket, setSocket] = useState<WebSocket | null>(null);
  const [connected, setConnected] = useState(false);
  const [lastMessage, setLastMessage] = useState<any>(null);

  useEffect(() => {
    const ws = new WebSocket(url);

    ws.onopen = () => {
      setConnected(true);
      console.log('WebSocket connected');
    };

    ws.onmessage = (event) => {
      try {
        const data = JSON.parse(event.data);
        setLastMessage(data);
      } catch (err) {
        console.error('Failed to parse WebSocket message:', err);
      }
    };

    ws.onerror = (error) => {
      console.error('WebSocket error:', error);
    };

    ws.onclose = () => {
      setConnected(false);
      console.log('WebSocket disconnected');
    };

    setSocket(ws);

    return () => {
      ws.close();
    };
  }, [url]);

  const sendMessage = (message: any) => {
    if (socket && connected) {
      socket.send(JSON.stringify(message));
    }
  };

  return { socket, connected, lastMessage, sendMessage };
}
