# **2\. High-Level Architecture**

The system uses a decoupled three-tier architecture: a React frontend, a FastAPI backend, and a Docker-based secure execution engine. This separation of concerns provides scalability, security, and maintainability.

## **Platform and Infrastructure Choice**

* **Platform:** Docker for containerization of the backend and execution engine.  
* **Hosting:** The platform is designed to be cloud-agnostic and can be deployed on any major cloud provider (AWS, Azure, GCP) that supports Docker containers and PostgreSQL.  
* **Key Services:** A virtual private server for hosting containers, a managed PostgreSQL database, and an object store for any potential file-based checkpointing.

## **Repository Structure**

* **Structure:** Monorepo. This is ideal for a full-stack application with shared logic (like types), simplifying dependency management and ensuring consistency.  
* **Monorepo Tool:** npm/pnpm/yarn workspaces will be used.

## **High-Level Architecture Diagram**

graph TD  
    subgraph User  
        A\[Browser\]  
    end

    subgraph Frontend (React SPA)  
        B\[UI Components\]  
        C\[State Management\]  
        D\[API Client\]  
    end

    subgraph Backend (FastAPI Server)  
        E\[API Endpoints\]  
        F\[Orchestration Logic & Meta-Agent\]  
        G\[Database (PostgreSQL)\]  
    end

    subgraph Secure Execution Engine  
        H\[Docker Sandbox\]  
        I\[Workflow Runner\]  
        J\[Checkpoint Manager\]  
    end

    A \--\> B  
    B \--\> C  
    C \--\> D  
    D \<--\> E

    E \--\> F  
    F \<--\> G  
    F \--\> H

    H \--\> I  
    I \--\> J  
    I \-- Streams Events \--\> F
