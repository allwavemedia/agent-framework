import './app.css'
import '@xyflow/react/dist/style.css'
import { useState, useCallback } from 'react'
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
} from '@xyflow/react'

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

const initialNodes: Node[] = [
  {
    id: '1',
    type: 'input',
    data: { label: 'Start' },
    position: { x: 250, y: 0 },
  },
]

const initialEdges: Edge[] = []

function App() {
  const [nodes, setNodes, onNodesChange] = useNodesState(initialNodes)
  const [edges, setEdges, onEdgesChange] = useEdgesState(initialEdges)
  const [selectedNode, setSelectedNode] = useState<Node | null>(null)

  const onConnect = useCallback(
    (params: Connection) => setEdges((eds) => addEdge(params, eds)),
    [setEdges]
  )

  const onNodeClick = useCallback((_event: React.MouseEvent, node: Node) => {
    setSelectedNode(node)
  }, [])

  return (
    <div className="w-screen h-screen flex flex-col">
      {/* Header */}
      <header className="bg-gray-900 text-white p-4 shadow-lg">
        <div className="container mx-auto flex justify-between items-center">
          <h1 className="text-2xl font-bold">Agent Workflow Builder</h1>
          <div className="flex gap-4">
            <button className="px-4 py-2 bg-blue-600 hover:bg-blue-700 rounded-md transition-colors">
              New Workflow
            </button>
            <button className="px-4 py-2 bg-green-600 hover:bg-green-700 rounded-md transition-colors">
              Save
            </button>
            <button className="px-4 py-2 bg-purple-600 hover:bg-purple-700 rounded-md transition-colors">
              Execute
            </button>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <div className="flex-1 flex">
        {/* Sidebar */}
        <aside className="w-64 bg-gray-100 border-r border-gray-300 p-4">
          <h2 className="text-lg font-semibold mb-4">Components</h2>
          
          <div className="space-y-2">
            <div className="p-3 bg-white rounded-md shadow-sm border border-gray-200 cursor-grab hover:shadow-md transition-shadow">
              <div className="font-medium">Agent Node</div>
              <div className="text-sm text-gray-600">AI Agent Executor</div>
            </div>
            
            <div className="p-3 bg-white rounded-md shadow-sm border border-gray-200 cursor-grab hover:shadow-md transition-shadow">
              <div className="font-medium">Sequential Node</div>
              <div className="text-sm text-gray-600">Sequential Execution</div>
            </div>
            
            <div className="p-3 bg-white rounded-md shadow-sm border border-gray-200 cursor-grab hover:shadow-md transition-shadow">
              <div className="font-medium">Concurrent Node</div>
              <div className="text-sm text-gray-600">Parallel Execution</div>
            </div>
            
            <div className="p-3 bg-white rounded-md shadow-sm border border-gray-200 cursor-grab hover:shadow-md transition-shadow">
              <div className="font-medium">Condition Node</div>
              <div className="text-sm text-gray-600">Conditional Branch</div>
            </div>
          </div>

          {selectedNode && (
            <div className="mt-6 p-4 bg-white rounded-md shadow-sm border border-gray-200">
              <h3 className="font-semibold mb-2">Node Properties</h3>
              <div className="text-sm">
                <div className="mb-2">
                  <span className="font-medium">ID:</span> {selectedNode.id}
                </div>
                <div className="mb-2">
                  <span className="font-medium">Type:</span> {selectedNode.type}
                </div>
                <div className="mb-2">
                  <span className="font-medium">Label:</span>{' '}
                  {String(selectedNode.data.label)}
                </div>
              </div>
            </div>
          )}
        </aside>

        {/* Workflow Canvas */}
        <main className="flex-1 bg-gray-50">
          <ReactFlow
            nodes={nodes}
            edges={edges}
            onNodesChange={onNodesChange}
            onEdgesChange={onEdgesChange}
            onConnect={onConnect}
            onNodeClick={onNodeClick}
            fitView
          >
            <Controls />
            <MiniMap />
            <Background gap={12} size={1} />
          </ReactFlow>
        </main>

        {/* Right Panel - Execution Monitor */}
        <aside className="w-80 bg-gray-100 border-l border-gray-300 p-4">
          <h2 className="text-lg font-semibold mb-4">Execution Monitor</h2>
          
          <div className="space-y-3">
            <div className="p-3 bg-white rounded-md shadow-sm border border-gray-200">
              <div className="flex items-center justify-between mb-2">
                <span className="font-medium">Status</span>
                <span className="px-2 py-1 bg-green-100 text-green-800 text-xs rounded-full">
                  Ready
                </span>
              </div>
              <div className="text-sm text-gray-600">
                Workflow is ready to execute
              </div>
            </div>

            <div className="p-3 bg-white rounded-md shadow-sm border border-gray-200">
              <div className="font-medium mb-2">Recent Executions</div>
              <div className="text-sm text-gray-500">No executions yet</div>
            </div>

            <div className="p-3 bg-white rounded-md shadow-sm border border-gray-200">
              <div className="font-medium mb-2">Validation</div>
              <div className="text-sm text-gray-500">
                Add nodes to validate workflow
              </div>
            </div>
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

export default App
