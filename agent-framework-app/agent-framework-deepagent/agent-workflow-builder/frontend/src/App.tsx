import './app.css'
import '@xyflow/react/dist/style.css'
import { useState, useCallback, useRef, DragEvent } from 'react'
import {
  ReactFlow,
  MiniMap,
  Controls,
  Background,
  useNodesState,
  useEdgesState,
  addEdge,
  type Connection,
  type Edge,
  type Node,
  ReactFlowProvider,
} from '@xyflow/react'
import { NodePalette } from './components/NodePalette'
import { CheckpointManager } from './components/CheckpointManager'
import { ApprovalPanel } from './components/ApprovalPanel'
import { useAgents, useWorkflow, useWebSocket } from './hooks'
import { apiClient } from './api/client'

/**
 * Agent Workflow Builder - Main Application
 * 
 * A visual workflow builder for creating and managing AI agent workflows
 * using Microsoft Agent Framework.
 * 
 * Features:
 * - Visual workflow designer with React Flow
 * - Real-time execution monitoring via WebSocket
 * - Agent and workflow management
 * - Workflow validation and visualization
 */

const initialNodes: Node[] = []
const initialEdges: Edge[] = []

function WorkflowBuilder() {
  const [nodes, setNodes, onNodesChange] = useNodesState(initialNodes)
  const [edges, setEdges, onEdgesChange] = useEdgesState(initialEdges)
  const [selectedNode, setSelectedNode] = useState<Node | null>(null)
  const [workflowId, setWorkflowId] = useState<number | null>(null)
  const [workflowName, setWorkflowName] = useState('Untitled Workflow')
  const [validationResult, setValidationResult] = useState<any>(null)
  const [executionStatus, setExecutionStatus] = useState<string>('Ready')
  
  const reactFlowWrapper = useRef<HTMLDivElement>(null)
  const { agents, loading: agentsLoading } = useAgents()
  const { workflow, refetch: refetchWorkflow } = useWorkflow(workflowId)
  
  // WebSocket for real-time execution monitoring
  const wsUrl = workflowId 
    ? `ws://localhost:8000/api/ws/execution/${workflowId}` 
    : ''
  const { lastMessage, connected: wsConnected } = workflowId 
    ? useWebSocket(wsUrl) 
    : { lastMessage: null, connected: false }
  
  // Handle WebSocket messages
  if (lastMessage) {
    if (lastMessage.type === 'execution_event') {
      setExecutionStatus(lastMessage.data.status || 'Running')
    }
  }
  
  // Generate unique node ID
  const getId = () => `node_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`

  const onConnect = useCallback(
    (params: Connection) => setEdges((eds) => addEdge(params, eds)),
    [setEdges]
  )

  const onNodeClick = useCallback((_event: React.MouseEvent, node: Node) => {
    setSelectedNode(node)
  }, [])
  
  // Handle drag over canvas
  const onDragOver = useCallback((event: DragEvent) => {
    event.preventDefault()
    event.dataTransfer.dropEffect = 'move'
  }, [])
  
  // Handle drop on canvas
  const onDrop = useCallback(
    (event: DragEvent) => {
      event.preventDefault()
      
      if (!reactFlowWrapper.current) return
      
      const nodeType = event.dataTransfer.getData('application/reactflow')
      const agentId = event.dataTransfer.getData('agentId')
      
      if (!nodeType) return
      
      const reactFlowBounds = reactFlowWrapper.current.getBoundingClientRect()
      const position = {
        x: event.clientX - reactFlowBounds.left - 75,
        y: event.clientY - reactFlowBounds.top - 25,
      }
      
      const newNode: Node = {
        id: getId(),
        type: nodeType === 'start' ? 'input' : nodeType === 'end' ? 'output' : 'default',
        position,
        data: { 
          label: `${nodeType.charAt(0).toUpperCase() + nodeType.slice(1)} Node`,
          nodeType,
          agentId: agentId ? Number(agentId) : undefined,
        },
      }
      
      setNodes((nds) => nds.concat(newNode))
    },
    [setNodes]
  )
  
  // Create new workflow
  const handleNewWorkflow = async () => {
    try {
      const workflow = await apiClient.createWorkflow({
        name: workflowName,
        description: 'Created from workflow builder',
        version: '1.0.0',
        tags: ['builder'],
        is_template: false,
        is_public: false,
      })
      setWorkflowId(workflow.id)
      setNodes([])
      setEdges([])
      setValidationResult(null)
    } catch (error) {
      console.error('Failed to create workflow:', error)
      alert('Failed to create workflow')
    }
  }
  
  // Save workflow
  const handleSave = async () => {
    if (!workflowId) {
      await handleNewWorkflow()
      return
    }
    
    try {
      // Save nodes and edges to backend
      for (const node of nodes) {
        await apiClient.createNode({
          workflow_id: workflowId,
          name: node.data.label,
          node_type: node.data.nodeType || 'default',
          executor_type: 'AGENT',
          agent_id: node.data.agentId,
          config: { ...node.data },
          position_x: node.position.x,
          position_y: node.position.y,
          is_output_node: node.type === 'output',
        })
      }
      
      alert('Workflow saved successfully!')
      refetchWorkflow()
    } catch (error) {
      console.error('Failed to save workflow:', error)
      alert('Failed to save workflow')
    }
  }
  
  // Validate workflow
  const handleValidate = async () => {
    if (!workflowId) {
      alert('Please save the workflow first')
      return
    }
    
    try {
      const result = await apiClient.validateWorkflow(workflowId)
      setValidationResult(result)
    } catch (error) {
      console.error('Failed to validate workflow:', error)
      alert('Failed to validate workflow')
    }
  }
  
  // Execute workflow
  const handleExecute = async () => {
    if (!workflowId) {
      alert('Please save the workflow first')
      return
    }
    
    try {
      await apiClient.createExecution({
        workflow_id: workflowId,
        input_data: { message: 'Hello from workflow builder' },
      })
      setExecutionStatus('Running')
    } catch (error) {
      console.error('Failed to execute workflow:', error)
      alert('Failed to execute workflow')
    }
  }

  return (
    <div className="w-screen h-screen flex flex-col">
      {/* Header */}
      <header className="bg-gray-900 text-white p-4 shadow-lg">
        <div className="container mx-auto flex justify-between items-center">
          <div className="flex items-center gap-4">
            <h1 className="text-2xl font-bold">Agent Workflow Builder</h1>
            <input
              type="text"
              value={workflowName}
              onChange={(e) => setWorkflowName(e.target.value)}
              className="px-3 py-1 bg-gray-800 border border-gray-700 rounded text-sm"
              placeholder="Workflow name"
            />
          </div>
          <div className="flex gap-4">
            <button 
              onClick={handleNewWorkflow}
              className="px-4 py-2 bg-blue-600 hover:bg-blue-700 rounded-md transition-colors"
            >
              New Workflow
            </button>
            <button 
              onClick={handleSave}
              className="px-4 py-2 bg-green-600 hover:bg-green-700 rounded-md transition-colors"
            >
              Save
            </button>
            <button 
              onClick={handleValidate}
              className="px-4 py-2 bg-yellow-600 hover:bg-yellow-700 rounded-md transition-colors"
            >
              Validate
            </button>
            <button 
              onClick={handleExecute}
              className="px-4 py-2 bg-purple-600 hover:bg-purple-700 rounded-md transition-colors"
              disabled={!workflowId}
            >
              Execute
            </button>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <div className="flex-1 flex">
        {/* Node Palette Sidebar */}
        <NodePalette agents={agents} />

        {/* Workflow Canvas */}
        <main className="flex-1 bg-gray-50" ref={reactFlowWrapper}>
          <ReactFlow
            nodes={nodes}
            edges={edges}
            onNodesChange={onNodesChange}
            onEdgesChange={onEdgesChange}
            onConnect={onConnect}
            onNodeClick={onNodeClick}
            onDrop={onDrop}
            onDragOver={onDragOver}
            fitView
          >
            <Controls />
            <MiniMap />
            <Background gap={12} size={1} />
          </ReactFlow>
        </main>

        {/* Right Panel - Execution Monitor */}
        <aside className="w-80 bg-gray-100 border-l border-gray-300 p-4 overflow-y-auto">
          <h2 className="text-lg font-semibold mb-4">Execution Monitor</h2>
          
          <div className="space-y-3">
            {/* Status */}
            <div className="p-3 bg-white rounded-md shadow-sm border border-gray-200">
              <div className="flex items-center justify-between mb-2">
                <span className="font-medium">Status</span>
                <span className={`px-2 py-1 text-xs rounded-full ${
                  executionStatus === 'Running' ? 'bg-yellow-100 text-yellow-800' :
                  executionStatus === 'Completed' ? 'bg-green-100 text-green-800' :
                  executionStatus === 'Failed' ? 'bg-red-100 text-red-800' :
                  'bg-green-100 text-green-800'
                }`}>
                  {executionStatus}
                </span>
              </div>
              <div className="text-sm text-gray-600">
                {wsConnected ? '🟢 Connected to execution stream' : '⚪ Not connected'}
              </div>
            </div>

            {/* Validation Results */}
            {validationResult && (
              <div className="p-3 bg-white rounded-md shadow-sm border border-gray-200">
                <div className="font-medium mb-2">Validation</div>
                {validationResult.valid ? (
                  <div className="text-sm text-green-600">✅ Valid workflow</div>
                ) : (
                  <div className="text-sm text-red-600">
                    ❌ {validationResult.errors?.length || 0} errors
                    {validationResult.errors?.map((error: string, i: number) => (
                      <div key={i} className="mt-1 text-xs">{error}</div>
                    ))}
                  </div>
                )}
                {validationResult.warnings && validationResult.warnings.length > 0 && (
                  <div className="text-sm text-yellow-600 mt-2">
                    ⚠️ {validationResult.warnings.length} warnings
                  </div>
                )}
              </div>
            )}

            {/* Selected Node */}
            {selectedNode && (
              <div className="p-4 bg-white rounded-md shadow-sm border border-gray-200">
                <h3 className="font-semibold mb-2">Node Properties</h3>
                <div className="text-sm space-y-2">
                  <div>
                    <span className="font-medium">ID:</span> {selectedNode.id}
                  </div>
                  <div>
                    <span className="font-medium">Type:</span> {selectedNode.data.nodeType || selectedNode.type}
                  </div>
                  <div>
                    <span className="font-medium">Label:</span> {String(selectedNode.data.label)}
                  </div>
                  {selectedNode.data.agentId && (
                    <div>
                      <span className="font-medium">Agent ID:</span> {selectedNode.data.agentId}
                    </div>
                  )}
                </div>
              </div>
            )}
            
            {/* Workflow Info */}
            <div className="p-3 bg-white rounded-md shadow-sm border border-gray-200">
              <div className="font-medium mb-2">Workflow Info</div>
              <div className="text-sm text-gray-600">
                <div>Nodes: {nodes.length}</div>
                <div>Edges: {edges.length}</div>
                {workflowId && <div>ID: {workflowId}</div>}
              </div>
            </div>
            
            {/* Checkpoints */}
            {workflowId && (
              <div className="mt-4">
                <CheckpointManager 
                  workflowId={String(workflowId)} 
                  onRestore={() => {
                    setExecutionStatus('Restored');
                    alert('Workflow restored from checkpoint');
                  }}
                />
              </div>
            )}

            {/* Approval Requests */}
            {workflowId && (
              <div className="mt-4">
                <ApprovalPanel 
                  workflowId={String(workflowId)}
                  onApprovalProcessed={() => {
                    console.log('Approval processed, refreshing workflow state');
                  }}
                />
              </div>
            )}

            {/* Agents */}
            {!agentsLoading && agents.length > 0 && (
              <div className="p-3 bg-white rounded-md shadow-sm border border-gray-200">
                <div className="font-medium mb-2">Available Agents</div>
                <div className="text-sm space-y-1 max-h-40 overflow-y-auto">
                  {agents.map((agent) => (
                    <div key={agent.id} className="p-2 bg-gray-50 rounded text-xs">
                      <div className="font-medium">{agent.name}</div>
                      <div className="text-gray-500">{agent.agent_type}</div>
                    </div>
                  ))}
                </div>
              </div>
            )}
          </div>
        </aside>
      </div>

      {/* Footer */}
      <footer className="bg-gray-900 text-white p-2 text-center text-sm">
        <span>Agent Workflow Builder v0.1.0 | Powered by Microsoft Agent Framework</span>
      </footer>
    </div>
  )
}

function App() {
  return (
    <ReactFlowProvider>
      <WorkflowBuilder />
    </ReactFlowProvider>
  )
}

export default App
