# **MVP Scope**

## **Core Features (Must Have)**

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

## **Out of Scope for MVP**

* **Collaboration Features:** Sharing workflows, multi-user editing.  
* **Version Control:** History and versioning for saved workflows.

## **MVP Success Criteria**

The MVP will be considered a success when a new user can sign up, describe a two-step sequential workflow in natural language, generate an interactive code/visual representation, execute it successfully with debugging, save it, and view the output, all within the application.
