/**
 * Node Palette Component
 * Displays available node types that can be dragged onto the workflow canvas
 */
import { useState } from 'react';
import type { Agent } from '../types';

interface NodePaletteProps {
  agents: Agent[];
  onNodeTypeSelect?: (nodeType: string) => void;
}

interface NodeType {
  type: string;
  label: string;
  description: string;
  icon: string;
  color: string;
}

const nodeTypes: NodeType[] = [
  {
    type: 'start',
    label: 'Start Node',
    description: 'Workflow entry point',
    icon: '▶️',
    color: 'bg-green-100 border-green-300',
  },
  {
    type: 'agent',
    label: 'Agent Node',
    description: 'AI Agent Executor',
    icon: '🤖',
    color: 'bg-blue-100 border-blue-300',
  },
  {
    type: 'sequential',
    label: 'Sequential Node',
    description: 'Sequential Execution',
    icon: '➡️',
    color: 'bg-purple-100 border-purple-300',
  },
  {
    type: 'concurrent',
    label: 'Concurrent Node',
    description: 'Parallel Execution',
    icon: '⚡',
    color: 'bg-yellow-100 border-yellow-300',
  },
  {
    type: 'condition',
    label: 'Condition Node',
    description: 'Conditional Branch',
    icon: '❓',
    color: 'bg-orange-100 border-orange-300',
  },
  {
    type: 'end',
    label: 'End Node',
    description: 'Workflow exit point',
    icon: '🏁',
    color: 'bg-red-100 border-red-300',
  },
];

export function NodePalette({ agents, onNodeTypeSelect }: NodePaletteProps) {
  const [selectedAgent, setSelectedAgent] = useState<number | null>(null);

  const onDragStart = (event: React.DragEvent, nodeType: string) => {
    event.dataTransfer.setData('application/reactflow', nodeType);
    event.dataTransfer.effectAllowed = 'move';
    
    if (nodeType === 'agent' && selectedAgent) {
      event.dataTransfer.setData('agentId', selectedAgent.toString());
    }
  };

  return (
    <div className="w-64 bg-gray-100 border-r border-gray-300 p-4 overflow-y-auto">
      <h2 className="text-lg font-semibold mb-4 text-gray-800">Node Palette</h2>
      
      <div className="space-y-3">
        {nodeTypes.map((node) => (
          <div
            key={node.type}
            className={`p-3 ${node.color} rounded-md shadow-sm border-2 cursor-grab hover:shadow-md transition-shadow active:cursor-grabbing`}
            draggable
            onDragStart={(e) => onDragStart(e, node.type)}
            onClick={() => onNodeTypeSelect?.(node.type)}
          >
            <div className="flex items-center gap-2">
              <span className="text-2xl">{node.icon}</span>
              <div className="flex-1">
                <div className="font-medium text-gray-900">{node.label}</div>
                <div className="text-xs text-gray-600">{node.description}</div>
              </div>
            </div>
          </div>
        ))}
      </div>

      {/* Agent Selection for Agent Nodes */}
      {agents.length > 0 && (
        <div className="mt-6">
          <h3 className="text-sm font-semibold mb-2 text-gray-700">
            Select Agent (for Agent Nodes)
          </h3>
          <select
            className="w-full p-2 border border-gray-300 rounded-md bg-white text-sm"
            value={selectedAgent || ''}
            onChange={(e) => setSelectedAgent(e.target.value ? Number(e.target.value) : null)}
          >
            <option value="">-- No Agent --</option>
            {agents.map((agent) => (
              <option key={agent.id} value={agent.id}>
                {agent.name}
              </option>
            ))}
          </select>
        </div>
      )}

      <div className="mt-6 p-3 bg-blue-50 rounded-md text-xs text-blue-800">
        <strong>💡 Tip:</strong> Drag and drop nodes onto the canvas to build your workflow.
      </div>
    </div>
  );
}
