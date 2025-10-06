# **9\. Epic 4: Advanced Execution & Stateful Debugging**

**Goal:** To implement persistence for running workflows and provide interactive debugging capabilities.

## **Story 4.1: Implement Workflow Checkpointing**

As a developer, I want the system to automatically save the state of a running workflow, so that it can be resumed later. (FR13)  
Acceptance Criteria:

1. The Secure Execution Engine is configured with a persistent CheckpointManager (e.g., pointing to a shared volume or database).  
2. When a workflow runs, its state is automatically saved at the end of each superstep.  
3. The backend stores a reference to the latest checkpoint ID associated with that execution.  
4. The system reliably persists state, surviving application restarts (NFR4).

## **Story 4.2: Implement Workflow Resumption**

As a user, I want to resume a paused or failed workflow from its last known state. (FR14)  
Acceptance Criteria:

1. A "Resume" button is available for workflows that have a saved checkpoint.  
2. Clicking "Resume" triggers an API call to the backend with the checkpoint ID.  
3. The backend instructs the Secure Execution Engine to resume the workflow from the specified checkpoint.  
4. Event streaming continues from the point of resumption.

## **Story 4.3: Implement Breakpoints & State Inspection**

As a user, I want to set breakpoints in my visual workflow and inspect the state when it pauses, so I can debug it. (FR10)  
Acceptance Criteria:

1. Users can click on an Executor in the visualizer to toggle a breakpoint.  
2. When running in "debug" mode, the execution engine pauses when it reaches a marked Executor.  
3. When paused, the backend receives the current state of the workflow (e.g., executor state, pending messages) from the execution engine.  
4. This state is displayed to the user in a new "State" tab in the console panel.  
5. A "Continue" button is available to resume execution until the next breakpoint or completion.
