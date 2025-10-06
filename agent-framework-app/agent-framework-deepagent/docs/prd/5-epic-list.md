# **5\. Epic List**

The MVP will be developed across four logically sequential epics. Each epic delivers a significant, deployable increment of functionality.

* **Epic 1: Foundation & Core Generation Engine:** Establish the project foundation, provision external LLM services, implement the core natural language to-code/visuals pipeline, validate APIs via integration tests before UI consumption, and enable secure, one-off workflow execution.  
	* Story Ordering (dependency driven): 1.1 Scaffolding → 1.1.5 External Service Configuration → 1.2 Generation API → 1.3 Visualization API → 1.3.5 API Integration Testing → 1.4 Core UI Layout → 1.5 Secure Execution Engine → 1.6 Event Streaming.
* **Epic 2: User & Workflow Persistence:** Introduce user authentication and the ability to save, list, and load created workflows.  
* **Epic 3: Full Two-Way Interactivity:** Implement the complex real-time synchronization features, enabling users to edit both the visual diagram and the code interactively.  
* **Epic 4: Advanced Execution & Stateful Debugging:** Build the advanced debugging tools, including breakpoints and state inspection, and implement the stateful execution capabilities for checkpointing and resuming workflows.
