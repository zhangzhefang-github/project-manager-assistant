import streamlit as st
import pandas as pd
import requests
import time
import plotly.express as px
from datetime import datetime, timedelta
import streamlit.components.v1 as components
import json
import uuid

# --- 核心配置与示例数据 ---
# 动态获取当前主机地址，适应不同网络环境
import os
def get_api_url():
    # 尝试从环境变量获取
    if 'API_HOST' in os.environ:
        return f"http://{os.environ['API_HOST']}:8000"
    
    # 自动检测当前访问的主机
    import streamlit as st
    try:
        # 获取当前页面的host
        if hasattr(st, 'session_state') and hasattr(st.session_state, 'host'):
            return f"http://{st.session_state.host}:8000"
    except:
        pass
    
    # 默认回退到本地地址
    return "http://127.0.0.1:8000"

API_URL = get_api_url()
PAGE_TITLE = "AI 项目管理助手"
PAGE_ICON = "🤖"

# Base64 encoded image to avoid external network requests
LANGCHAIN_ICON_B64 = "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"

# 🎯 智能执行阶段映射 (基于时间推断)
EXECUTION_PHASES = [
    {"name": "🧠 需求理解", "duration": 3, "progress": 10, "description": "AI分析项目需求，理解业务逻辑", "details": "• 解析项目描述\n• 识别核心功能\n• 分析技术需求"},
    {"name": "📋 任务分解", "duration": 8, "progress": 25, "description": "基于需求生成详细任务清单", "details": "• 分解功能模块\n• 估算工作量\n• 生成任务列表"},
    {"name": "🔗 依赖分析", "duration": 5, "progress": 45, "description": "分析任务间的依赖关系", "details": "• 识别任务前置条件\n• 构建依赖图\n• 优化执行顺序"},
    {"name": "📅 智能调度", "duration": 7, "progress": 65, "description": "制定最优项目时间安排", "details": "• 优化时间线\n• 并行任务识别\n• 生成甘特图"},
    {"name": "👥 团队匹配", "duration": 6, "progress": 80, "description": "根据技能为任务分配最佳人员", "details": "• 技能匹配分析\n• 负载均衡考虑\n• 生成分配方案"},
    {"name": "⚠️ 风险评估", "duration": 4, "progress": 95, "description": "识别潜在风险并制定预案", "details": "• 风险识别\n• 评分计算\n• 生成改进建议"},
    {"name": "✨ 方案优化", "duration": 2, "progress": 100, "description": "最终优化和结果整合", "details": "• 方案验证\n• 最终调整\n• 输出完整计划"}
]

EXAMPLE_PROJECT_DESCRIPTION = """
# 项目名称：
公司内部员工餐饮预定微信小程序

# 项目目标：
为了提升员工满意度和优化后勤管理效率，计划开发一个微信小程序。员工可以通过该小程序提前预定未来一周的工作日午餐和晚餐，并进行在线支付。行政部门可以通过后台管理菜单、统计预定数量、与供应商结算。

# 核心功能：
1.  **用户端 (小程序)**:
    - 用户登录/认证 (与企业微信打通)。
    - 按周显示菜单，包含图片、价格和营养成分。
    - 用户选择餐品并加入购物车。
    - 按周一次性下单并使用微信支付。
    - 查看历史订单。
2.  **管理后台 (Web)**:
    - 菜单管理：增删改查每周的餐品。
    - 订单管理：按天、按周查看和导出预定统计报表。
    - 用户管理：管理员工信息。

# 目标用户：
公司全体员工 (~500人) 和行政部后勤人员 (2-3人)。

# 技术栈偏好（可选）：
后端希望使用Python (FastAPI)，前端无特殊要求。
""".strip()

EXAMPLE_TEAM_CSV = """name,profile
张三,"后端工程师, 5年Python和Django经验, 熟悉数据库设计和API开发"
李四,"前端工程师, 3年前端经验, 精通React和Vue, 关注用户体验"
王五,"产品经理, 6年互联网产品经验, 擅长需求分析和原型设计"
赵六,"UI/UX设计师, 4年设计经验, 精通Figma, 有完整小程序设计案例"
孙七,"测试工程师, 3年测试经验, 熟悉自动化测试框架, 如Pytest和Selenium"
""".strip()


st.set_page_config(page_title=PAGE_TITLE, page_icon=PAGE_ICON, layout="wide")

# --- 智能进度系统 ---
def get_current_phase(elapsed_time):
    """基于执行时间智能推断当前阶段"""
    cumulative_time = 0
    
    for i, phase in enumerate(EXECUTION_PHASES):
        cumulative_time += phase["duration"]
        if elapsed_time <= cumulative_time:
            # 计算当前阶段内的进度
            phase_start_time = cumulative_time - phase["duration"]
            phase_progress = min((elapsed_time - phase_start_time) / phase["duration"], 1.0)
            
            # 计算整体进度
            prev_progress = EXECUTION_PHASES[i-1]["progress"] if i > 0 else 0
            current_progress = prev_progress + (phase["progress"] - prev_progress) * phase_progress
            
            return {
                "phase": phase,
                "phase_index": i,
                "overall_progress": min(current_progress, 100),
                "phase_progress": phase_progress * 100,
                "estimated_remaining": max(0, sum(p["duration"] for p in EXECUTION_PHASES) - elapsed_time)
            }
    
    # 如果时间超出预期，返回最后阶段
    return {
        "phase": EXECUTION_PHASES[-1],
        "phase_index": len(EXECUTION_PHASES) - 1,
        "overall_progress": 100,
        "phase_progress": 100,
        "estimated_remaining": 0
    }

def render_intelligent_progress(phase_info, elapsed_time, job_id):
    """渲染智能化进度界面"""
    current_phase = phase_info["phase"]
    
    # 主标题区域
    st.markdown(f"""
    <div style='background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); padding: 20px; border-radius: 15px; color: white; margin-bottom: 20px;'>
        <h2 style='margin: 0; text-align: center;'>{current_phase["name"]}</h2>
        <p style='margin: 5px 0; text-align: center; opacity: 0.9;'>{current_phase["description"]}</p>
    </div>
    """, unsafe_allow_html=True)
    
    # 进度展示区域
    col1, col2, col3 = st.columns([2, 1, 1])
    
    with col1:
        # 主进度条
        st.progress(phase_info["overall_progress"] / 100)
        
        # 进度数据
        progress_col1, progress_col2, progress_col3 = st.columns(3)
        with progress_col1:
            st.metric("📈 总体进度", f"{phase_info['overall_progress']:.0f}%")
        with progress_col2:
            st.metric("⏱️ 已执行", f"{elapsed_time}秒")
        with progress_col3:
            remaining = phase_info["estimated_remaining"]
            st.metric("⏰ 预计剩余", f"{remaining:.0f}秒" if remaining > 0 else "即将完成")
    
    with col2:
        # 当前阶段详情
        st.markdown("**🔍 当前阶段详情**")
        st.markdown(current_phase["details"])
    
    with col3:
        # 执行状态
        st.markdown(f"""
        <div style='background-color: #f0f8ff; padding: 15px; border-radius: 10px; border-left: 4px solid #4A90E2;'>
            <h4 style='margin: 0; color: #4A90E2;'>🤖 AI 执行状态</h4>
            <p><strong>任务ID:</strong> <code>{job_id[:8]}...</code></p>
            <p><strong>执行阶段:</strong> {phase_info["phase_index"] + 1}/{len(EXECUTION_PHASES)}</p>
            <p><strong>阶段进度:</strong> {phase_info["phase_progress"]:.0f}%</p>
        </div>
        """, unsafe_allow_html=True)
    
    # 阶段时间线
    st.markdown("---")
    st.markdown("**📊 执行时间线**")
    
    timeline_cols = st.columns(len(EXECUTION_PHASES))
    for i, (phase, col) in enumerate(zip(EXECUTION_PHASES, timeline_cols)):
        with col:
            if i < phase_info["phase_index"]:
                # 已完成阶段
                st.markdown(f"""
                <div style='text-align: center; padding: 10px; background-color: #d4edda; border-radius: 8px; border: 2px solid #28a745;'>
                    <div style='font-size: 20px;'>✅</div>
                    <small style='color: #155724;'><strong>{phase["name"]}</strong></small>
                </div>
                """, unsafe_allow_html=True)
            elif i == phase_info["phase_index"]:
                # 当前阶段
                st.markdown(f"""
                <div style='text-align: center; padding: 10px; background-color: #cce7ff; border-radius: 8px; border: 2px solid #007bff; box-shadow: 0 0 10px rgba(0,123,255,0.3);'>
                    <div style='font-size: 20px;'>⚡</div>
                    <small style='color: #004085;'><strong>{phase["name"]}</strong></small>
                </div>
                """, unsafe_allow_html=True)
            else:
                # 待执行阶段
                st.markdown(f"""
                <div style='text-align: center; padding: 10px; background-color: #f8f9fa; border-radius: 8px; border: 2px solid #dee2e6;'>
                    <div style='font-size: 20px;'>⏳</div>
                    <small style='color: #6c757d;'>{phase["name"]}</small>
                </div>
                """, unsafe_allow_html=True)

# --- 辅助函数 ---
def plot_gantt_chart(results_data, iteration):
    """为指定的迭代绘制甘特图。"""
    try:
        schedule_data = results_data['schedule_iteration'][iteration]['schedule']
        allocation_data = results_data['task_allocations_iteration'][iteration]['task_allocations']
        
        # 将Pydantic模型转换为DataFrame
        tasks = [item['task'] for item in allocation_data]
        allocations = [{'task_id': item['task']['id'], 'member_name': item['team_member']['name']} for item in allocation_data]
        schedules = [{'task_id': item['task_id'], 'start_date': item['start_date'], 'end_date': item['end_date']} for item in schedule_data]

        df_tasks = pd.DataFrame(tasks)
        df_alloc = pd.DataFrame(allocations)
        df_sched = pd.DataFrame(schedules)

        # 合并数据
        df = pd.merge(df_tasks, df_alloc, left_on='id', right_on='task_id')
        df = pd.merge(df, df_sched, on='task_id')
        
        # 日期转换
        df['start'] = pd.to_datetime(df['start_date'])
        df['end'] = pd.to_datetime(df['end_date'])
        
        df = df.rename(columns={'task_name': '任务名称', 'member_name': '负责人'})
        df = df.sort_values(by='负责人')

        fig = px.timeline(
            df, 
            x_start="start", 
            x_end="end", 
            y="任务名称", 
            color="负责人", 
            title=f"项目排期甘特图 - 第 {iteration + 1} 版"
        )
        fig.update_layout(
            xaxis_title="时间线",
            yaxis_title="任务",
            yaxis=dict(autorange="reversed"),
            title_x=0.5
        )
        st.plotly_chart(fig, use_container_width=True)
    except (KeyError, IndexError, TypeError) as e:
        st.error(f"无法为第 {iteration + 1} 版计划生成甘特图。错误: {e}")

# --- SSE实时进度组件 ---
def create_sse_progress_component(job_id: str, api_url: str) -> str:
    """创建SSE实时进度追踪的HTML组件"""
    component_id = str(uuid.uuid4())[:8]
    
    html_code = f"""
    <div id="sse-container-{component_id}">
        <div id="progress-display-{component_id}" style="font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;">
            <div style="text-align: center; padding: 20px;">
                <div style="font-size: 18px; color: #1f77b4; margin-bottom: 10px;">
                    🔄 正在连接实时更新服务...
                </div>
                <div id="connection-status-{component_id}" style="font-size: 12px; color: #666;">
                    等待连接建立
                </div>
            </div>
        </div>
    </div>

    <script>
    (function() {{
        console.log('Starting SSE connection for job: {job_id}');
        
        const containerId = 'sse-container-{component_id}';
        const progressDisplayId = 'progress-display-{component_id}';
        const connectionStatusId = 'connection-status-{component_id}';
        
        const progressDisplay = document.getElementById(progressDisplayId);
        const connectionStatus = document.getElementById(connectionStatusId);
        
        if (!progressDisplay) {{
            console.error('Progress display element not found');
            return;
        }}
        
        // 构建API URL - 修复iframe环境下hostname获取问题
        let apiUrl;
        
        // 尝试从父窗口获取hostname（针对iframe环境）
        try {{
            const parentHost = window.parent.location.hostname;
            const currentHost = window.location.hostname || parentHost;
            
            console.log('Current hostname:', currentHost);
            console.log('Parent hostname:', parentHost);
            
            if (currentHost && currentHost !== '' && currentHost !== 'localhost') {{
                apiUrl = `http://${{currentHost}}:8000`;
            }} else if (currentHost === 'localhost') {{
                apiUrl = 'http://127.0.0.1:8000';
            }} else {{
                // 直接使用已知的服务器地址
                apiUrl = 'http://172.19.136.212:8000';
            }}
        }} catch (e) {{
            console.log('Cannot access parent location, using fallback');
            // iframe跨域限制时直接使用已知地址
            apiUrl = 'http://172.19.136.212:8000';
        }}
        
        console.log('Final API URL:', apiUrl);
        
        const eventSource = new EventSource(`${{apiUrl}}/v1/plans/{job_id}/stream`);
        let startTime = Date.now();
        let hasReceivedData = false;
        
        // 5秒后如果还没收到数据，显示更友好的提示
        setTimeout(() => {{
            if (!hasReceivedData) {{
                connectionStatus.innerHTML = '⚠️ 连接建立中，请稍候...';
                connectionStatus.style.color = '#ffc107';
                
                // 如果是已完成的任务，直接显示完成状态
                fetch(`${{apiUrl}}/v1/plans/{job_id}/status`)
                    .then(response => response.json())
                    .then(data => {{
                        if (data.status === 'finished' || data.progress === 100) {{
                            progressDisplay.innerHTML = `
                                <div style="text-align: center; padding: 25px; background: linear-gradient(135deg, #28a745, #20c997); border-radius: 10px; color: white;">
                                    <div style="font-size: 24px; margin-bottom: 15px;">🎉 项目计划已生成完成！</div>
                                    <div style="font-size: 16px; margin-bottom: 10px;">✅ 进度: 100%</div>
                                    <div style="font-size: 14px; opacity: 0.9;">任务ID: {job_id}</div>
                                    <button onclick="showTaskResult('{job_id}')" 
                                            style="margin-top: 15px; padding: 12px 24px; background: white; color: #28a745; border: none; border-radius: 8px; cursor: pointer; font-weight: bold; box-shadow: 0 2px 10px rgba(0,0,0,0.1); transition: all 0.3s ease;">
                                        📋 查看详细结果
                                    </button>
                                </div>
                            `;
                            connectionStatus.innerHTML = '🎉 任务已完成！点击查看结果';
                            connectionStatus.style.color = '#28a745';
                            connectionStatus.style.cursor = 'pointer';
                            connectionStatus.onclick = () => showTaskResult('{job_id}');
                            eventSource.close();
                        }}
                    }})
                    .catch(e => console.log('Status check failed:', e));
            }}
        }}, 5000);
        
        eventSource.onopen = function(event) {{
            console.log('SSE connection opened');
            hasReceivedData = true;
            connectionStatus.innerHTML = '✅ 实时连接已建立';
            connectionStatus.style.color = '#28a745';
        }};
        
        eventSource.addEventListener('progress', function(event) {{
            try {{
                const data = JSON.parse(event.data);
                console.log('Progress update:', data);
                hasReceivedData = true;
                
                updateProgressDisplay(data);
                
                // 通知Streamlit状态更新（如果需要）
                if (window.parent && window.parent.postMessage) {{
                    window.parent.postMessage({{
                        type: 'sse_progress_update',
                        data: data
                    }}, '*');
                }}
                
            }} catch (e) {{
                console.error('Failed to parse SSE data:', e, event.data);
            }}
        }});
        
                        eventSource.addEventListener('complete', function(event) {{
            try {{
                const data = JSON.parse(event.data);
                console.log('Task completed:', data);
                
                updateProgressDisplay(data, true);
                connectionStatus.innerHTML = '🎉 任务完成！点击查看结果';
                connectionStatus.style.color = '#28a745';
                connectionStatus.style.cursor = 'pointer';
                connectionStatus.onclick = () => showTaskResult('{job_id}');
                
                // 关闭连接
                eventSource.close();
                
                // 立即显示完成状态 - 修复按钮逻辑
                progressDisplay.innerHTML = `
                    <div style="text-align: center; padding: 25px; background: linear-gradient(135deg, #28a745, #20c997); border-radius: 10px; color: white;">
                        <div style="font-size: 24px; margin-bottom: 15px;">🎉 项目计划生成完成！</div>
                        <div style="font-size: 16px; margin-bottom: 10px;">✅ 进度: 100%</div>
                        <div style="font-size: 14px; opacity: 0.9;">任务ID: ${{data.job_id}}</div>
                        <button onclick="showTaskResult('${{data.job_id}}')" 
                                style="margin-top: 15px; padding: 12px 24px; background: white; color: #28a745; border: none; border-radius: 8px; cursor: pointer; font-weight: bold; box-shadow: 0 2px 10px rgba(0,0,0,0.1); transition: all 0.3s ease;">
                            📋 查看详细结果  
                        </button>
                    </div>
                `;
                
                // 通知Streamlit任务完成
                if (window.parent && window.parent.postMessage) {{
                    window.parent.postMessage({{
                        type: 'sse_task_complete',
                        data: data
                    }}, '*');
                }}
                
                // 不自动刷新，让用户手动点击查看结果
                
            }} catch (e) {{
                console.error('Failed to parse completion data:', e);
            }}
        }});
        
        eventSource.addEventListener('error', function(event) {{
            try {{
                const data = JSON.parse(event.data);
                console.error('SSE error:', data);
                
                progressDisplay.innerHTML = `
                    <div style="text-align: center; padding: 20px; color: #dc3545;">
                        <div style="font-size: 18px; margin-bottom: 10px;">❌ 连接错误</div>
                        <div style="font-size: 14px;">${{data.error || '未知错误'}}</div>
                    </div>
                `;
                
                connectionStatus.innerHTML = '❌ 连接已断开';
                connectionStatus.style.color = '#dc3545';
                eventSource.close();
                
            }} catch (e) {{
                console.error('Failed to parse error data:', e);
            }}
        }});
        
        eventSource.onerror = function(event) {{
            console.error('EventSource failed:', event);
            connectionStatus.innerHTML = '⚠️ 连接不稳定，尝试重连...';
            connectionStatus.style.color = '#ffc107';
        }};
        
        function updateProgressDisplay(data, isComplete = false) {{
            const progress = data.progress || 0;
            const phase = data.phase || {{}};
            
            let statusIcon = '🔄';
            let statusColor = '#1f77b4';
            
            if (isComplete || data.status === 'finished') {{
                statusIcon = '🎉';
                statusColor = '#28a745';
            }} else if (data.status === 'failed') {{
                statusIcon = '❌';
                statusColor = '#dc3545';
            }}
            
            const elapsedTime = data.elapsed_time || 0;
            const estimatedRemaining = data.estimated_remaining || 0;
            
            progressDisplay.innerHTML = `
                <div style="max-width: 600px; margin: 0 auto; padding: 20px; border: 1px solid #e0e0e0; border-radius: 8px; background: #f8f9fa;">
                    <div style="display: flex; align-items: center; justify-content: space-between; margin-bottom: 15px;">
                        <div style="font-size: 18px; color: ${{statusColor}};">
                            ${{statusIcon}} ${{phase.name || '正在处理...'}}
                        </div>
                        <div style="font-size: 14px; color: #666;">
                            ${{progress}}%
                        </div>
                    </div>
                    
                    <div style="width: 100%; background-color: #e9ecef; border-radius: 4px; margin-bottom: 15px;">
                        <div style="width: ${{progress}}%; height: 8px; background-color: ${{statusColor}}; border-radius: 4px; transition: width 0.3s ease;"></div>
                    </div>
                    
                    <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 15px; font-size: 12px; color: #666;">
                        <div>
                            <strong>已执行时间:</strong> ${{Math.floor(elapsedTime)}}秒
                        </div>
                        <div>
                            <strong>预计剩余:</strong> ${{Math.floor(estimatedRemaining)}}秒
                        </div>
                        <div>
                            <strong>任务状态:</strong> ${{data.status}}
                        </div>
                        <div>
                            <strong>连接时长:</strong> ${{Math.floor((Date.now() - startTime) / 1000)}}秒
                        </div>
                    </div>
                    
                    ${{phase.name ? `
                        <div style="margin-top: 15px; padding: 10px; background: #e3f2fd; border-radius: 4px; border-left: 4px solid #2196f3;">
                            <div style="font-size: 13px; color: #1976d2;">
                                <strong>当前阶段:</strong> ${{phase.name}}
                            </div>
                            <div style="font-size: 12px; color: #666; margin-top: 5px;">
                                阶段进度: ${{phase.phase_progress || 0}}%
                            </div>
                        </div>
                    ` : ''}}
                </div>
            `;
        }}
        
        // 添加查看结果的JavaScript函数
        window.showTaskResult = function(jobId) {{
            console.log('Showing task result for job:', jobId);
            
            // 直接触发手动检查结果的逻辑
            fetch(`${{apiUrl}}/v1/plans/${{jobId}}`)
                .then(response => response.json())
                .then(data => {{
                    if (data.status === 'finished' && data.result) {{
                        // 通过postMessage通知Streamlit设置结果
                        if (window.parent && window.parent.postMessage) {{
                            window.parent.postMessage({{
                                type: 'set_task_result',
                                job_id: jobId,
                                result: data.result
                            }}, '*');
                        }}
                        
                        // 触发页面刷新以显示结果
                        setTimeout(() => {{
                            window.parent.location.reload();
                        }}, 500);
                    }}
                }})
                .catch(e => {{
                    console.error('Failed to fetch task result:', e);
                    // 如果API调用失败，仍然尝试刷新页面
                    window.parent.location.reload();
                }});
        }};
        
        // 监听来自父窗口的消息
        window.addEventListener('message', function(event) {{
            console.log('Received message:', event.data);
            if (event.data.type === 'set_task_result') {{
                // 在localStorage中存储结果数据，以便页面刷新后使用
                localStorage.setItem('task_result_' + event.data.job_id, JSON.stringify(event.data.result));
                localStorage.setItem('task_completed', 'true');
                localStorage.setItem('current_job_id', event.data.job_id);
            }}
        }});
        
        // 清理函数，当组件卸载时关闭连接
        window.addEventListener('beforeunload', function() {{
            eventSource.close();
        }});
        
    }})();
    </script>
    """
    
    return html_code

# --- 页面渲染 ---

# 标题和描述
st.title(f"{PAGE_ICON} {PAGE_TITLE}")
st.markdown(
    """
    <div style='text-align: center; padding: 20px; background: linear-gradient(90deg, #667eea 0%, #764ba2 100%); color: white; border-radius: 10px; margin-bottom: 30px;'>
        <h2>🚀 智能项目管理，让协作更高效</h2>
        <p>基于AI的项目计划生成器，为您的团队提供专业的任务分解、时间安排和风险评估</p>
    </div>
    """, 
    unsafe_allow_html=True
)

# 输入区域
with st.container():
    st.header("✏️ 项目信息输入")
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        project_description = st.text_area(
            "项目描述",
            value=EXAMPLE_PROJECT_DESCRIPTION,
            height=300,
            help="详细描述您的项目目标、功能需求、目标用户等信息"
        )
    
    with col2:
        st.subheader("📁 团队信息")
        uploaded_file = st.file_uploader(
            "上传团队信息CSV文件", 
            type=['csv'],
            help="包含团队成员姓名和技能简介的CSV文件"
        )
        
        # 示例文件下载
        st.download_button(
            label="📥 下载示例CSV文件",
            data=EXAMPLE_TEAM_CSV,
            file_name="team_example.csv",
            mime="text/csv"
        )
        
        # 如果上传了文件，显示预览
        if uploaded_file is not None:
            st.success("✅ 文件上传成功！")
            try:
                df = pd.read_csv(uploaded_file)
                st.subheader("👥 团队成员预览")
                st.dataframe(df, use_container_width=True)
            except Exception as e:
                st.error(f"文件读取失败: {e}")

# 生成按钮
generate_button = st.button("🚀 生成项目计划", type="primary", use_container_width=True)

# --- 检查并恢复localStorage中的任务结果 ---
components.html("""
<script>
// 检查localStorage中是否有任务结果需要恢复
if (localStorage.getItem('task_completed') === 'true') {
    const jobId = localStorage.getItem('current_job_id');
    const taskResult = localStorage.getItem('task_result_' + jobId);
    
    if (jobId && taskResult) {
        // 通知Streamlit恢复任务结果
        if (window.parent && window.parent.postMessage) {
            window.parent.postMessage({
                type: 'restore_task_result',
                job_id: jobId,
                result: JSON.parse(taskResult)
            }, '*');
        }
        
        // 清理localStorage
        localStorage.removeItem('task_completed');
        localStorage.removeItem('current_job_id');  
        localStorage.removeItem('task_result_' + jobId);
    }
}
</script>
""", height=0)

# 监听JavaScript消息来恢复任务状态
if 'restore_requested' not in st.session_state:
    st.session_state.restore_requested = False

# --- SSE实时进度监控与结果展示 ---
if generate_button:
    if not project_description or uploaded_file is None:
        st.error("⚠️ 请确保项目描述和团队CSV文件都已提供。")
    else:
        # 提交任务到后端
        files = {'team_file': (uploaded_file.name, uploaded_file.getvalue(), 'text/csv')}
        data = {'project_description': project_description}
        
        try:
            response = requests.post(f"{API_URL}/v1/plans", files=files, data=data)
            response.raise_for_status()
            job_info = response.json()
            st.session_state.job_id = job_info['job_id']
            st.session_state.task_submitted = True
            
            st.success(f"✅ 任务已提交！任务ID: {job_info['job_id']}")
            
        except requests.exceptions.RequestException as e:
            st.error(f"❌ 无法提交任务到后端: {e}")
            st.session_state.job_id = None

# 如果有正在进行的任务，显示SSE实时进度
if 'job_id' in st.session_state and st.session_state.job_id and st.session_state.get('task_submitted', False):
    job_id = st.session_state.job_id
    
    st.markdown("---")
    st.subheader("📊 实时任务进度")
    
    # 显示SSE进度组件
    sse_html = create_sse_progress_component(job_id, API_URL)
    components.html(sse_html, height=300, scrolling=False)
    
    # 添加手动刷新按钮 - 优化样式
    col1, col2, col3 = st.columns([1, 1, 1])
    with col2:
        # 创建美观的手动检查按钮
        st.markdown("""
        <style>
        .custom-button {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 10px 20px;
            border-radius: 25px;
            border: none;
            font-weight: bold;
            cursor: pointer;
            transition: all 0.3s ease;
            box-shadow: 0 4px 15px rgba(102, 126, 234, 0.3);
        }
        .custom-button:hover {
            transform: translateY(-2px);
            box-shadow: 0 6px 20px rgba(102, 126, 234, 0.4);
        }
        </style>
        """, unsafe_allow_html=True)
        
        if st.button("🔄 手动检查结果", key="manual_refresh", type="primary"):
            try:
                response = requests.get(f"{API_URL}/v1/plans/{job_id}")
                response.raise_for_status()
                result_data = response.json()
                
                if result_data.get("status") == "finished":
                    st.session_state.task_completed = True
                    st.session_state.task_result = result_data.get("result")
                    st.session_state.job_id = job_id  # 确保job_id保持
                    st.rerun()
                elif result_data.get("status") == "failed":
                    st.error("❌ 任务执行失败，请重试")
                    st.session_state.task_submitted = False
                else:
                    st.info(f"📋 任务状态: {result_data.get('status', '未知')}")
                    
            except requests.exceptions.RequestException as e:
                st.error(f"❌ 获取任务状态失败: {e}")

# 如果任务完成，显示结果
if st.session_state.get('task_completed', False) and st.session_state.get('task_result'):
    st.session_state.task_submitted = False  # 重置提交状态
    result_data = st.session_state.task_result
    
    # 继续使用原有的结果展示逻辑
    st.markdown("---")
    st.success("🎉 **项目计划生成完成！** 请查看下方详细结果。")
    
    # 成功摘要
    with st.container():
        st.markdown("---")
        st.header("📈 项目计划摘要")
        
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            results = result_data  # 定义results变量
            task_count = len(results.get('tasks', {}).get('tasks', []))
            st.metric("📋 任务总数", task_count)
        
        with col2:
            total_days = sum([task.get('estimated_day', 0) for task in results.get('tasks', {}).get('tasks', [])])
            st.metric("⏱️ 预估工期", f"{total_days} 天")
        
        with col3:
            risk_score = results.get('project_risk_score_iterations', [0])[-1]
            st.metric("⚠️ 风险评分", risk_score)
        
        with col4:
            iterations = results.get('iteration_number', 0)
            st.metric("🔄 优化轮次", iterations)
    
    # 详细结果标签页
    tab_tasks, tab_gantt, tab_risk, tab_raw = st.tabs(["📝 任务详情", "📊 甘特图", "⚠️ 风险评估", "🔧 原始数据"])

    with tab_tasks:
        st.header("📋 任务清单与分配")
        if results.get('task_allocations_iteration'):
            allocations = results['task_allocations_iteration'][-1]['task_allocations']
            df_alloc = pd.DataFrame([
                {
                    "任务名称": a['task']['task_name'],
                    "负责人": a['team_member']['name'],
                    "预计工时(天)": a['task']['estimated_day'],
                    "任务描述": a['task']['task_description'],
                } for a in allocations
            ])
            st.dataframe(df_alloc, use_container_width=True)
        else:
            st.info("📭 未能生成任务分配信息。")

    with tab_gantt:
        st.header("📊 项目排期甘特图")
        num_iterations = results.get('iteration_number', 0)
        if num_iterations > 0:
            plot_gantt_chart(results, num_iterations - 1) # 只显示最后一版
        else:
            st.info("📊 未能生成甘特图信息。")

    with tab_risk:
        st.header("⚠️ 风险评估与演进")
        st.subheader("🎯 最终风险清单")
        if results.get('risks_iteration'):
            risks = results['risks_iteration'][-1]['risks']
            df_risk = pd.DataFrame(risks)
            st.table(df_risk)
        else:
            st.info("📈 未能生成风险评估信息。")
        
        st.subheader("📈 项目风险分数变化")
        risk_scores = results.get('project_risk_score_iterations', [])
        if risk_scores:
            df_risk_chart = pd.DataFrame({
                '迭代次数': range(1, len(risk_scores) + 1),
                '风险总分': risk_scores
            })
            st.line_chart(df_risk_chart.set_index('迭代次数'))
        else:
            st.info("📊 无风险分数变化数据。")

    with tab_raw:
        st.header("🔧 完整的Agent最终状态")
        st.json(results)

# 页脚
st.markdown("---")
st.markdown(
    """
    <div style='text-align: center; color: #666; padding: 20px;'>
        <p>🤖 <strong>AI项目管理助手</strong> | 让项目管理更智能、更高效</p>
        <p>基于先进的AI技术，为您提供专业的项目规划服务</p>
    </div>
    """, 
    unsafe_allow_html=True
) 