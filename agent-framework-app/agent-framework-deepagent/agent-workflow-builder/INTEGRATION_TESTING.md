# Frontend-Backend Integration Testing Guide

## Overview

This document provides detailed test cases for verifying the integration between the Agent Workflow Builder frontend (React/Vite) and backend (FastAPI).

## Prerequisites

### Environment Setup

1. **Backend Running:**
   ```bash
   cd backend
   uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
   ```

2. **Frontend Running:**
   ```bash
   cd frontend
   npm run dev
   # Server runs on http://localhost:3000
   ```

3. **Browser DevTools Open:**
   - Press F12 to open DevTools
   - Go to Console tab for JavaScript logs
   - Go to Network tab for API requests
   - Filter by "WS" in Network tab for WebSocket connections

## Test Suite 1: Basic Connectivity

### Test 1.1: Frontend Loads Successfully
**Steps:**
1. Navigate to http://localhost:3000
2. Wait for page to fully load

**Expected Results:**
- ✅ Page renders without errors
- ✅ "Agent Workflow Builder" title visible
- ✅ Node palette visible on left
- ✅ Canvas area visible in center
- ✅ Execution monitor visible on right
- ✅ No console errors

**Validation:**
```javascript
// Check in browser console:
console.log(document.title); // Should be "frontend"
console.log(document.querySelectorAll('.node-palette').length); // Should be 1
```

### Test 1.2: Backend Health Check
**Steps:**
1. Open new terminal
2. Execute health check command

**Command:**
```bash
curl http://localhost:8000/health
```

**Expected Response:**
```json
{
  "status": "healthy",
  "environment": "development"
}
```

### Test 1.3: Frontend-Backend Connection
**Steps:**
1. Open browser DevTools → Console
2. Check for connection errors
3. Look at Execution Monitor status

**Expected Results:**
- ✅ No "ERR_CONNECTION_REFUSED" errors
- ✅ Execution Monitor shows "Connected" (green indicator)
- ✅ No CORS errors in console

**Common Issues:**
- ❌ "ERR_CONNECTION_REFUSED" → Backend not running
- ❌ CORS errors → Check backend ALLOWED_ORIGINS setting
- ❌ "Network Error" → Check firewall/proxy settings

### Test 1.4: API Documentation Access
**Steps:**
1. Navigate to http://localhost:8000/docs

**Expected Results:**
- ✅ Swagger UI loads
- ✅ API endpoints visible
- ✅ Can expand and test endpoints

## Test Suite 2: Agent Management

### Test 2.1: List Agents (Empty State)
**Steps:**
1. Open frontend at http://localhost:3000
2. Check Execution Monitor → Agents section

**Expected Results:**
- ✅ Agents list loads
- ✅ Shows empty state or existing agents
- ✅ No errors in console

**API Verification:**
```bash
curl http://localhost:8000/api/v1/agents/
```

**Expected Response:**
```json
[]
```
or
```json
[
  {
    "id": 1,
    "name": "Test Agent",
    "description": "...",
    "agent_type": "CHAT_AGENT",
    ...
  }
]
```

### Test 2.2: Create Agent via API
**Steps:**
1. Use curl or Swagger UI to create an agent

**Command:**
```bash
curl -X POST http://localhost:8000/api/v1/agents/ \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Test Agent",
    "description": "A test agent for integration testing",
    "agent_type": "CHAT_AGENT",
    "instructions": "You are a helpful assistant that helps users test workflows.",
    "model_config": {
      "model": "gpt-4",
      "temperature": 0.7,
      "max_tokens": 1000
    },
    "tools": []
  }'
```

**Expected Response:**
```json
{
  "id": 1,
  "name": "Test Agent",
  "description": "A test agent for integration testing",
  "agent_type": "CHAT_AGENT",
  "instructions": "You are a helpful assistant that helps users test workflows.",
  "model_config": {
    "model": "gpt-4",
    "temperature": 0.7,
    "max_tokens": 1000
  },
  "tools": [],
  "created_at": "2025-01-06T...",
  "updated_at": "2025-01-06T..."
}
```

### Test 2.3: Agent Appears in Frontend
**Steps:**
1. After creating agent via API
2. Frontend should automatically refresh agents list
3. Check Execution Monitor → Agents section

**Expected Results:**
- ✅ New agent appears in list
- ✅ Agent name displayed correctly
- ✅ Can select agent for use in workflow

### Test 2.4: Create Agent via UI (Future Feature)
**Note:** This test is for when UI agent creation is implemented

**Steps:**
1. Click "Add Agent" button (if available)
2. Fill in agent form
3. Click "Save"

**Expected Results:**
- ✅ Form validates input
- ✅ POST request to /api/v1/agents/
- ✅ Success message displayed
- ✅ New agent appears in list

## Test Suite 3: Workflow Builder

### Test 3.1: Drag Start Node
**Steps:**
1. Click and hold "Start Node" in Node Palette
2. Drag onto canvas
3. Release mouse button

**Expected Results:**
- ✅ Node appears on canvas at drop location
- ✅ Node is green (Start Node color)
- ✅ Node has label "Start Node"
- ✅ Workflow Info updates: "Nodes: 1"

### Test 3.2: Drag Agent Node
**Steps:**
1. Drag "Agent Node" from palette
2. Drop on canvas next to Start Node

**Expected Results:**
- ✅ Node appears on canvas
- ✅ Node is blue (Agent Node color)
- ✅ Node has label "Agent Node"
- ✅ Workflow Info updates: "Nodes: 2"

### Test 3.3: Connect Nodes
**Steps:**
1. Hover over Start Node
2. Click on output handle (right side)
3. Drag to Agent Node input handle (left side)
4. Release to connect

**Expected Results:**
- ✅ Edge (connection line) appears
- ✅ Edge connects the two nodes
- ✅ Edge is animated (showing flow direction)
- ✅ Workflow Info updates: "Edges: 1"

### Test 3.4: Add End Node
**Steps:**
1. Drag "End Node" from palette
2. Drop on canvas
3. Connect Agent Node output to End Node input

**Expected Results:**
- ✅ End Node appears (red color)
- ✅ Nodes: 3, Edges: 2
- ✅ Complete workflow visible

### Test 3.5: Save Workflow
**Steps:**
1. Enter workflow name in textbox (e.g., "Test Workflow")
2. Click "Save" button
3. Check browser Network tab

**Expected Results:**
- ✅ POST request to /api/v1/workflows/
- ✅ Request payload contains nodes and edges
- ✅ Response status 200 or 201
- ✅ Success message displayed
- ✅ Workflow ID stored in UI state

**Network Tab - Request:**
```json
{
  "name": "Test Workflow",
  "version": "1.0.0",
  "nodes": [
    {
      "id": "node-1",
      "type": "start",
      "position": {"x": 100, "y": 100},
      "data": {...}
    },
    {
      "id": "node-2",
      "type": "agent",
      "position": {"x": 300, "y": 100},
      "data": {"agentId": 1, ...}
    },
    {
      "id": "node-3",
      "type": "end",
      "position": {"x": 500, "y": 100},
      "data": {...}
    }
  ],
  "edges": [
    {
      "id": "edge-1",
      "source": "node-1",
      "target": "node-2"
    },
    {
      "id": "edge-2",
      "source": "node-2",
      "target": "node-3"
    }
  ]
}
```

## Test Suite 4: Workflow Validation

### Test 4.1: Validate Valid Workflow
**Steps:**
1. Create a valid workflow (Start → Agent → End)
2. Save workflow
3. Click "Validate" button

**Expected Results:**
- ✅ POST request to /api/v1/workflows/{id}/validate
- ✅ Validation passes
- ✅ Green checkmark or success message
- ✅ "Execute" button becomes enabled

### Test 4.2: Validate Invalid Workflow (Missing Start Node)
**Steps:**
1. Create workflow with only Agent → End
2. Click "Validate"

**Expected Results:**
- ✅ Validation fails
- ✅ Error message: "Workflow must have exactly one Start node"
- ✅ "Execute" button stays disabled

### Test 4.3: Validate Invalid Workflow (Disconnected Nodes)
**Steps:**
1. Create workflow with Start and Agent nodes, but no edge
2. Click "Validate"

**Expected Results:**
- ✅ Validation fails
- ✅ Error message about disconnected nodes
- ✅ Problem nodes highlighted on canvas

### Test 4.4: Validate Invalid Workflow (Multiple Paths from Start)
**Steps:**
1. Create Start node with edges to two different Agent nodes
2. Click "Validate"

**Expected Results:**
- ✅ Validation may pass or warn depending on requirements
- ✅ Clear feedback about workflow structure

## Test Suite 5: Workflow Execution

### Test 5.1: Execute Simple Workflow
**Steps:**
1. Create and validate workflow: Start → Agent → End
2. Click "Execute" button
3. Monitor Execution Monitor panel

**Expected Results:**
- ✅ POST request to /api/v1/executions/
- ✅ WebSocket connection establishes
- ✅ Status changes to "Running"
- ✅ Real-time updates display
- ✅ Status changes to "Completed"
- ✅ Execution results display

**WebSocket Messages:**
```json
// Initial message
{
  "type": "execution_started",
  "execution_id": 1,
  "workflow_id": 1
}

// Progress updates
{
  "type": "node_started",
  "node_id": "node-1"
}

{
  "type": "node_completed",
  "node_id": "node-1",
  "output": {...}
}

// Final message
{
  "type": "execution_completed",
  "execution_id": 1,
  "status": "success",
  "output": {...}
}
```

### Test 5.2: Execute Workflow with Input
**Steps:**
1. Execute workflow
2. Provide input when prompted (if applicable)

**Expected Results:**
- ✅ Input form appears
- ✅ Can enter text/data
- ✅ Input sent to backend
- ✅ Workflow processes input

### Test 5.3: Monitor Execution in Real-Time
**Steps:**
1. Execute a multi-node workflow
2. Watch Execution Monitor panel

**Expected Results:**
- ✅ Each node highlights as it executes
- ✅ Progress indicator updates
- ✅ Can see intermediate outputs
- ✅ Timestamps for each step

### Test 5.4: Handle Execution Error
**Steps:**
1. Create workflow with an agent that will fail
2. Execute workflow

**Expected Results:**
- ✅ Status changes to "Failed"
- ✅ Error message displayed
- ✅ Failed node highlighted on canvas
- ✅ Can view error details

## Test Suite 6: WebSocket Connection

### Test 6.1: WebSocket Connection Establishes
**Steps:**
1. Open DevTools → Network tab
2. Filter by "WS"
3. Execute a workflow

**Expected Results:**
- ✅ WebSocket connection to ws://localhost:8000/ws/executions/{id}
- ✅ Status: "101 Switching Protocols"
- ✅ Connection stays open during execution

### Test 6.2: WebSocket Receives Messages
**Steps:**
1. During workflow execution
2. Click on WebSocket connection in Network tab
3. View Messages sub-tab

**Expected Results:**
- ✅ Can see sent and received messages
- ✅ Messages are valid JSON
- ✅ Message types match expected protocol
- ✅ No malformed messages

### Test 6.3: WebSocket Reconnection
**Steps:**
1. Start workflow execution
2. Disconnect network briefly
3. Reconnect

**Expected Results:**
- ✅ WebSocket attempts reconnection
- ✅ Execution state syncs after reconnect
- ✅ No data loss

### Test 6.4: WebSocket Closes Gracefully
**Steps:**
1. Execute workflow to completion
2. Check WebSocket status

**Expected Results:**
- ✅ WebSocket closes after execution
- ✅ Close code is normal (1000)
- ✅ No error messages

## Test Suite 7: Error Handling

### Test 7.1: Backend Unavailable
**Steps:**
1. Stop backend server
2. Try to interact with frontend

**Expected Results:**
- ✅ Frontend shows "Not connected" status
- ✅ User-friendly error messages
- ✅ No JavaScript errors
- ✅ UI still functional (can design workflows offline)

### Test 7.2: Network Timeout
**Steps:**
1. Simulate slow network
2. Try to save workflow

**Expected Results:**
- ✅ Loading indicator displays
- ✅ Timeout error after reasonable wait
- ✅ Can retry operation

### Test 7.3: Invalid API Response
**Steps:**
1. Backend returns 400/500 error
2. Check frontend handling

**Expected Results:**
- ✅ Error message displayed
- ✅ Error details available
- ✅ UI recovers gracefully

## Test Suite 8: Performance

### Test 8.1: Large Workflow (50+ Nodes)
**Steps:**
1. Create workflow with 50+ nodes
2. Try to pan, zoom, save

**Expected Results:**
- ✅ Canvas remains responsive
- ✅ Save operation completes in <5 seconds
- ✅ No browser freezing

### Test 8.2: Multiple Executions
**Steps:**
1. Execute same workflow 10 times rapidly

**Expected Results:**
- ✅ All executions queue properly
- ✅ No race conditions
- ✅ Each execution tracked separately

### Test 8.3: Long-Running Execution
**Steps:**
1. Execute workflow that takes 2+ minutes

**Expected Results:**
- ✅ WebSocket stays connected
- ✅ Updates continue flowing
- ✅ Can cancel execution

## Test Suite 9: Browser Compatibility

### Test 9.1: Chrome/Edge
- ✅ All features work
- ✅ No console errors
- ✅ WebSocket stable

### Test 9.2: Firefox
- ✅ All features work
- ✅ Drag-and-drop smooth
- ✅ Canvas rendering correct

### Test 9.3: Safari (if available)
- ✅ Core features work
- ✅ Check for WebKit-specific issues

## Test Suite 10: Security

### Test 10.1: CORS Headers
**Steps:**
1. Check Network tab for API responses
2. Look for CORS headers

**Expected Headers:**
```
Access-Control-Allow-Origin: http://localhost:3000
Access-Control-Allow-Credentials: true
Access-Control-Allow-Methods: *
Access-Control-Allow-Headers: *
```

### Test 10.2: No Sensitive Data in Console
**Steps:**
1. Check console logs
2. Check Network tab responses

**Expected:**
- ✅ No API keys logged
- ✅ No passwords visible
- ✅ Sensitive data redacted

## Test Reporting Template

### Test Session Report

**Date:** YYYY-MM-DD  
**Tester:** Name  
**Environment:**
- Frontend Version: v0.1.0
- Backend Version: v1.0.0
- Browser: Chrome 120.x
- OS: Windows/Mac/Linux

**Tests Executed:**
| Test ID | Test Name | Status | Notes |
|---------|-----------|--------|-------|
| 1.1 | Frontend Loads | ✅ Pass | - |
| 1.2 | Backend Health | ✅ Pass | - |
| 3.1 | Drag Start Node | ✅ Pass | - |
| 5.1 | Execute Workflow | ❌ Fail | Timeout after 30s |
| ... | ... | ... | ... |

**Issues Found:**
1. **Issue #1:** Workflow execution timeout
   - **Severity:** High
   - **Steps to Reproduce:** ...
   - **Expected:** ...
   - **Actual:** ...

**Overall Status:** 45/50 tests passed (90%)

---

## Quick Test Commands

```bash
# Backend health
curl http://localhost:8000/health

# List agents
curl http://localhost:8000/api/v1/agents/

# Create agent
curl -X POST http://localhost:8000/api/v1/agents/ \
  -H "Content-Type: application/json" \
  -d @test-agent.json

# List workflows
curl http://localhost:8000/api/v1/workflows/

# Validate workflow
curl -X POST http://localhost:8000/api/v1/workflows/1/validate

# Execute workflow
curl -X POST http://localhost:8000/api/v1/executions/ \
  -H "Content-Type: application/json" \
  -d '{"workflow_id": 1, "input_data": {"message": "Hello"}}'

# Get execution status
curl http://localhost:8000/api/v1/executions/1
```

---

**Document Version:** 1.0  
**Last Updated:** January 6, 2025  
**Status:** Ready for Testing ✅
