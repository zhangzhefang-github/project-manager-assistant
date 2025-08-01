# API Reference

## Overview

The Project Manager AI Assistant provides a RESTful API for programmatic access to project planning functionality. This document describes all available endpoints, request/response formats, and authentication methods.

## Base URL

```
http://localhost:8000
```

## Authentication

Currently, the API uses API key authentication. Include your API key in the request headers:

```
Authorization: Bearer YOUR_API_KEY
```

## Endpoints

### 1. Health Check

**GET** `/health`

Check if the API is running.

**Response:**
```json
{
  "status": "healthy",
  "timestamp": "2024-01-15T10:30:00Z"
}
```

### 2. Generate Project Plan

**POST** `/api/v1/projects/generate`

Generate a comprehensive project plan from a project description and team information.

**Request Body:**
```json
{
  "project_description": "Develop a new e-commerce website for a local bookstore...",
  "team_members": [
    {
      "name": "John Smith",
      "role": "Senior Full-Stack Developer",
      "skills": ["React", "Node.js", "Python", "AWS"],
      "availability_hours": 40,
      "experience_years": 8
    }
  ],
  "constraints": {
    "timeline_months": 3,
    "budget": 50000,
    "team_size": 5
  }
}
```

**Response:**
```json
{
  "project_id": "proj_123456",
  "plan": {
    "tasks": [
      {
        "id": "task_001",
        "name": "Project Setup",
        "description": "Initialize project repository and development environment",
        "estimated_hours": 8,
        "assigned_to": "John Smith",
        "dependencies": [],
        "start_date": "2024-01-15",
        "end_date": "2024-01-16"
      }
    ],
    "dependencies": [
      {
        "from_task": "task_001",
        "to_task": "task_002",
        "type": "finish_to_start"
      }
    ],
    "timeline": {
      "start_date": "2024-01-15",
      "end_date": "2024-04-15",
      "critical_path": ["task_001", "task_002", "task_005"]
    },
    "risks": [
      {
        "id": "risk_001",
        "description": "Team member availability during holidays",
        "severity": "medium",
        "mitigation": "Plan buffer time and cross-train team members"
      }
    ]
  }
}
```

### 3. Get Project Plan

**GET** `/api/v1/projects/{project_id}`

Retrieve a previously generated project plan.

**Response:**
```json
{
  "project_id": "proj_123456",
  "created_at": "2024-01-15T10:30:00Z",
  "plan": {
    // Same structure as generate response
  }
}
```

### 4. Update Project Plan

**PUT** `/api/v1/projects/{project_id}`

Update an existing project plan with modifications.

**Request Body:**
```json
{
  "modifications": {
    "task_updates": [
      {
        "task_id": "task_001",
        "estimated_hours": 12,
        "assigned_to": "Sarah Johnson"
      }
    ],
    "new_tasks": [
      {
        "name": "Additional Testing",
        "description": "Comprehensive testing phase",
        "estimated_hours": 16,
        "assigned_to": "John Smith",
        "dependencies": ["task_005"]
      }
    ]
  }
}
```

### 5. Export Project Plan

**GET** `/api/v1/projects/{project_id}/export`

Export project plan in various formats.

**Query Parameters:**
- `format`: `pdf`, `excel`, `jira`, `msproject`

**Response:**
- For PDF/Excel: File download
- For Jira/MS Project: JSON configuration

### 6. List Projects

**GET** `/api/v1/projects`

List all projects for the authenticated user.

**Query Parameters:**
- `page`: Page number (default: 1)
- `limit`: Items per page (default: 10)
- `status`: Filter by status

**Response:**
```json
{
  "projects": [
    {
      "project_id": "proj_123456",
      "name": "E-commerce Website",
      "created_at": "2024-01-15T10:30:00Z",
      "status": "active"
    }
  ],
  "pagination": {
    "page": 1,
    "limit": 10,
    "total": 25,
    "pages": 3
  }
}
```

### 7. Delete Project

**DELETE** `/api/v1/projects/{project_id}`

Delete a project and all associated data.

**Response:**
```json
{
  "message": "Project deleted successfully"
}
```

## Error Responses

All endpoints may return the following error responses:

### 400 Bad Request
```json
{
  "error": "validation_error",
  "message": "Invalid request data",
  "details": {
    "field": "project_description",
    "issue": "Required field is missing"
  }
}
```

### 401 Unauthorized
```json
{
  "error": "authentication_error",
  "message": "Invalid or missing API key"
}
```

### 404 Not Found
```json
{
  "error": "not_found",
  "message": "Project not found"
}
```

### 500 Internal Server Error
```json
{
  "error": "internal_error",
  "message": "An unexpected error occurred"
}
```

## Rate Limiting

API requests are limited to:
- 100 requests per minute per API key
- 1000 requests per hour per API key

Rate limit headers are included in responses:
```
X-RateLimit-Limit: 100
X-RateLimit-Remaining: 95
X-RateLimit-Reset: 1642234567
```

## Webhooks

Configure webhooks to receive real-time updates when project plans are modified.

### Register Webhook

**POST** `/api/v1/webhooks`

**Request Body:**
```json
{
  "url": "https://your-app.com/webhook",
  "events": ["project.created", "project.updated"],
  "secret": "your-webhook-secret"
}
```

### Webhook Payload

```json
{
  "event": "project.updated",
  "timestamp": "2024-01-15T10:30:00Z",
  "data": {
    "project_id": "proj_123456",
    "changes": {
      "tasks_modified": 3,
      "timeline_updated": true
    }
  }
}
```

## SDKs and Libraries

### Python SDK

```python
from project_manager_ai import ProjectManagerAI

client = ProjectManagerAI(api_key="your-api-key")

# Generate project plan
plan = client.generate_plan(
    project_description="Develop a new website...",
    team_members=[...],
    constraints={...}
)

# Get project plan
plan = client.get_project("proj_123456")
```

### JavaScript SDK

```javascript
import { ProjectManagerAI } from 'project-manager-ai';

const client = new ProjectManagerAI('your-api-key');

// Generate project plan
const plan = await client.generatePlan({
  projectDescription: 'Develop a new website...',
  teamMembers: [...],
  constraints: {...}
});
```

## Examples

### Complete Project Generation

```bash
curl -X POST http://localhost:8000/api/v1/projects/generate \
  -H "Authorization: Bearer YOUR_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "project_description": "Build a mobile app for food delivery",
    "team_members": [
      {
        "name": "Alice Johnson",
        "role": "Mobile Developer",
        "skills": ["React Native", "JavaScript", "iOS", "Android"],
        "availability_hours": 40,
        "experience_years": 5
      }
    ],
    "constraints": {
      "timeline_months": 6,
      "budget": 100000,
      "team_size": 8
    }
  }'
```

### Export to Jira

```bash
curl -X GET "http://localhost:8000/api/v1/projects/proj_123456/export?format=jira" \
  -H "Authorization: Bearer YOUR_API_KEY"
```

## Support

For API support:
- Email: api-support@projectmanager-ai.com
- Documentation: https://docs.projectmanager-ai.com
- GitHub Issues: https://github.com/your-username/project-manager-assistant/issues 