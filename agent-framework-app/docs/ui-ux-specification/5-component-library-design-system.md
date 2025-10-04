# **5\. Component Library / Design System**

The frontend will be built using a pre-existing component library to ensure consistency and speed up development.

* **Design System Approach:** Utilize a library like **Shadcn/UI** (or an equivalent modern, accessible component library) built on top of Tailwind CSS. This provides a set of unstyled, accessible components that we can theme to match our brand.  
* **Core Components:**  
  * **Button:** For all primary actions.  
  * **Input:** For the natural language prompt.  
  * **Tabs:** For the console panel.  
  * **Dialog/Modal:** For confirmations (e.g., "Save workflow?").  
  * **Dropdown Menu:** For user profile/logout actions.  
  * **Resizable Pane Layout:** To implement the core split-screen.  
  * **Custom Node Components:** For the visualizer, representing different Executor types.
