# **AI Workflow Builder UI/UX Specification**

## **1\. Introduction**

This document defines the user experience goals, information architecture, user flows, and visual design specifications for the AI Workflow Builder's user interface. It serves as the foundation for visual design and frontend development, ensuring a cohesive and user-centered experience.

### **Overall UX Goals & Principles**

#### **Target User Personas**

* **Low-Code Developer/Non-Expert User:** This user understands the logic of a workflow but is not a professional programmer. They need a highly intuitive visual interface that abstracts away code complexity.  
* **Python Developer:** An experienced programmer who wants to accelerate their workflow. They value efficiency, keyboard shortcuts, and the ability to drop into code for complex logic, but will use the visual tools for speed and clarity.

#### **Usability Goals**

* **Ease of Learning:** A new user should be able to generate their first workflow from a natural language prompt within 2 minutes of using the application.  
* **Efficiency of Use:** An expert user should be able to create, test, and save a moderately complex (5-7 node) workflow faster than they could by writing the Python code from scratch.  
* **Error Prevention:** The UI must provide clear feedback and confirmations for destructive actions (e.g., deleting a node). The two-way sync should never result in a syntactically invalid state.  
* **Memorability:** An infrequent user should be able to return to the application after a week and immediately understand how to load and run their saved workflows.

#### **Design Principles**

1. **Clarity Over Cleverness:** The state of the workflow must always be clear. The visual diagram is the source of truth for the structure, and the code is the source of truth for the implementation. There should be no ambiguity.  
2. **Two-Way Sync is King:** The core of the experience is the seamless, real-time synchronization between the visual and code editors. This link must feel instantaneous and reliable.  
3. **Progressive Disclosure:** Keep the interface clean. Show core controls by default and reveal advanced options (like breakpoint states or detailed event logs) only when the user actively seeks them.  
4. **Immediate Feedback:** Every user action—be it dragging a node, typing code, or clicking "Run"—must provide an immediate and clear visual response.

### **Change Log**

| Date | Version | Description | Author |
| :---- | :---- | :---- | :---- |
| 2025-10-03 | 1.0 | Initial draft of the UI/UX Spec | Sally |

## **2\. Information Architecture (IA)**

### **Site Map / Screen Inventory**

The application has a simple, focused information architecture centered around the two main user contexts: managing workflows and working on a single workflow.

graph TD  
    A\[User visits site\] \--\> B{Logged In?};  
    B \--\>|No| C\[Login / Signup Page\];  
    B \--\>|Yes| D\[Dashboard (Workflow List)\];  
    C \--\> D;  
    D \--\> E\[Workspace (Editor)\];  
    E \--\> D;

### **Navigation Structure**

* **Primary Navigation:** A persistent top header will contain the application logo, a link back to the Dashboard, user profile/authentication controls (e.g., "Logged in as user@email.com", "Logout"), and the name of the current workflow being edited.  
* **Workspace Controls:** Within the Workspace view, primary actions like "Generate", "Run", "Debug", "Save", and "Share" will be located in a prominent, easily accessible control bar above the main split-screen panes.

## **3\. User Flows**

### **Flow 1: Create and Run a New Workflow**

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

### **Flow 2: Edit a Workflow Visually**

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

## **4\. Wireframes & Mockups**

The core interface is the split-screen workspace.

* **Left Pane (Workflow Visualizer):** A canvas where the Mermaid/Graphviz diagram is rendered. It will have zoom/pan controls. A palette of available Executor types will be visible for users to drag onto the canvas.  
* **Right Pane (Code Editor):** An instance of the Monaco editor themed for the application. It will have line numbers and Python syntax highlighting.  
* **Top Control Bar:** Contains primary action buttons: "Generate", "Run", "Debug", and "Save".  
* **Bottom Console Panel:** A collapsible panel with tabs for "Logs", "Events", and "State Inspector".

## **5\. Component Library / Design System**

The frontend will be built using a pre-existing component library to ensure consistency and speed up development.

* **Design System Approach:** Utilize a library like **Shadcn/UI** (or an equivalent modern, accessible component library) built on top of Tailwind CSS. This provides a set of unstyled, accessible components that we can theme to match our brand.  
* **Core Components:**  
  * **Button:** For all primary actions.  
  * **Input:** For the natural language prompt.  
  * **Tabs:** For the console panel.  
  * **Dialog/Modal:** For confirmations (e.g., "Save workflow?").  
  * **Dropdown Menu:** For user profile/logout actions.  
  * **Resizable Pane Layout:** To implement the core split-screen.  
  * **Custom Node Components:** For the visualizer, representing different Executor types.

## **6\. Branding & Style Guide**

* **Visual Identity:** The style should be minimalist, professional, and tech-focused. A dark mode will be the default to reduce eye strain for developers.  
* **Color Palette:**  
  * **Primary:** A bright, energetic color for primary actions (e.g., a vibrant blue or purple).  
  * **Background:** A very dark grey/charcoal.  
  * **Text:** Off-white.  
  * **Accents:** Specific colors for diagram nodes based on status: Green (Success), Yellow (Running), Red (Failed).  
* **Typography:** A clean, legible sans-serif font (like Inter) for UI elements and a monospaced font (like Fira Code or JetBrains Mono) for the code editor.

## **7\. Accessibility & Responsiveness**

* **Compliance Target:** The application will aim for **WCAG 2.1 AA** compliance. All components from the chosen library must be fully accessible via keyboard and screen readers.  
* **Responsiveness:** The primary target is desktop. The application will be usable on tablets, where the split-pane layout will adjust. On mobile, the interface will likely switch to a tabbed view (showing either the visualizer or the code, not both at once) for viewing purposes, as editing would be impractical.