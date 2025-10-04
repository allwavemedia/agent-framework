# **4\. Technical Assumptions**

## **Repository Structure: Monorepo**

The project will be structured as a monorepo (e.g., using npm workspaces or similar) containing separate packages for the frontend (React SPA) and backend (FastAPI server). This simplifies dependency management and type sharing.

## **Service Architecture**

The backend will be a monolith to start, built with FastAPI. A separate, decoupled service (the Secure Execution Engine) will handle the running of user code. Communication between the backend and this engine will be asynchronous.

## **Testing Requirements**

The project will follow a full testing pyramid approach:

* **Unit Tests:** For individual components, services, and utilities on both frontend and backend.  
* **Integration Tests:** To verify interactions between the backend API and the database, and between the frontend and API services.  
* **End-to-End (E2E) Tests:** To validate critical user flows, such as generating a workflow, editing it visually, running it, and seeing the results.
