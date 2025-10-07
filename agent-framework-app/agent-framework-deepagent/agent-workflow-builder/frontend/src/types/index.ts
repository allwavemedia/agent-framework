/**
 * TypeScript types for Agent Workflow Builder
 */

export interface Agent {
  id: number;
  name: string;
  description?: string;
  agent_type: 'CHAT_AGENT' | 'SPECIALIST_AGENT' | 'TOOL_AGENT' | 'CUSTOM_AGENT';
  instructions: string;
  model_config: Record<string, any>;
  tools: string[];
  is_active: boolean;
  created_at: string;
  updated_at?: string;
}

export interface Workflow {
  id: number;
  name: string;
  description?: string;
  version: string;
  tags: string[];
  is_template: boolean;
  is_public: boolean;
  status?: string;
  created_at: string;
  updated_at?: string;
  nodes: WorkflowNode[];
  edges: WorkflowEdge[];
}

export interface WorkflowNode {
  id: number;
  workflow_id: number;
  name: string;
  node_type: string;
  executor_type: 'AGENT' | 'FUNCTION' | 'CONDITION' | 'HUMAN_INPUT' | 'CUSTOM';
  agent_id?: number;
  config: Record<string, any>;
  position_x: number;
  position_y: number;
  is_output_node: boolean;
}

export interface WorkflowEdge {
  id: number;
  workflow_id: number;
  source_node_id: number;
  target_node_id: number;
  condition?: string;
}

export interface WorkflowExecution {
  id: number;
  workflow_id: number;
  status: 'DRAFT' | 'RUNNING' | 'COMPLETED' | 'FAILED' | 'PAUSED' | 'CANCELLED';
  input_data: Record<string, any>;
  output_data?: Record<string, any>;
  error_message?: string;
  started_at?: string;
  completed_at?: string;
  created_at: string;
}

export interface ValidationResult {
  valid: boolean;
  errors: string[];
  warnings: string[];
}

export interface VisualizationResult {
  format: string;
  visualization: string;
}

export interface WebSocketMessage {
  type: string;
  data: any;
}

export interface ExecutionEvent {
  event_type: string;
  node_id?: number;
  message?: string;
  timestamp: string;
  data?: any;
}

export interface Checkpoint {
  checkpoint_id: string;
  created_at: string;
  metadata: Record<string, any>;
}

export interface CheckpointStatusResponse {
  status: string;
  message?: string;
  workflow_id?: string;
  checkpoint_id?: string;
}

export interface ApprovalRequest {
  id: number;
  workflow_id: string;
  request_type: string;
  request_data: Record<string, any>;
  status: 'PENDING' | 'APPROVED' | 'REJECTED' | 'TIMEOUT';
  created_at: string;
  updated_at?: string;
}

export interface ApprovalResponse {
  approved: boolean;
  feedback?: string;
  modified_data?: Record<string, any>;
}
