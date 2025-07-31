import time
from loguru import logger
from langchain_openai.chat_models import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate

from app.agent.state import AgentState
from app.schemas.plan import TaskList
from app.core.config import get_settings
from app.prompts.loader import get_prompt


def task_generation_node(state: AgentState) -> dict:
    """
    使用中文化prompt从项目描述生成任务列表
    包含实时进度追踪
    """
    # === 进度追踪：节点开始 ===
    current_time = time.time()
    
    # 初始化总开始时间（如果是第一个节点）
    if not state.get("total_start_time"):
        state["total_start_time"] = current_time
    
    # 更新当前节点状态
    state["current_node"] = "task_generation"
    state["node_start_time"] = current_time
    state["overall_status"] = "processing"
    
    # 初始化节点进度
    if "node_progress" not in state:
        state["node_progress"] = {}
    
    state["node_progress"]["task_generation"] = {
        "status": "started",
        "start_time": current_time,
        "description": "🧠 分析项目需求，智能提取任务清单",
        "details": "正在解析项目描述，识别核心功能模块..."
    }
    
    # === 实时更新任务队列状态 ===
    if state.get("job_id"):
        try:
            from app.services.task_queue import update_job_progress
            update_job_progress(state["job_id"], state)
        except ImportError:
            pass
    
    logger.info(f"📋 开始任务生成，项目: {state['project_description'][:100]}...")
    
    try:
        # === 实际LLM处理 ===
        settings = get_settings()
        llm = ChatOpenAI(
            model=settings.OPENAI_MODEL,
            api_key=settings.OPENAI_API_KEY,
            base_url=settings.OPENAI_API_BASE,
            temperature=0.1
        )
        
        # 更新进度：开始LLM调用
        state["node_progress"]["task_generation"]["details"] = "正在调用AI模型进行任务分解..."
        if state.get("job_id"):
            try:
                from app.services.task_queue import update_job_progress
                update_job_progress(state["job_id"], state)
            except ImportError:
                pass
        
        # 从 state 中获取团队信息，如果不存在则提供默认值
        team_info = state.get("team", "未提供团队信息")
        
        # 使用中文化的prompt模板，并传入团队信息
        chinese_prompt = get_prompt(
            "task_generation", 
            description=state["project_description"],
            team=str(team_info) # 确保team信息是字符串格式
        )
        
        # 构建结构化输出的prompt - 修复ChatPromptTemplate变量问题
        full_prompt = f"""{chinese_prompt}

请按照以下JSON格式返回结果：
{{{{
  "tasks": [
    {{{{
      "id": "task-1",
      "task_name": "任务名称（简体中文）",
      "task_description": "详细任务描述（简体中文）",
      "estimated_day": 天数数字
    }}}}
  ]
}}}}

注意：
- 所有任务名称和描述必须使用简体中文
- id字段使用简单的字符串标识符如 'task-1', 'task-2' 等
- estimated_day必须是数字"""
        
        # 直接使用完整的prompt字符串，不需要ChatPromptTemplate的变量替换
        from langchain_core.messages import HumanMessage
        messages = [HumanMessage(content=full_prompt)]
        
        # 使用同步调用
        result = llm.invoke(messages)
        
        # 更新进度：解析结果
        state["node_progress"]["task_generation"]["details"] = "正在解析AI生成的任务列表..."
        if state.get("job_id"):
            try:
                from app.services.task_queue import update_job_progress
                update_job_progress(state["job_id"], state)
            except ImportError:
                pass
        
        try:
            import json
            import re
            
            # 提取JSON内容
            content = result.content
            json_match = re.search(r'\{.*\}', content, re.DOTALL)
            if json_match:
                json_str = json_match.group()
                parsed_result = json.loads(json_str)
                
                if "tasks" in parsed_result:
                    # 转换为适配器模式期望的格式
                    from app.services.model_adapter import ModelAdapter
                    from app.schemas.simple import SimpleTaskList
                    
                    # 创建SimpleTaskList对象
                    simple_task_list = SimpleTaskList(tasks=parsed_result["tasks"])
                    
                    # 使用正确的方法名进行转换
                    tasks, id_mapping = ModelAdapter.simple_to_full_task_list(simple_task_list)
                    
                    # === 进度追踪：节点完成 ===
                    state["node_progress"]["task_generation"]["status"] = "completed"
                    state["node_progress"]["task_generation"]["end_time"] = time.time()
                    state["node_progress"]["task_generation"]["details"] = f"✅ 成功提取 {len(tasks.tasks)} 个任务"
                    
                    if state.get("job_id"):
                        try:
                            from app.services.task_queue import update_job_progress
                            update_job_progress(state["job_id"], state)
                        except ImportError:
                            pass
                    
                    logger.info(f"✅ 成功生成 {len(tasks.tasks)} 个任务")
                    return {"tasks": tasks, "id_mapping": id_mapping}
                else:
                    raise ValueError("AI响应中没有找到tasks字段")
            else:
                raise ValueError("AI响应中没有找到有效的JSON格式")
                
        except (json.JSONDecodeError, KeyError, ValueError) as e:
            logger.error(f"❌ 解析AI响应失败: {e}")
            logger.error(f"原始响应: {result.content}")
            
            # 生成fallback任务列表
            fallback_tasks = TaskList(tasks=[
                {
                    "id": "task-1",
                    "task_name": "项目规划与需求分析",
                    "task_description": "分析项目需求，制定详细的项目计划和技术方案",
                    "estimated_day": 3
                },
                {
                    "id": "task-2", 
                    "task_name": "系统架构设计",
                    "task_description": "设计系统整体架构，包括前端、后端和数据库设计",
                    "estimated_day": 5
                },
                {
                    "id": "task-3",
                    "task_name": "核心功能开发",
                    "task_description": "开发项目的主要功能模块",
                    "estimated_day": 10
                },
                {
                    "id": "task-4",
                    "task_name": "测试与质量保证",
                    "task_description": "进行系统测试，确保功能正常运行",
                    "estimated_day": 4
                },
                {
                    "id": "task-5",
                    "task_name": "部署与上线",
                    "task_description": "将系统部署到生产环境并进行上线准备",
                    "estimated_day": 2
                }
            ])
            
            state["node_progress"]["task_generation"]["status"] = "completed"
            state["node_progress"]["task_generation"]["end_time"] = time.time()
            state["node_progress"]["task_generation"]["details"] = f"⚠️ 使用备用方案生成 {len(fallback_tasks.tasks)} 个任务"
            
            logger.warning("使用备用任务列表")
            return {"tasks": fallback_tasks}
            
    except Exception as e:
        # === 进度追踪：节点失败 ===
        state["node_progress"]["task_generation"]["status"] = "failed"
        state["node_progress"]["task_generation"]["end_time"] = time.time()
        state["node_progress"]["task_generation"]["details"] = f"❌ 任务生成失败: {str(e)}"
        
        if state.get("job_id"):
            try:
                from app.services.task_queue import update_job_progress
                update_job_progress(state["job_id"], state)
            except ImportError:
                pass
        
        logger.error(f"❌ 任务生成节点执行失败: {e}")
        raise 