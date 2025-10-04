# **2\. Information Architecture (IA)**

## **Site Map / Screen Inventory**

The application has a simple, focused information architecture centered around the two main user contexts: managing workflows and working on a single workflow.

graph TD  
    A\[User visits site\] \--\> B{Logged In?};  
    B \--\>|No| C\[Login / Signup Page\];  
    B \--\>|Yes| D\[Dashboard (Workflow List)\];  
    C \--\> D;  
    D \--\> E\[Workspace (Editor)\];  
    E \--\> D;

## **Navigation Structure**

* **Primary Navigation:** A persistent top header will contain the application logo, a link back to the Dashboard, user profile/authentication controls (e.g., "Logged in as user@email.com", "Logout"), and the name of the current workflow being edited.  
* **Workspace Controls:** Within the Workspace view, primary actions like "Generate", "Run", "Debug", "Save", and "Share" will be located in a prominent, easily accessible control bar above the main split-screen panes.
