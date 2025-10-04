# **8\. Epic 3: Full Two-Way Interactivity**

**Goal:** To implement the bidirectional synchronization between the visual editor and the code editor.

## **Story 3.1: Implement Visual Node/Edge Manipulation**

As a user, I want to add, delete, and connect nodes in the visual diagram, so that I can edit my workflow visually. (FR4)  
Acceptance Criteria:

1. The frontend diagram renderer (e.g., using React Flow on top of Mermaid) supports adding new nodes from a palette.  
2. Users can delete nodes and edges.  
3. Users can draw new edges between nodes.

## **Story 3.2: Implement Visual-to-Code Synchronization**

As a user, when I modify the diagram, I want the Python code to update automatically. (FR5)  
Acceptance Criteria:

1. Any visual change (add/delete node/edge) triggers an event.  
2. This event sends a structured representation of the change to a new backend endpoint (e.g., POST /api/sync/visual-to-code).  
3. The backend modifies its abstract representation of the workflow graph and regenerates the complete Python code.  
4. The updated code is sent back to the frontend and displayed in the editor.  
5. The entire round-trip completes in under 500ms (NFR1).  
6. A performance test (automated or scripted) measures median and 95th percentile latency for 10 sequential node add operations (<500ms p95).  
7. Logging (debug mode) captures individual processing phases (parse → transform → respond) for latency analysis.

### Performance Validation Notes
* Include a lightweight timing harness (could be a dev-only script) to repeatedly apply changes and record durations.  
* If p95 exceeds 500ms, capture flamegraphs or profiling output and create a follow-up optimization task.

## **Story 3.3: Implement Code-to-Visual Synchronization**

As a user, when I edit the Python code, I want the visual diagram to update automatically. (FR7)  
Acceptance Criteria:

1. A debounce mechanism detects when the user stops typing in the code editor.  
2. The full content of the code editor is sent to a backend endpoint (e.g., POST /api/sync/code-to-visual).  
3. The backend parses the Python code to build an abstract representation of the workflow graph.  
4. It then uses WorkflowViz to generate a new Mermaid definition.  
5. The new definition is sent to the frontend and the visualizer is re-rendered.  
6. The end-to-end update cycle (debounce trigger to UI re-render completion) averages <400ms and stays <500ms at p95 for typical workflow size (define baseline sample).  
7. Add a profiling toggle to log parse + transform + render timings when `PERF_DEBUG=1` is set.  
8. Document a scaling test scenario (e.g., 50 nodes) and record initial latency baseline.

### Performance Validation Notes
* Use synthetic typing sequence to emulate user edits for timing consistency.  
* If latency budgets are not met, create optimization tasks (parser efficiency, caching, incremental diffing).
