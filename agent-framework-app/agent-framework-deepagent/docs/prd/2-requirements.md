# **2\. Requirements**

## **Functional**

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

## **Non-Functional**

1. **NFR1: Performance:** UI updates for visual-to-code and code-to-visual synchronization (FR5, FR7) must complete in under 500ms for workflows with up to 10 nodes.  
2. **NFR2: Security:** The workflow execution sandbox must prevent any access to the host system's filesystem, network (except for whitelisted domains), or other users' data.  
3. **NFR3: Usability:** The visual editor shall be intuitive, allowing a first-time user to create a two-node workflow without requiring documentation.  
4. **NFR4: Reliability:** Workflow state persisted via checkpointing (FR13) must be durable and survive application restarts. The system should guarantee at-least-once execution semantics upon resumption.  
5. **NFR5: Compliance:** All generated code must be 100% compatible with the version of the agent-framework pip package specified in the technical stack.
