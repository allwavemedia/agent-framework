# **5\. API Specification (OpenAPI 3.0)**

This defines the contract between the frontend and the FastAPI backend.

\# Simplified OpenAPI 3.0 Spec  
openapi: 3.0.0  
info:  
  title: AI Workflow Builder API  
  version: 1.0.0  
paths:  
  /api/generate-workflow:  
    post:  
      summary: Generates a workflow from a natural language prompt.  
      requestBody:  
        required: true  
        content:  
          application/json:  
            schema: { type: object, properties: { prompt: { type: string } } }  
      responses:  
        '200':  
          description: OK  
          content:  
            application/json:  
              schema: { type: object, properties: { code: { type: string }, mermaidDefinition: { type: string } } }  
    
  /api/sync/visual-to-code:  
    post:  
      summary: Updates Python code based on a visual graph structure.  
      \# ... request/response definitions  
        
  /api/sync/code-to-visual:  
    post:  
      summary: Generates a new visual diagram from Python code.  
      \# ... request/response definitions

  /api/execute-workflow:  
    post:  
      summary: Executes a workflow and initiates event streaming.  
      \# ... request/response definitions

  /api/workflows:  
    post:  
      summary: Saves a new workflow. (Authenticated)  
    get:  
      summary: Lists saved workflows. (Authenticated)
