# Plugin Development Guide

## Overview

The Project Manager AI Assistant supports a flexible plugin system that allows you to extend functionality without modifying the core codebase. This guide will help you create custom plugins for various integrations.

## Plugin Architecture

### Base Plugin Interface

All plugins must implement the `BasePlugin` interface:

```python
from abc import ABC, abstractmethod
from typing import Dict, Any

class BasePlugin(ABC):
    """Base class for all plugins."""
    
    name: str
    version: str
    description: str
    
    @abstractmethod
    def initialize(self, config: Dict[str, Any]) -> None:
        """Initialize the plugin with configuration."""
        pass
    
    @abstractmethod
    def execute(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Execute the plugin's main functionality."""
        pass
    
    def validate_config(self, config: Dict[str, Any]) -> bool:
        """Validate plugin configuration."""
        return True
    
    def cleanup(self) -> None:
        """Clean up plugin resources."""
        pass
```

## Creating a New Plugin

### 1. Plugin Directory Structure

Create your plugin in the `app/plugins/` directory:

```
app/plugins/your_plugin/
├── __init__.py
├── plugin.py          # Main plugin implementation
├── config.py          # Configuration schema
├── models.py          # Data models (optional)
├── utils.py           # Utility functions (optional)
└── tests/
    ├── __init__.py
    └── test_plugin.py  # Plugin tests
```

### 2. Implement the Plugin

**plugin.py**
```python
from typing import Dict, Any
from app.plugins.base import BasePlugin
import requests

class JiraPlugin(BasePlugin):
    """Plugin for Jira integration."""
    
    name = "jira"
    version = "1.0.0"
    description = "Export project plans to Jira"
    
    def __init__(self):
        self.jira_url = None
        self.auth_token = None
    
    def initialize(self, config: Dict[str, Any]) -> None:
        """Initialize Jira connection."""
        self.jira_url = config.get("jira_url")
        self.auth_token = config.get("auth_token")
        
        if not self.jira_url or not self.auth_token:
            raise ValueError("Jira URL and auth token are required")
    
    def execute(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Export project plan to Jira."""
        project_plan = data.get("project_plan")
        if not project_plan:
            raise ValueError("Project plan is required")
        
        # Create Jira project
        project_data = self._create_jira_project(project_plan)
        
        # Create tasks as Jira issues
        issues = []
        for task in project_plan.get("tasks", []):
            issue = self._create_jira_issue(task, project_data["key"])
            issues.append(issue)
        
        return {
            "status": "success",
            "project": project_data,
            "issues": issues
        }
    
    def _create_jira_project(self, project_plan: Dict[str, Any]) -> Dict[str, Any]:
        """Create a new Jira project."""
        headers = {
            "Authorization": f"Bearer {self.auth_token}",
            "Content-Type": "application/json"
        }
        
        project_data = {
            "key": project_plan.get("name", "").upper()[:10],
            "name": project_plan.get("name"),
            "description": project_plan.get("description"),
            "projectTypeKey": "software",
            "leadAccountId": "your-account-id"
        }
        
        response = requests.post(
            f"{self.jira_url}/rest/api/3/project",
            json=project_data,
            headers=headers
        )
        
        if response.status_code == 201:
            return response.json()
        else:
            raise Exception(f"Failed to create Jira project: {response.text}")
    
    def _create_jira_issue(self, task: Dict[str, Any], project_key: str) -> Dict[str, Any]:
        """Create a Jira issue for a task."""
        headers = {
            "Authorization": f"Bearer {self.auth_token}",
            "Content-Type": "application/json"
        }
        
        issue_data = {
            "fields": {
                "project": {"key": project_key},
                "summary": task.get("name"),
                "description": task.get("description"),
                "issuetype": {"name": "Task"},
                "assignee": {"displayName": task.get("assigned_to")},
                "priority": {"name": "Medium"}
            }
        }
        
        response = requests.post(
            f"{self.jira_url}/rest/api/3/issue",
            json=issue_data,
            headers=headers
        )
        
        if response.status_code == 201:
            return response.json()
        else:
            raise Exception(f"Failed to create Jira issue: {response.text}")
```

### 3. Configuration Schema

**config.py**
```python
from pydantic import BaseModel, HttpUrl
from typing import Optional

class JiraConfig(BaseModel):
    """Configuration schema for Jira plugin."""
    
    jira_url: HttpUrl
    auth_token: str
    project_template: Optional[str] = "software"
    default_assignee: Optional[str] = None
    
    class Config:
        schema_extra = {
            "example": {
                "jira_url": "https://your-domain.atlassian.net",
                "auth_token": "your-api-token",
                "project_template": "software",
                "default_assignee": "john.doe@company.com"
            }
        }
```

### 4. Register the Plugin

**__init__.py**
```python
from .plugin import JiraPlugin
from .config import JiraConfig

__all__ = ["JiraPlugin", "JiraConfig"]
```

Update the main plugin registry in `app/plugins/__init__.py`:

```python
from .jira import JiraPlugin
from .slack import SlackPlugin
from .export import PDFExportPlugin

AVAILABLE_PLUGINS = {
    "jira": JiraPlugin,
    "slack": SlackPlugin,
    "pdf_export": PDFExportPlugin,
}
```

## Testing Your Plugin

### Unit Tests

**tests/test_plugin.py**
```python
import pytest
from unittest.mock import Mock, patch
from app.plugins.jira.plugin import JiraPlugin

class TestJiraPlugin:
    
    @pytest.fixture
    def jira_plugin(self):
        plugin = JiraPlugin()
        config = {
            "jira_url": "https://test.atlassian.net",
            "auth_token": "test-token"
        }
        plugin.initialize(config)
        return plugin
    
    @pytest.fixture
    def sample_project_plan(self):
        return {
            "name": "Test Project",
            "description": "A test project",
            "tasks": [
                {
                    "name": "Task 1",
                    "description": "First task",
                    "assigned_to": "John Doe"
                }
            ]
        }
    
    def test_initialize_valid_config(self):
        plugin = JiraPlugin()
        config = {
            "jira_url": "https://test.atlassian.net",
            "auth_token": "test-token"
        }
        
        plugin.initialize(config)
        
        assert plugin.jira_url == "https://test.atlassian.net"
        assert plugin.auth_token == "test-token"
    
    def test_initialize_missing_config(self):
        plugin = JiraPlugin()
        config = {"jira_url": "https://test.atlassian.net"}
        
        with pytest.raises(ValueError, match="auth token are required"):
            plugin.initialize(config)
    
    @patch('requests.post')
    def test_execute_success(self, mock_post, jira_plugin, sample_project_plan):
        # Mock successful responses
        mock_post.side_effect = [
            Mock(status_code=201, json=lambda: {"key": "TEST"}),  # Project creation
            Mock(status_code=201, json=lambda: {"id": "10001"})   # Issue creation
        ]
        
        data = {"project_plan": sample_project_plan}
        result = jira_plugin.execute(data)
        
        assert result["status"] == "success"
        assert result["project"]["key"] == "TEST"
        assert len(result["issues"]) == 1
```

### Integration Tests

```python
@pytest.mark.integration
def test_jira_integration():
    """Test actual Jira integration (requires valid credentials)."""
    plugin = JiraPlugin()
    config = {
        "jira_url": os.getenv("JIRA_URL"),
        "auth_token": os.getenv("JIRA_TOKEN")
    }
    
    if not all(config.values()):
        pytest.skip("Jira credentials not provided")
    
    plugin.initialize(config)
    
    # Test with real data
    project_plan = {
        "name": "Integration Test",
        "description": "Testing plugin integration",
        "tasks": [{"name": "Test Task", "description": "Test", "assigned_to": "Test User"}]
    }
    
    result = plugin.execute({"project_plan": project_plan})
    assert result["status"] == "success"
```

## Plugin Configuration

### Environment Variables

Add plugin-specific environment variables to `.env`:

```bash
# Jira Plugin
JIRA_URL=https://your-domain.atlassian.net
JIRA_AUTH_TOKEN=your-api-token

# Slack Plugin
SLACK_BOT_TOKEN=xoxb-your-bot-token
SLACK_CHANNEL=#project-updates
```

### Configuration File

Create a plugin configuration file `config/plugins.yml`:

```yaml
plugins:
  jira:
    enabled: true
    config:
      jira_url: "${JIRA_URL}"
      auth_token: "${JIRA_AUTH_TOKEN}"
      project_template: "software"
  
  slack:
    enabled: true
    config:
      bot_token: "${SLACK_BOT_TOKEN}"
      channel: "${SLACK_CHANNEL}"
      
  pdf_export:
    enabled: true
    config:
      template_path: "templates/project_plan.html"
      output_dir: "exports/"
```

## Using Plugins in the Application

### Plugin Manager

```python
from typing import Dict, Any, List
from app.plugins import AVAILABLE_PLUGINS

class PluginManager:
    """Manages plugin lifecycle and execution."""
    
    def __init__(self):
        self.plugins = {}
        self.enabled_plugins = []
    
    def load_plugins(self, plugin_config: Dict[str, Any]):
        """Load and initialize enabled plugins."""
        for plugin_name, config in plugin_config.items():
            if config.get("enabled", False):
                plugin_class = AVAILABLE_PLUGINS.get(plugin_name)
                if plugin_class:
                    plugin = plugin_class()
                    plugin.initialize(config.get("config", {}))
                    self.plugins[plugin_name] = plugin
                    self.enabled_plugins.append(plugin_name)
    
    def execute_plugin(self, plugin_name: str, data: Dict[str, Any]) -> Dict[str, Any]:
        """Execute a specific plugin."""
        if plugin_name not in self.plugins:
            raise ValueError(f"Plugin {plugin_name} not loaded")
        
        return self.plugins[plugin_name].execute(data)
    
    def execute_all(self, data: Dict[str, Any]) -> Dict[str, List[Dict[str, Any]]]:
        """Execute all enabled plugins."""
        results = {}
        for plugin_name in self.enabled_plugins:
            try:
                result = self.execute_plugin(plugin_name, data)
                results[plugin_name] = result
            except Exception as e:
                results[plugin_name] = {"status": "error", "error": str(e)}
        
        return results
```

### API Integration

Add plugin endpoints to your FastAPI application:

```python
from fastapi import APIRouter, HTTPException
from app.services.plugin_manager import PluginManager

router = APIRouter(prefix="/plugins", tags=["plugins"])
plugin_manager = PluginManager()

@router.post("/{plugin_name}/execute")
async def execute_plugin(plugin_name: str, data: dict):
    """Execute a specific plugin."""
    try:
        result = plugin_manager.execute_plugin(plugin_name, data)
        return result
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/")
async def list_plugins():
    """List all available plugins."""
    return {
        "available": list(AVAILABLE_PLUGINS.keys()),
        "enabled": plugin_manager.enabled_plugins
    }
```

## Best Practices

### Error Handling

```python
def execute(self, data: Dict[str, Any]) -> Dict[str, Any]:
    try:
        # Plugin logic here
        result = self._do_work(data)
        return {"status": "success", "data": result}
    except ValidationError as e:
        return {"status": "error", "error": f"Validation failed: {e}"}
    except ConnectionError as e:
        return {"status": "error", "error": f"Connection failed: {e}"}
    except Exception as e:
        return {"status": "error", "error": f"Unexpected error: {e}"}
```

### Logging

```python
import logging

logger = logging.getLogger(__name__)

class MyPlugin(BasePlugin):
    def execute(self, data: Dict[str, Any]) -> Dict[str, Any]:
        logger.info(f"Executing {self.name} plugin")
        
        try:
            result = self._process_data(data)
            logger.info(f"Plugin {self.name} completed successfully")
            return result
        except Exception as e:
            logger.error(f"Plugin {self.name} failed: {e}")
            raise
```

### Configuration Validation

```python
from pydantic import BaseModel, validator

class PluginConfig(BaseModel):
    api_url: str
    api_key: str
    timeout: int = 30
    
    @validator('api_url')
    def validate_url(cls, v):
        if not v.startswith(('http://', 'https://')):
            raise ValueError('API URL must start with http:// or https://')
        return v
    
    @validator('timeout')
    def validate_timeout(cls, v):
        if v <= 0:
            raise ValueError('Timeout must be positive')
        return v
```

## Example Plugins

### Slack Notification Plugin

```python
class SlackPlugin(BasePlugin):
    name = "slack"
    version = "1.0.0"
    description = "Send project updates to Slack"
    
    def execute(self, data: Dict[str, Any]) -> Dict[str, Any]:
        from slack_sdk import WebClient
        
        client = WebClient(token=self.bot_token)
        
        message = self._format_message(data["project_plan"])
        
        response = client.chat_postMessage(
            channel=self.channel,
            text=message
        )
        
        return {"status": "success", "message_ts": response["ts"]}
```

### PDF Export Plugin

```python
class PDFExportPlugin(BasePlugin):
    name = "pdf_export"
    version = "1.0.0"
    description = "Export project plans to PDF"
    
    def execute(self, data: Dict[str, Any]) -> Dict[str, Any]:
        from weasyprint import HTML, CSS
        
        html_content = self._render_template(data["project_plan"])
        
        pdf_file = f"exports/project_plan_{data['project_id']}.pdf"
        HTML(string=html_content).write_pdf(pdf_file)
        
        return {"status": "success", "file_path": pdf_file}
```

## Troubleshooting

### Common Issues

1. **Plugin not loading**: Check plugin registration and imports
2. **Configuration errors**: Validate configuration schema
3. **Runtime errors**: Check logs and error handling
4. **Performance issues**: Profile plugin execution

### Debugging

```python
import logging
logging.basicConfig(level=logging.DEBUG)

# Enable plugin debugging
logger = logging.getLogger('app.plugins')
logger.setLevel(logging.DEBUG)
```

---

*For more examples and advanced plugin development techniques, check the existing plugins in the `app/plugins/` directory.*