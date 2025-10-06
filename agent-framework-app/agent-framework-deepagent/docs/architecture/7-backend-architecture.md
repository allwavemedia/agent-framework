# **7\. Backend Architecture**

* **API Layer:** FastAPI routers will define the API endpoints. They will handle request validation (using Pydantic) and delegate to the orchestration layer.  
* **Orchestration Layer:** This is the core of the backend. It will house the "meta-agent" responsible for FR1. This service will take user prompts, interact with an LLM via ChatClientAgent to get a structured plan, and then generate the Python code and WorkflowViz output.  
* **Execution Service:** This service will manage the lifecycle of the secure execution engine. It will receive code, spin up a Docker container, pass the code to it, and establish a communication channel (e.g., Redis pub/sub or a direct WebSocket proxy) to stream WorkflowEvent data back.  
* **Database Access:** A repository pattern will be used to abstract database operations, managed by a library like SQLModel or SQLAlchemy.
