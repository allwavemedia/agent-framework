# **Risks & Open Questions**

## **Key Risks**

* **Implementation Complexity (High):** The two-way synchronization between a visual editor and a code editor is notoriously difficult to implement correctly and can be prone to bugs.  
* **Performance Bottlenecks (Medium):** Real-time code parsing, visualization updates, and event streaming could lead to performance issues on the server or client side, especially with complex workflows.  
* **Security Vulnerabilities (High):** An escape from the Docker sandbox would represent a critical security breach. The sandbox implementation must be rigorously tested.

## **Open Questions**

* How will the debugging feature (e.g., breakpoints) be implemented? Will it require modifying the user's code at runtime or a more sophisticated execution wrapper?  
* What is the precise mechanism for mapping a visual change (e.g., "move a node") to a specific, syntactically correct change in the Python code?  
* Can the WorkflowViz output be made interactive, or will we need to build a custom rendering layer on top of its output?
