# **4\. Data Models**

These TypeScript interfaces will be defined in a shared package within the monorepo for use by both the frontend and the backend API.

// in packages/shared/src/types.ts

export interface User {  
  id: string;  
  email: string;  
  createdAt: Date;  
}

export interface Workflow {  
  id: string;  
  name: string;  
  code: string; // The Python script  
  ownerId: string;  
  createdAt: Date;  
  updatedAt: Date;  
}

export interface WorkflowExecution {  
  id: string;  
  workflowId: string;  
  status: 'running' | 'paused' | 'completed' | 'failed';  
  latestCheckpointId?: string;  
}
