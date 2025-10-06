# **6\. Unified Project Structure (Monorepo)**

/ai-workflow-builder/  
|-- /apps/  
|   |-- /frontend/         \# React SPA (Vite)  
|   |   |-- /src/  
|   |   |   |-- /components/ \# UI components  
|   |   |   |-- /features/   \# Feature-sliced logic (e.g., editor, visualizer)  
|   |   |   |-- /hooks/  
|   |   |   |-- /services/   \# API client  
|   |   |   \`-- App.tsx  
|   |   \`-- package.json  
|   \`-- /backend/          \# FastAPI Server  
|       |-- /app/  
|       |   |-- /api/        \# API routers  
|       |   |-- /core/       \# Core logic (NLP processing, code gen)  
|       |   |-- /models/     \# Database models (e.g., using SQLModel)  
|       |   |-- /services/   \# Services (e.g., execution\_service)  
|       |   \`-- main.py  
|       |-- Dockerfile  
|       \`-- requirements.txt  
|-- /packages/  
|   |-- /shared/           \# Shared TypeScript types and constants  
|   \`-- /ui/               \# Shared React components (from Shadcn/UI)  
|-- /execution-engine/  
|   |-- Dockerfile         \# Dockerfile for the secure sandbox  
|   \`-- runner.py          \# Script to execute workflow code inside the sandbox  
|-- package.json             \# Root package.json with workspace definitions  
\`-- README.md
