/**
 * API client for Agent Workflow Builder backend
 */

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

export class ApiClient {
  private baseUrl: string;

  constructor(baseUrl: string = API_BASE_URL) {
    this.baseUrl = baseUrl;
  }

  private async request<T>(
    endpoint: string,
    options: RequestInit = {}
  ): Promise<T> {
    const url = `${this.baseUrl}${endpoint}`;
    const response = await fetch(url, {
      ...options,
      headers: {
        'Content-Type': 'application/json',
        ...options.headers,
      },
    });

    if (!response.ok) {
      const error = await response.json().catch(() => ({ detail: 'Unknown error' }));
      throw new Error(error.detail || `API error: ${response.statusText}`);
    }

    return response.json();
  }

  // Agent endpoints
  async getAgents() {
    return this.request('/api/agents/');
  }

  async getAgent(id: number) {
    return this.request(`/api/agents/${id}`);
  }

  async createAgent(data: any) {
    return this.request('/api/agents/', {
      method: 'POST',
      body: JSON.stringify(data),
    });
  }

  async updateAgent(id: number, data: any) {
    return this.request(`/api/agents/${id}`, {
      method: 'PUT',
      body: JSON.stringify(data),
    });
  }

  async deleteAgent(id: number) {
    return this.request(`/api/agents/${id}`, {
      method: 'DELETE',
    });
  }

  // Workflow endpoints
  async getWorkflows() {
    return this.request('/api/workflows/');
  }

  async getWorkflow(id: number) {
    return this.request(`/api/workflows/${id}`);
  }

  async createWorkflow(data: any) {
    return this.request('/api/workflows/', {
      method: 'POST',
      body: JSON.stringify(data),
    });
  }

  async updateWorkflow(id: number, data: any) {
    return this.request(`/api/workflows/${id}`, {
      method: 'PUT',
      body: JSON.stringify(data),
    });
  }

  async deleteWorkflow(id: number) {
    return this.request(`/api/workflows/${id}`, {
      method: 'DELETE',
    });
  }

  async validateWorkflow(id: number) {
    return this.request(`/api/workflows/${id}/validate`, {
      method: 'POST',
    });
  }

  async visualizeWorkflow(id: number, format: string = 'mermaid') {
    return this.request(`/api/workflows/${id}/visualize?format=${format}`);
  }

  // Workflow Node endpoints
  async createNode(data: any) {
    return this.request('/api/workflows/nodes', {
      method: 'POST',
      body: JSON.stringify(data),
    });
  }

  async updateNode(id: number, data: any) {
    return this.request(`/api/workflows/nodes/${id}`, {
      method: 'PUT',
      body: JSON.stringify(data),
    });
  }

  async deleteNode(id: number) {
    return this.request(`/api/workflows/nodes/${id}`, {
      method: 'DELETE',
    });
  }

  // Workflow Edge endpoints
  async createEdge(data: any) {
    return this.request('/api/workflows/edges', {
      method: 'POST',
      body: JSON.stringify(data),
    });
  }

  async deleteEdge(id: number) {
    return this.request(`/api/workflows/edges/${id}`, {
      method: 'DELETE',
    });
  }

  // Execution endpoints
  async getExecutions(workflowId?: number) {
    const params = workflowId ? `?workflow_id=${workflowId}` : '';
    return this.request(`/api/executions/${params}`);
  }

  async getExecution(id: number) {
    return this.request(`/api/executions/${id}`);
  }

  async createExecution(data: any) {
    return this.request('/api/executions/', {
      method: 'POST',
      body: JSON.stringify(data),
    });
  }

  async cancelExecution(id: number) {
    return this.request(`/api/executions/${id}/cancel`, {
      method: 'POST',
    });
  }
}

export const apiClient = new ApiClient();
