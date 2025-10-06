# **Constraints & Assumptions**

## **Constraints**

* **Framework Lock-in:** The entire system is fundamentally tied to the Microsoft Agent Framework (Python SDK). All generated code and execution logic must remain 100% compliant.  
* **Timeline:** The expanded MVP scope significantly increases complexity; an aggressive timeline may not be feasible.  
* **Resources:** The development team must have expertise in Python (FastAPI), React, Docker, and real-time web technologies.

## **Key Assumptions**

* **Framework Capabilities:** We assume the Agent Framework's APIs (WorkflowViz, CheckpointManager, AgentThread serialization, WorkflowEvent stream) are robust and performant enough to support a real-time, interactive user experience.  
* **Code Parsing Feasibility:** We assume that parsing Python code in the backend to regenerate a visual graph in real-time is technically feasible and can be performed with acceptable latency.  
* **Security Model:** We assume a Docker-based sandboxing model is sufficient to mitigate the risks of executing user-generated code.
