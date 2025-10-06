# **7\. Epic 2: User & Workflow Persistence**

**Goal:** To enable users to create accounts, save their work, and reload it in a future session.

## **Story 2.1: Set up User Authentication**

As a user, I want to sign up and log in, so that I can save my work.  
Acceptance Criteria:

1. A user database table is created.  
2. API endpoints for user registration and login (e.g., using JWTs) are implemented.  
3. The frontend provides simple sign-up and login forms.  
4. Authenticated routes are protected.  
5. Passwords are hashed using a modern algorithm (e.g., Argon2 or bcrypt) with appropriate work factors.  
6. JWTs include expiration (short-lived access) and a refresh token mechanism is outlined (even if implemented in later epic).  
7. Secret keys for JWT signing are injected via environment variables (never hard-coded) and rotation procedure documented.  
8. Basic rate limiting strategy (login attempts) is specified for future implementation (placeholder if not implemented here).  
9. Input validation & error responses avoid leaking user existence (generic auth failure message).  
10. Minimal audit logging plan documented (successful login, failed login, registration).  

### Security Hardening Notes (Must Review Before Implementation)
* Choose Argon2 (preferred) or bcrypt with cost factor aligned to performance budget.  
* Store only password hashes + per-user salt (library-managed).  
* JWT signing key length & algorithm: HS256 acceptable for MVP; plan migration to asymmetric keys (RS256) for multi-service scaling.  
* Document rotation: issue new key, accept old for grace period, revoke after window.  
* Rate limiting to mitigate brute force (future: implement with middleware or gateway).  
* Consider adding email verification flow in a later epic (deferred).  
* All auth endpoints return uniform error shape.  


## **Story 2.2: Implement Save Workflow API**

As a logged-in user, I want to save my current workflow, so that I can access it later. (FR11)  
Acceptance Criteria:

1. A workflows database table is created, linked to the user table.  
2. An authenticated API endpoint POST /api/workflows is created.  
3. It accepts a name and the code (Python script) for the workflow.  
4. The workflow is saved to the database.

## **Story 2.3: Implement List & Load Workflows**

As a logged-in user, I want to see a list of my saved workflows and load one into the editor. (FR12)  
Acceptance Criteria:

1. An authenticated API endpoint GET /api/workflows returns a list of the user's saved workflows.  
2. A dashboard page is created to display this list.  
3. Clicking a workflow in the list loads its code into the main editor and triggers a re-visualization.
