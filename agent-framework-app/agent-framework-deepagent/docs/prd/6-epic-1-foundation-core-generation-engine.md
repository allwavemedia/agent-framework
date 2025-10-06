# **6\. Epic 1: Foundation & Core Generation Engine**

**Goal:** To deliver the core value proposition: converting a natural language prompt into executable, framework-compliant Python code and a corresponding visual diagram, and running it securely.

## **Story 1.1: Project Scaffolding & Setup**

As a developer, I want a complete monorepo structure with frontend and backend applications set up, so that I can begin development efficiently.  
Acceptance Criteria:

1. A monorepo is initialized.  
2. A basic "Hello World" React application is created in the `apps/frontend` directory.  
3. A basic "Hello World" FastAPI application is created in the `apps/backend` directory.  
4. Both applications can be started with a single `npm run dev` command from the root.  
5. Docker Desktop (or compatible engine) installation is verified locally (version logged).  
6. Required language runtimes are verified: **Node.js LTS version** and **Python 3.11+** (version outputs recorded).  
7. A `.env.example` file is created listing all baseline environment variables (placeholders only).  
8. README local setup section includes: prerequisites, install, bootstrap, run, test, lint steps.  
9. Initial database container/service (PostgreSQL) is provisioned via Docker Compose and reachable from backend service.  
10. A database migration tool is selected and initialized (e.g., Alembic for Python) with an empty baseline migration.

### Developer Environment Checklist (Informational)
* Node.js LTS installed & version logged
* Python 3.11+ installed & version logged
* Docker engine running
* `npm install` succeeds at root
* `npm run dev` starts both services
* Database container starts and accepts connections

## **Story 1.1.5: External Service Configuration (Azure/OpenAI)**

As a platform engineer, I want external LLM service credentials provisioned and securely injected, so that generation APIs function reliably in all environments.  
Acceptance Criteria:

1. Azure OpenAI (or OpenAI) resource creation steps documented (portal & CLI reference).  
2. Keys & endpoint retrieved from Azure portal **Keys and Endpoint** blade (two-key rotation practice noted).  
3. Environment variables defined in `.env.example` (e.g., `AZURE_OPENAI_API_KEY`, `AZURE_OPENAI_ENDPOINT`, `AZURE_OPENAI_DEPLOYMENT_NAME`, `OPENAI_API_VERSION`).  
4. Local `.env` loading verified; application can read variables at runtime (simple health endpoint or startup log).  
5. Secret storage guidance documented (recommend Azure Key Vault for cloud deployments; no plaintext keys committed).  
6. Key rotation procedure documented (swap KEY1/KEY2 with zero downtime).  
7. Security note: prefer Microsoft Entra ID / managed identity for production; API key usage flagged as interim.  
8. A minimal script or backend health endpoint validates the model credentials (dry-run or simple prompt).  

Sources (for key retrieval & environment handling): See project PRD master sources section to be appended (will reference official Azure OpenAI quickstarts).

## **Story 1.2: Implement NLP to Python Generation API**

As a user, I want to submit a text prompt to the application, so that it generates a Python script for an AI workflow. (FR1)  
Acceptance Criteria:

1. An API endpoint POST /api/generate-workflow is created.  
2. It accepts a JSON payload with a prompt field.  
3. It uses a meta-agent (ChatClientAgent with structured output) to process the prompt.  
4. It returns a JSON response containing the generated Python code as a string.

## **Story 1.3: Implement Workflow Visualization API**

As a developer, I want an API that converts a workflow's Python code into a visual diagram definition, so that it can be rendered on the frontend. (FR2)  
Acceptance Criteria:

1. An API endpoint POST /api/visualize-workflow is created.  
2. It accepts Python code as input.  
3. It uses the WorkflowViz class to generate a Mermaid diagram definition string.  
4. It returns the Mermaid string in a JSON response.

## **Story 1.3.5: API Integration Testing Harness**

As a developer, I want an automated integration testing harness for the generation and visualization APIs, so that regressions are caught before UI integration.  
Acceptance Criteria:

1. Test runner configured (e.g., pytest + requests or httpx) with a dedicated `tests/integration` directory.  
2. A Docker Compose or local script starts backend dependencies (DB + backend service) for tests.  
3. Tests cover happy path for `/api/generate-workflow` (valid prompt returns Python code).  
4. Tests cover error handling (empty prompt, invalid payload).  
5. Tests for `/api/visualize-workflow` using sample Python code produce a Mermaid definition.  
6. Round‑trip test: generation output fed into visualization endpoint successfully.  
7. Basic performance assertion: each endpoint responds < 1s under local dev conditions.  
8. CI workflow placeholder or script stub added for future automation.

## **Story 1.4: Build Core UI Layout**

As a user, I want to see a split-screen layout with a placeholder for the visual diagram and a code editor, so that I can interact with the core features. (FR2, FR3)  
Acceptance Criteria:

1. The main UI displays a left pane for the visualizer and a right pane with an embedded Monaco code editor.  
2. A text input field and a "Generate" button are present.  
3. Pressing "Generate" calls the /api/generate-workflow endpoint and displays the returned code in the editor.  
4. The generated code is then sent to the /api/visualize-workflow endpoint, and the returned Mermaid definition is rendered in the left pane.

## **Story 1.5: Implement Secure Execution Engine**

As a developer, I want a secure sandbox to execute user-provided Python code, so that workflows can be run without risk to the system. (FR8)  
Acceptance Criteria:

1. A Docker image is created with Python and agent-framework installed.  
2. An internal API is created on the backend that accepts Python code.  
3. The API spins up a new, isolated Docker container to run the code.  
4. The container has networking disabled and strict CPU/memory limits.  
5. Standard output and errors from the script are captured and returned.

## **Story 1.6: Implement Real-time Event Streaming**

---
### Dependency Ordering Rationale (Informational)
1.1 scaffolds environment → 1.1.5 provisions external LLM credentials → 1.2 implements generation → 1.3 adds visualization → 1.3.5 validates both APIs integratively → 1.4 UI consumes stable APIs → 1.5 adds secure execution → 1.6 streams events.

### Added Cross-Cutting Requirements
* **Database Migration Strategy:** Alembic baseline migration in Story 1.1 ensures reproducible schema evolution; future stories extend migrations instead of ad-hoc SQL.
* **API Documentation Generation:** Add a task (later story or ops doc) to integrate automatic OpenAPI doc exposure (`/docs` via FastAPI) and ensure endpoints include descriptive models.
* **Environment Validation:** Story 1.1 now enforces explicit version & tooling checks to reduce onboarding friction.
* **External Service Security:** Story 1.1.5 documents secure key handling, rotation, and encourages migration to managed identity.

### Follow-Up (Will Be Addressed in Later Epics)
* Error handling pattern centralization
* Observability/logging instrumentation
* Structured performance benchmarks
* Accessibility and UI quality gates

### Sources (Azure OpenAI Key & Endpoint Handling)
* Azure OpenAI Quickstart (Retrieve key and endpoint & environment variable guidance) – https://learn.microsoft.com/en-us/azure/ai-foundry/openai/quickstart#retrieve-key-and-endpoint  
* Azure OpenAI Chat Completions Quickstart (Key rotation & two-key model) – https://learn.microsoft.com/en-us/azure/ai-foundry/openai/chatgpt-quickstart#set-up  
* Azure AI Services Authentication (Recommendation for Microsoft Entra ID / managed identity) – https://learn.microsoft.com/en-us/azure/ai-services/authentication  
* API Keys Security & Key Vault guidance – https://learn.microsoft.com/en-us/azure/key-vault/general/apps-api-keys-secrets


As a user, I want to see real-time events from my workflow execution in a console, so that I can understand its progress. (FR9)  
Acceptance Criteria:

1. A WebSocket connection is established between the frontend and backend when a workflow is executed.  
2. The Secure Execution Engine streams WorkflowEvent data back to the backend.  
3. The backend forwards these events over the WebSocket to the frontend.  
4. A collapsible console in the UI displays a formatted log of incoming events.
