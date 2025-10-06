# Agent Workflow Builder

A comprehensive full-stack Python application for creating and managing AI agent workflows using the Microsoft Agent Framework. This application provides a modern, intuitive visual interface for building complex multi-agent workflows with drag-and-drop functionality.

## 🚀 Features

### Core Capabilities
- **Visual Workflow Builder**: Drag-and-drop interface for creating complex agent workflows
- **Microsoft Agent Framework Integration**: Full support for the latest Agent Framework Python SDK
- **MCP Tool Integration**: Built-in support for Microsoft Learn MCP Server and Context7 MCP tools
- **Multi-Agent Orchestration**: Support for sequential, concurrent, handoff, and Magentic patterns
- **Human-in-the-Loop**: Interactive workflows with approval gates and user input
- **Real-time Execution**: Stream workflow execution with live updates
- **Workflow Visualization**: Export workflows as SVG, PNG, or Mermaid diagrams

### Agent Patterns Supported
- **Sequential Orchestration**: Step-by-step agent execution
- **Concurrent Orchestration**: Parallel agent processing
- **Handoff Orchestration**: Dynamic agent-to-agent handoffs
- **Magentic Orchestration**: Complex multi-agent collaboration
- **Custom Executors**: Build your own workflow components

### Technical Features
- **Type-Safe Architecture**: Strong typing throughout the application
- **Checkpointing & Resume**: Save and restore workflow state
- **Observability**: Built-in monitoring and logging
- **Extensible Design**: Easy to add new agents and tools
- **Modern UI/UX**: Responsive design with dark/light mode support

## 🏗️ Architecture

### Backend (Python)
- **FastAPI**: Modern, fast web framework
- **Microsoft Agent Framework**: AI agent orchestration
- **Pydantic**: Data validation and settings management
- **SQLModel**: Database ORM with type safety
- **WebSocket**: Real-time communication

### Frontend (React + TypeScript)
- **React 18**: Modern React with hooks and concurrent features
- **TypeScript**: Type-safe JavaScript development
- **React Flow**: Visual workflow editor with drag-and-drop
- **Tailwind CSS**: Utility-first CSS framework
- **Vite**: Fast build tool and development server
- **Zustand**: Lightweight state management

### Integration Layer
- **MCP Protocol**: Model Context Protocol for tool integration
- **WebSocket API**: Real-time workflow execution
- **REST API**: Standard CRUD operations
- **Event Streaming**: Live workflow updates

## 📋 Prerequisites

- Python 3.11+
- Node.js 18+
- npm or yarn
- Git

## 🛠️ Installation

### 1. Clone the Repository
```bash
git clone <repository-url>
cd agent-workflow-builder
```

### 2. Backend Setup
```bash
cd backend

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Set up environment variables
cp .env.example .env
# Edit .env with your configuration
```

### 3. Frontend Setup
```bash
cd frontend

# Install dependencies
npm install

# Set up environment variables
cp .env.example .env.local
# Edit .env.local with your configuration
```

## 🚀 Quick Start

### 1. Start the Backend
```bash
cd backend
source venv/bin/activate
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### 2. Start the Frontend
```bash
cd frontend
npm run dev
```

### 3. Open the Application
Navigate to `http://localhost:3000` in your browser.

## 📖 Usage Guide

### Creating Your First Workflow

1. **Open the Workflow Builder**: Click "New Workflow" on the dashboard
2. **Add Agents**: Drag agent nodes from the sidebar to the canvas
3. **Configure Agents**: Click on nodes to set instructions, tools, and parameters
4. **Connect Agents**: Drag connections between nodes to define the flow
5. **Add Logic**: Use conditional edges and custom executors as needed
6. **Test & Execute**: Run your workflow and monitor execution in real-time

### Supported Agent Types

- **Chat Agents**: General-purpose conversational agents
- **Specialist Agents**: Domain-specific expert agents
- **Tool Agents**: Agents with specific tool capabilities
- **Custom Agents**: Build your own agent types

### MCP Tool Integration

The application comes with pre-configured MCP tools:

- **Microsoft Learn MCP**: Access Microsoft documentation and learning resources
- **Context7 MCP**: Advanced context management and retrieval
- **Custom MCP Tools**: Add your own MCP servers

## 🔧 Configuration

### Environment Variables

#### Backend (.env)
```env
# API Configuration
API_HOST=0.0.0.0
API_PORT=8000
DEBUG=true

# Database
DATABASE_URL=sqlite:///./agent_workflows.db

# Azure OpenAI (optional)
AZURE_OPENAI_ENDPOINT=your-endpoint
AZURE_OPENAI_API_KEY=your-key
AZURE_OPENAI_DEPLOYMENT_NAME=gpt-4

# OpenAI (optional)
OPENAI_API_KEY=your-key

# MCP Configuration
MICROSOFT_LEARN_MCP_URL=https://learn.microsoft.com/api/mcp
CONTEXT7_MCP_URL=your-context7-endpoint
```

#### Frontend (.env.local)
```env
VITE_API_BASE_URL=http://localhost:8000
VITE_WS_BASE_URL=ws://localhost:8000
VITE_APP_TITLE=Agent Workflow Builder
```

## 🧪 Testing

### Backend Tests
```bash
cd backend
pytest tests/ -v
```

### Frontend Tests
```bash
cd frontend
npm test
```

### Integration Tests
```bash
# Run the test suite
python test_runner.py
```

## 📚 API Documentation

Once the backend is running, visit:
- **Interactive API Docs**: http://localhost:8000/docs
- **ReDoc Documentation**: http://localhost:8000/redoc

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- **Microsoft Agent Framework Team**: For the excellent Agent Framework
- **React Flow Team**: For the powerful visual workflow library
- **FastAPI Team**: For the modern Python web framework
- **Open Source Community**: For the amazing tools and libraries

## 📞 Support

- **Documentation**: [Link to docs]
- **Issues**: [GitHub Issues]
- **Discussions**: [GitHub Discussions]
- **Email**: support@example.com

## 🗺️ Roadmap

- [ ] Advanced workflow templates
- [ ] Workflow marketplace
- [ ] Multi-tenant support
- [ ] Advanced analytics and monitoring
- [ ] Mobile-responsive design improvements
- [ ] Plugin system for custom integrations

---

**Built with ❤️ using Microsoft Agent Framework**