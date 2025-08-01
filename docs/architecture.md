# Architecture Guide

## Overview

The Project Manager AI Assistant uses a modern, scalable architecture with LangGraph for intelligent workflow orchestration and a flexible plugin system.

## System Architecture

```
Frontend (Streamlit) ←→ Backend (FastAPI) ←→ LangGraph Workflow ←→ Plugins
```

## Core Components

### 1. Frontend Layer (Streamlit)
- **Location**: `streamlit_app/`
- **Purpose**: User interface for project planning
- **Features**: Real-time updates, interactive visualizations, form handling

### 2. Backend Layer (FastAPI)
- **Location**: `app/`
- **Purpose**: RESTful API and business logic
- **Components**: Routes, services, models, middleware

### 3. LangGraph Workflow Engine
- **Location**: `app/agent/`
- **Purpose**: AI-powered project planning orchestration
- **Nodes**: Task extraction, dependency analysis, resource allocation, risk assessment

### 4. Plugin System
- **Location**: `app/plugins/`
- **Purpose**: Extensible integrations (Jira, Slack, etc.)

## Data Flow

1. **User Input**: Project description and team info
2. **API Processing**: Validation and request handling
3. **Workflow Execution**: LangGraph orchestrates AI analysis
4. **Result Generation**: Comprehensive project plan
5. **Response**: Return plan to frontend

## Data Models

### Core Models
```python
class Project(BaseModel):
    id: str
    name: str
    description: str
    team_members: List[TeamMember]
    constraints: ProjectConstraints

class Task(BaseModel):
    id: str
    name: str
    description: str
    estimated_hours: float
    assigned_to: str
    dependencies: List[str]
```

## Security & Performance

- **Authentication**: API key and session-based auth
- **Caching**: Redis for expensive operations
- **Rate Limiting**: Prevent API abuse
- **Input Validation**: Pydantic models for data validation

## Deployment

### Development
- Frontend: `http://localhost:8501`
- Backend: `http://localhost:8000`

### Production
- Load balancer → Application servers → Database cluster
- CDN for static assets
- Redis cache cluster

## Monitoring

- **Logging**: Structured logging with structlog
- **Metrics**: Request latency, error rates, resource usage
- **Health Checks**: `/health` endpoint for monitoring

## Development Guidelines

### Adding Features
1. Create feature branch
2. Implement in appropriate service
3. Add API endpoints if needed
4. Update frontend
5. Write tests
6. Update documentation

### Plugin Development
1. Create plugin directory in `app/plugins/`
2. Implement BasePlugin interface
3. Add configuration and tests
4. Update plugin registry

## Troubleshooting

### Common Issues
- **High Memory**: Check LangGraph workflows and Redis usage
- **Slow Response**: Review database queries and caching
- **Workflow Failures**: Check OpenAI API limits and error handling

### Debug Tools
```python
# Enable debug logging
import logging
logging.basicConfig(level=logging.DEBUG)

# Profile performance
import cProfile
cProfile.run('generate_project_plan(project_id)')
```

## Future Enhancements

- Multi-tenant support
- Advanced analytics
- Machine learning integration
- Real-time collaboration
- Mobile application
- Microservices architecture 