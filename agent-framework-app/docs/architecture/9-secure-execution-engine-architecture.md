# **9\. Secure Execution Engine Architecture**

* **Isolation:** The engine is built on Docker. The execution-engine/Dockerfile will define a minimal Python environment with only the agent-framework and its direct dependencies installed.  
* **Invocation:** The backend's Execution Service will use the Docker SDK for Python to programmatically start and manage containers. The user's code will be mounted into the container or passed via stdin.  
* **Communication:** The runner.py script inside the container will execute the user's workflow code. It will capture all WorkflowEvent objects produced by InProcessExecution.StreamAsync and serialize them to stdout as JSON lines.  
* **Security Policies:**  
  * **Network:** Docker network policies will be set to none by default. Any necessary external API calls must be explicitly declared and will be proxied through a secure gateway managed by the backend.  
  * **Filesystem:** The container's root filesystem will be read-only. A temporary, in-memory volume (tmpfs) will be mounted for any ephemeral file needs.  
  * **Resources:** Each container will be launched with strict CPU and memory limits (e.g., 1 CPU, 512MB RAM) and a timeout (e.g., 60 seconds) to prevent abuse.
