# **3\. User Flows**

## **Flow 1: Create and Run a New Workflow**

* **User Goal:** To go from a natural language idea to an executed workflow.  
* **Entry Point:** Dashboard.  
* **Success Criteria:** The user sees the output of their generated workflow in the console.

sequenceDiagram  
    participant User  
    participant Frontend  
    participant Backend

    User-\>\>Frontend: Clicks "New Workflow" on Dashboard  
    Frontend-\>\>User: Navigates to new Workspace view  
    User-\>\>Frontend: Types prompt into generator input  
    User-\>\>Frontend: Clicks "Generate"  
    Frontend-\>\>Backend: POST /api/generate-workflow (with prompt)  
    Backend-\>\>Frontend: Returns { code, mermaidDefinition }  
    Frontend-\>\>User: Renders diagram and code in panes  
    User-\>\>Frontend: Clicks "Run"  
    Frontend-\>\>Backend: Establishes WebSocket, then POST /api/execute-workflow (with code)  
    Backend--\>\>Frontend: Streams WorkflowEvents over WebSocket  
    Frontend-\>\>User: Displays events in console, highlights nodes in visualizer

## **Flow 2: Edit a Workflow Visually**

* **User Goal:** To modify an existing workflow using the visual editor.  
* **Entry Point:** Workspace view with a loaded workflow.  
* **Success Criteria:** The Python code in the editor updates to reflect the visual changes.

sequenceDiagram  
    participant User  
    participant Frontend  
    participant Backend

    User-\>\>Frontend: Drags a new node from palette onto canvas  
    Frontend-\>\>Backend: POST /api/sync/visual-to-code (with graph structure)  
    Backend-\>\>Frontend: Returns { updatedCode }  
    Frontend-\>\>User: Updates code editor with new code
