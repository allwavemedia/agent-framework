# **Project Brief: AI Workflow Builder**

Session Date: 2025-10-03  
Facilitator: Mary (Business Analyst)

## **Executive Summary**

This project will create a web application that enables users to build, manage, and execute AI agents and multi-step workflows using natural language. The platform translates user intent into executable Python code compliant with the Microsoft Agent Framework, featuring a dual-pane UI with a visual workflow diagram and a corresponding code editor. The primary goal is to democratize AI agent creation for both technical and non-technical users by abstracting the complexity of the underlying framework.

## **Problem Statement**

Developing AI agents and workflows requires significant programming expertise and a deep understanding of specific frameworks like the Microsoft Agent Framework. This creates a high barrier to entry, limiting the ability of domain experts, business analysts, and low-code developers to leverage powerful AI orchestration capabilities. Existing solutions often lack a user-friendly interface that bridges the gap between high-level conceptual design and low-level code implementation, forcing users into either overly simplistic, restrictive tools or complex, code-heavy environments. There is a need for a platform that visually represents AI workflows while providing direct access to the underlying, compliant code.

## **Proposed Solution**

We propose a "Split Screen" web application that translates natural language descriptions into functional AI agents and workflows. The left pane will display an interactive, visual representation of the workflow graph (Executors and Edges), while the right pane shows the auto-generated, framework-compliant Python code. Users can edit either the visual diagram or the code, with changes reflected in the other pane. The application will provide a secure, sandboxed environment to test and run these workflows, with real-time feedback and debugging information surfaced directly in the UI. This solution directly addresses the problem by providing a user-friendly abstraction that does not sacrifice the power or compliance of the underlying Microsoft Agent Framework.

## **Target Users**

### **Primary User Segment: The Low-Code Developer / Power User**

* **Profile:** Business analysts, data scientists, product managers, and hobbyist developers who are technically proficient and understand logic, but are not expert Python programmers.  
* **Behaviors:** They are comfortable with visual builders, node-based editors (like Zapier or Make), and using natural language to express intent. They want to build powerful AI automations without writing boilerplate code or managing complex development environments.  
* **Needs & Pain Points:** They are frustrated by the limitations of purely no-code platforms but intimidated by the steep learning curve of coding-intensive AI frameworks. They need a tool that lets them design complex logic visually and then "drop down" into code only when necessary.

### **Secondary User Segment: The Python Developer**

* **Profile:** Experienced software developers who are familiar with Python and are either new to the Microsoft Agent Framework or want to accelerate their development process.  
* **Behaviors:** They are comfortable writing code and using IDEs. They value tools that reduce boilerplate, enforce best practices, and provide a clear starting point. They will primarily use the code editor but appreciate the visualizer for understanding, debugging, and communicating workflow structures to less technical colleagues.  
* **Needs & Pain Points:** Their main challenge is the time it takes to learn and correctly implement the specific constructs of the Agent Framework (Workflows, Executors, Edges). They need a tool that can quickly scaffold framework-compliant code from a high-level description, allowing them to focus on refining the core logic rather than setting up the structure.

## **Goals & Success Metrics**

### **Business Objectives**

* **Reduce Development Time:** Decrease the time required to build and deploy a functional AI workflow by 50% for Python Developers compared to writing framework code from scratch.  
* **Increase Accessibility:** Enable 1,000 Low-Code Developers to successfully create and run a multi-step workflow within the first six months post-launch.  
* **Establish Framework Adherence:** Achieve 100% compliance with Microsoft Agent Framework constructs in all generated code, ensuring portability and correctness.

### **User Success Metrics**

* **Ease of Use (Low-Code User):** 80% of new low-code users can successfully generate and execute a simple two-agent workflow from a natural language prompt within 10 minutes of their first session.  
* **Efficiency (Python Developer):** Python developers report a 70% or higher satisfaction rate with the code scaffolding feature, citing significant time savings.  
* **Confidence:** A user survey indicates that 75% of users feel confident understanding and debugging their workflows using the split-screen UI and event logs.

### **Key Performance Indicators (KPIs)**

* **Workflow Generation Success Rate:** 95% of natural language prompts result in valid, executable Python code.  
* **Active Users:** Achieve 500 weekly active users within the first quarter.  
* **User Retention:** Achieve a 30% week-4 retention rate for new users.  
* **Session-to-Execution Ratio:** 60% of user sessions result in at least one workflow execution.

## **MVP Scope**

### **Core Features (Must Have)**

* **Natural Language to Workflow:** A core processing engine that accepts a user's text prompt and generates a valid, executable Python script using WorkflowBuilder, Executors, and Edges.  
* **Split-Screen UI:** A display showing the generated Python code (right pane) and a visual diagram (left pane).  
* **Secure Execution:** A sandboxed environment (e.g., Docker) to run the generated workflow and capture its output.  
* **Output & Event Display:** A console view to display the final output and key WorkflowEvent data (e.g., ExecutorCompletedEvent).  
* **User Authentication:** Basic user sign-up and login to associate workflows with users.  
* **Workflow Persistence:** Ability to save a generated workflow (the Python code) and list previously saved workflows.  
* **Interactive Visual Editing:** Drag-and-drop or direct manipulation of the workflow diagram.  
* **Code-to-Visual Sync:** Real-time updates to the diagram based on code editor changes.  
* **Advanced Debugging Tools:** Breakpoints, step-through execution, or state inspection.  
* **AgentThread Persistence:** Saving and resuming the state of running conversations or workflows (checkpointing).

### **Out of Scope for MVP**

* **Collaboration Features:** Sharing workflows, multi-user editing.  
* **Version Control:** History and versioning for saved workflows.

### **MVP Success Criteria**

The MVP will be considered a success when a new user can sign up, describe a two-step sequential workflow in natural language, generate an interactive code/visual representation, execute it successfully with debugging, save it, and view the output, all within the application.

## **Post-MVP Vision**

### **Long-term Vision**

* **Workflow Marketplace:** A community-driven platform where users can share and discover pre-built agent and workflow templates.  
* **AI-Powered Refinement:** An agent that analyzes a user's workflow and suggests improvements for efficiency, error handling, or cost-effectiveness.  
* **Enterprise Integration:** Connectors for enterprise systems (e.g., Salesforce, SharePoint) and support for private, on-premise execution environments.

## **Technical Considerations**

* **Platform Requirements:** The application must be a web-based SPA accessible via modern browsers (Chrome, Firefox, Safari, Edge). The backend must be horizontally scalable to handle numerous concurrent workflow executions.  
* **Technology Preferences:**  
  * **Frontend:** React (with TypeScript) for a robust, component-based architecture.  
  * **Backend:** Python with FastAPI for high-performance, async API endpoints.  
  * **Database:** PostgreSQL for reliable, structured data storage.  
  * **Execution Sandbox:** Docker for secure, isolated code execution.  
* **Architecture Considerations:** A real-time communication channel (WebSockets) is mandatory between the frontend and backend to support interactive editing, code synchronization, and live debugging event streams. The architecture must separate the core web application from the workflow execution engine.

## **Constraints & Assumptions**

### **Constraints**

* **Framework Lock-in:** The entire system is fundamentally tied to the Microsoft Agent Framework (Python SDK). All generated code and execution logic must remain 100% compliant.  
* **Timeline:** The expanded MVP scope significantly increases complexity; an aggressive timeline may not be feasible.  
* **Resources:** The development team must have expertise in Python (FastAPI), React, Docker, and real-time web technologies.

### **Key Assumptions**

* **Framework Capabilities:** We assume the Agent Framework's APIs (WorkflowViz, CheckpointManager, AgentThread serialization, WorkflowEvent stream) are robust and performant enough to support a real-time, interactive user experience.  
* **Code Parsing Feasibility:** We assume that parsing Python code in the backend to regenerate a visual graph in real-time is technically feasible and can be performed with acceptable latency.  
* **Security Model:** We assume a Docker-based sandboxing model is sufficient to mitigate the risks of executing user-generated code.

## **Risks & Open Questions**

### **Key Risks**

* **Implementation Complexity (High):** The two-way synchronization between a visual editor and a code editor is notoriously difficult to implement correctly and can be prone to bugs.  
* **Performance Bottlenecks (Medium):** Real-time code parsing, visualization updates, and event streaming could lead to performance issues on the server or client side, especially with complex workflows.  
* **Security Vulnerabilities (High):** An escape from the Docker sandbox would represent a critical security breach. The sandbox implementation must be rigorously tested.

### **Open Questions**

* How will the debugging feature (e.g., breakpoints) be implemented? Will it require modifying the user's code at runtime or a more sophisticated execution wrapper?  
* What is the precise mechanism for mapping a visual change (e.g., "move a node") to a specific, syntactically correct change in the Python code?  
* Can the WorkflowViz output be made interactive, or will we need to build a custom rendering layer on top of its output?

## **Next Steps**

### **Immediate Actions**

1. Finalize and approve this Project Brief.  
2. Handoff to the Product Manager to begin creating the detailed Product Requirements Document (PRD).  
3. Initiate a technical spike/prototype to validate the feasibility of the real-time code-to-visual synchronization.

### **PM Handoff**

This Project Brief provides the full context for the AI Workflow Builder. Please start by reviewing the brief thoroughly, paying close attention to the expanded MVP scope. Your next step is to create the PRD, breaking down these features into detailed functional requirements, epics, and user stories.