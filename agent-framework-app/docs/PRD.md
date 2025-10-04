# **AI Workflow Builder Product Requirements Document (PRD)**

## **1\. Goals and Background Context**

### **Goals**

* **Reduce Development Time:** Decrease the time required to build and deploy a functional AI workflow by 50% for Python Developers.  
* **Increase Accessibility:** Enable non-expert users to successfully create and run multi-step AI workflows.  
* **Establish Framework Adherence:** Ensure 100% compliance with Microsoft Agent Framework constructs in all generated code.  
* **Provide Interactive Tooling:** Deliver a seamless, two-way interactive experience between visual workflow design and code generation.  
* **Enable Robust Debugging:** Offer tools for breakpoints, state inspection, and real-time event monitoring.  
* **Support Stateful Execution:** Implement persistence for long-running, pausable, and resumable workflows.

### **Background Context**

This project addresses the high barrier to entry for developing AI agents and workflows, which typically requires deep programming expertise. By creating a web application that translates natural language into framework-compliant Python code, we bridge the gap between high-level conceptual design and low-level implementation. The platform's core "Split Screen" model, featuring an interactive visualizer and a synchronized code editor, aims to democratize AI agent creation for a broader audience while accelerating development for experienced programmers. This PRD outlines the requirements for an ambitious MVP that includes not just code generation but also full interactivity, debugging, and stateful execution from day one.

### **Change Log**

| Date | Version | Description | Author |  
| 2025-10-03 | 1.0 | Initial draft of the PRD | John |

## **2\. Requirements**

### **Functional**

1. **FR1: Natural Language to Workflow Generation:** The system shall accept a natural language text prompt from the user and generate a complete, syntactically correct Python script that defines a workflow using the Microsoft Agent Framework's WorkflowBuilder.  
2. **FR2: Visual Workflow Display:** The system shall render a visual graph diagram of the generated workflow in the left pane of the UI. This visualization must be generated using the framework's WorkflowViz capability.  
3. **FR3: Code Display:** The system shall display the complete generated Python script in a code editor in the right pane of the UI.  
4. **FR4: Visual Editing:** Users shall be able to modify the workflow by interacting with the visual diagram. Supported actions include adding new nodes (Executors), deleting nodes, and creating/deleting connections (Edges).  
5. **FR5: Visual-to-Code Synchronization:** Any modification made to the visual diagram (per FR4) must be immediately reflected as a syntactically correct change in the Python code in the editor pane.  
6. **FR6: Code Editing:** Users shall be able to directly edit the Python code in the code editor.  
7. **FR7: Code-to-Visual Synchronization:** Any valid structural modification made to the Python code (e.g., adding an Executor or an .add\_edge() call) must be immediately reflected in the visual diagram.  
8. **FR8: Secure Workflow Execution:** The system shall provide a mechanism to execute the generated Python script in a secure, isolated sandboxed environment.  
9. **FR9: Real-time Event Streaming:** During execution, the system must capture WorkflowEvent data (e.g., ExecutorCompletedEvent, WorkflowOutputEvent) and stream it to the frontend for display in a console.  
10. **FR10: State Inspection (Debugging):** The system shall allow a user to pause a workflow at a breakpoint and inspect the current state of an Executor and any pending messages.  
11. **FR11: Workflow Persistence:** Authenticated users shall be able to save their named workflows (the Python script and its visual representation) to their account.  
12. **FR12: Workflow Loading:** Authenticated users shall be able to browse and load their previously saved workflows into the editor.  
13. **FR13: Stateful Execution (Checkpointing):** The system must utilize the framework's CheckpointManager to automatically save the state of a running workflow at the end of each superstep.  
14. **FR14: Workflow Resumption:** Users shall be able to resume a previously executed workflow from a saved checkpoint.

### **Non-Functional**

1. **NFR1: Performance:** UI updates for visual-to-code and code-to-visual synchronization (FR5, FR7) must complete in under 500ms for workflows with up to 10 nodes.  
2. **NFR2: Security:** The workflow execution sandbox must prevent any access to the host system's filesystem, network (except for whitelisted domains), or other users' data.  
3. **NFR3: Usability:** The visual editor shall be intuitive, allowing a first-time user to create a two-node workflow without requiring documentation.  
4. **NFR4: Reliability:** Workflow state persisted via checkpointing (FR13) must be durable and survive application restarts. The system should guarantee at-least-once execution semantics upon resumption.  
5. **NFR5: Compliance:** All generated code must be 100% compatible with the version of the agent-framework pip package specified in the technical stack.

## **3\. User Interface Design Goals**

### **Overall UX Vision**

The user experience will be centered around the "Split Screen" model, providing a seamless, interactive, and educational environment. The design should feel powerful yet intuitive, empowering low-code users while accelerating the workflow for experienced developers. The primary goal is to make the complex process of AI orchestration feel tangible and manageable.

### **Key Interaction Paradigms**

* **Two-Way Sync:** The core interaction is the real-time, bidirectional synchronization between the visualizer and the code editor. Changes in one are instantly reflected in the other.  
* **Direct Manipulation:** Users should feel like they are directly manipulating the workflow, whether by dragging nodes on a canvas or typing code.  
* **Progressive Disclosure:** The UI should be clean and uncluttered by default, with advanced options and details (like Executor state or event logs) available on demand.

### **Core Screens and Views**

* **Main Workspace View:** The primary split-screen interface. This includes the visualizer pane, the code editor pane, a top-level control bar (Generate, Run, Debug, Save), and a collapsible bottom console panel.  
* **Dashboard / Workflow List:** A simple view where authenticated users can see and manage their saved workflows.

### **Branding**

The branding should be modern, clean, and professional, evoking a sense of intelligence and efficiency. Use a simple color palette with clear primary actions. The visualizer should use distinct colors and shapes to represent different types of Executors or states (e.g., running, success, failed).

### **Target Device and Platforms: Web Responsive**

The primary target is a desktop web browser experience, as the complexity of the interface is not well-suited for small mobile screens. The application should, however, be responsive enough to function on tablets.

## **4\. Technical Assumptions**

### **Repository Structure: Monorepo**

The project will be structured as a monorepo (e.g., using npm workspaces or similar) containing separate packages for the frontend (React SPA) and backend (FastAPI server). This simplifies dependency management and type sharing.

### **Service Architecture**

The backend will be a monolith to start, built with FastAPI. A separate, decoupled service (the Secure Execution Engine) will handle the running of user code. Communication between the backend and this engine will be asynchronous.

### **Testing Requirements**

The project will follow a full testing pyramid approach:

* **Unit Tests:** For individual components, services, and utilities on both frontend and backend.  
* **Integration Tests:** To verify interactions between the backend API and the database, and between the frontend and API services.  
* **End-to-End (E2E) Tests:** To validate critical user flows, such as generating a workflow, editing it visually, running it, and seeing the results.

## **5\. Epic List**

The MVP will be developed across four logically sequential epics. Each epic delivers a significant, deployable increment of functionality.

* **Epic 1: Foundation & Core Generation Engine:** Establish the project foundation, implement the core natural language to-code/visuals pipeline, and enable secure, one-off workflow execution.  
* **Epic 2: User & Workflow Persistence:** Introduce user authentication and the ability to save, list, and load created workflows.  
* **Epic 3: Full Two-Way Interactivity:** Implement the complex real-time synchronization features, enabling users to edit both the visual diagram and the code interactively.  
* **Epic 4: Advanced Execution & Stateful Debugging:** Build the advanced debugging tools, including breakpoints and state inspection, and implement the stateful execution capabilities for checkpointing and resuming workflows.

## **6\. Epic 1: Foundation & Core Generation Engine**

**Goal:** To deliver the core value proposition: converting a natural language prompt into executable, framework-compliant Python code and a corresponding visual diagram, and running it securely.

### **Story 1.1: Project Scaffolding & Setup**

As a developer, I want a complete monorepo structure with frontend and backend applications set up, so that I can begin development efficiently.  
Acceptance Criteria:

1. A monorepo is initialized.  
2. A basic "Hello World" React application is created in the apps/frontend directory.  
3. A basic "Hello World" FastAPI application is created in the apps/backend directory.  
4. Both applications can be started with a single npm run dev command from the root.

### **Story 1.2: Implement NLP to Python Generation API**

As a user, I want to submit a text prompt to the application, so that it generates a Python script for an AI workflow. (FR1)  
Acceptance Criteria:

1. An API endpoint POST /api/generate-workflow is created.  
2. It accepts a JSON payload with a prompt field.  
3. It uses a meta-agent (ChatClientAgent with structured output) to process the prompt.  
4. It returns a JSON response containing the generated Python code as a string.

### **Story 1.3: Implement Workflow Visualization API**

As a developer, I want an API that converts a workflow's Python code into a visual diagram definition, so that it can be rendered on the frontend. (FR2)  
Acceptance Criteria:

1. An API endpoint POST /api/visualize-workflow is created.  
2. It accepts Python code as input.  
3. It uses the WorkflowViz class to generate a Mermaid diagram definition string.  
4. It returns the Mermaid string in a JSON response.

### **Story 1.4: Build Core UI Layout**

As a user, I want to see a split-screen layout with a placeholder for the visual diagram and a code editor, so that I can interact with the core features. (FR2, FR3)  
Acceptance Criteria:

1. The main UI displays a left pane for the visualizer and a right pane with an embedded Monaco code editor.  
2. A text input field and a "Generate" button are present.  
3. Pressing "Generate" calls the /api/generate-workflow endpoint and displays the returned code in the editor.  
4. The generated code is then sent to the /api/visualize-workflow endpoint, and the returned Mermaid definition is rendered in the left pane.

### **Story 1.5: Implement Secure Execution Engine**

As a developer, I want a secure sandbox to execute user-provided Python code, so that workflows can be run without risk to the system. (FR8)  
Acceptance Criteria:

1. A Docker image is created with Python and agent-framework installed.  
2. An internal API is created on the backend that accepts Python code.  
3. The API spins up a new, isolated Docker container to run the code.  
4. The container has networking disabled and strict CPU/memory limits.  
5. Standard output and errors from the script are captured and returned.

### **Story 1.6: Implement Real-time Event Streaming**

As a user, I want to see real-time events from my workflow execution in a console, so that I can understand its progress. (FR9)  
Acceptance Criteria:

1. A WebSocket connection is established between the frontend and backend when a workflow is executed.  
2. The Secure Execution Engine streams WorkflowEvent data back to the backend.  
3. The backend forwards these events over the WebSocket to the frontend.  
4. A collapsible console in the UI displays a formatted log of incoming events.

## **7\. Epic 2: User & Workflow Persistence**

**Goal:** To enable users to create accounts, save their work, and reload it in a future session.

### **Story 2.1: Set up User Authentication**

As a user, I want to sign up and log in, so that I can save my work.  
Acceptance Criteria:

1. A user database table is created.  
2. API endpoints for user registration and login (e.g., using JWTs) are implemented.  
3. The frontend provides simple sign-up and login forms.  
4. Authenticated routes are protected.

### **Story 2.2: Implement Save Workflow API**

As a logged-in user, I want to save my current workflow, so that I can access it later. (FR11)  
Acceptance Criteria:

1. A workflows database table is created, linked to the user table.  
2. An authenticated API endpoint POST /api/workflows is created.  
3. It accepts a name and the code (Python script) for the workflow.  
4. The workflow is saved to the database.

### **Story 2.3: Implement List & Load Workflows**

As a logged-in user, I want to see a list of my saved workflows and load one into the editor. (FR12)  
Acceptance Criteria:

1. An authenticated API endpoint GET /api/workflows returns a list of the user's saved workflows.  
2. A dashboard page is created to display this list.  
3. Clicking a workflow in the list loads its code into the main editor and triggers a re-visualization.

## **8\. Epic 3: Full Two-Way Interactivity**

**Goal:** To implement the bidirectional synchronization between the visual editor and the code editor.

### **Story 3.1: Implement Visual Node/Edge Manipulation**

As a user, I want to add, delete, and connect nodes in the visual diagram, so that I can edit my workflow visually. (FR4)  
Acceptance Criteria:

1. The frontend diagram renderer (e.g., using React Flow on top of Mermaid) supports adding new nodes from a palette.  
2. Users can delete nodes and edges.  
3. Users can draw new edges between nodes.

### **Story 3.2: Implement Visual-to-Code Synchronization**

As a user, when I modify the diagram, I want the Python code to update automatically. (FR5)  
Acceptance Criteria:

1. Any visual change (add/delete node/edge) triggers an event.  
2. This event sends a structured representation of the change to a new backend endpoint (e.g., POST /api/sync/visual-to-code).  
3. The backend modifies its abstract representation of the workflow graph and regenerates the complete Python code.  
4. The updated code is sent back to the frontend and displayed in the editor.  
5. The entire round-trip completes in under 500ms (NFR1).

### **Story 3.3: Implement Code-to-Visual Synchronization**

As a user, when I edit the Python code, I want the visual diagram to update automatically. (FR7)  
Acceptance Criteria:

1. A debounce mechanism detects when the user stops typing in the code editor.  
2. The full content of the code editor is sent to a backend endpoint (e.g., POST /api/sync/code-to-visual).  
3. The backend parses the Python code to build an abstract representation of the workflow graph.  
4. It then uses WorkflowViz to generate a new Mermaid definition.  
5. The new definition is sent to the frontend and the visualizer is re-rendered.

## **9\. Epic 4: Advanced Execution & Stateful Debugging**

**Goal:** To implement persistence for running workflows and provide interactive debugging capabilities.

### **Story 4.1: Implement Workflow Checkpointing**

As a developer, I want the system to automatically save the state of a running workflow, so that it can be resumed later. (FR13)  
Acceptance Criteria:

1. The Secure Execution Engine is configured with a persistent CheckpointManager (e.g., pointing to a shared volume or database).  
2. When a workflow runs, its state is automatically saved at the end of each superstep.  
3. The backend stores a reference to the latest checkpoint ID associated with that execution.  
4. The system reliably persists state, surviving application restarts (NFR4).

### **Story 4.2: Implement Workflow Resumption**

As a user, I want to resume a paused or failed workflow from its last known state. (FR14)  
Acceptance Criteria:

1. A "Resume" button is available for workflows that have a saved checkpoint.  
2. Clicking "Resume" triggers an API call to the backend with the checkpoint ID.  
3. The backend instructs the Secure Execution Engine to resume the workflow from the specified checkpoint.  
4. Event streaming continues from the point of resumption.

### **Story 4.3: Implement Breakpoints & State Inspection**

As a user, I want to set breakpoints in my visual workflow and inspect the state when it pauses, so I can debug it. (FR10)  
Acceptance Criteria:

1. Users can click on an Executor in the visualizer to toggle a breakpoint.  
2. When running in "debug" mode, the execution engine pauses when it reaches a marked Executor.  
3. When paused, the backend receives the current state of the workflow (e.g., executor state, pending messages) from the execution engine.  
4. This state is displayed to the user in a new "State" tab in the console panel.  
5. A "Continue" button is available to resume execution until the next breakpoint or completion.

## **10\. Next Steps**

### **UX Expert Prompt**

"The PRD for the AI Workflow Builder is complete. Please review the User Interface Design Goals section and create a detailed UI/UX Specification document (front-end-spec.md). Focus on wireframes for the core workspace, the user flow for generating and editing a workflow, and the design of the interactive debugging console."

### **Architect Prompt**

"The PRD for the AI Workflow Builder is complete. Please review it, especially the Technical Assumptions, Requirements, and Epics, and create the comprehensive fullstack-architecture.md document. Your design must provide detailed plans for the frontend, backend, the real-time synchronization mechanism, and the secure execution engine, ensuring all decisions align with the specified Microsoft Agent Framework capabilities."