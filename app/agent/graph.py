from langgraph.graph import StateGraph, END
from langgraph.checkpoint.memory import MemorySaver
from loguru import logger

from app.agent.state import AgentState
from app.agent.nodes.extract_tasks import task_generation_node
from app.agent.nodes.analyze_dependencies import task_dependency_node
from app.agent.nodes.schedule_tasks import task_scheduler_node
from app.agent.nodes.allocate_team import task_allocation_node
from app.agent.nodes.assess_risk import risk_assessment_node
from app.agent.nodes.generate_insights import insight_generation_node

def router(state: AgentState) -> str:
    """Routes the workflow based on iteration count and risk assessment."""
    iteration_number = state["iteration_number"]
    max_iteration = state["max_iteration"]
    
    logger.info(f"Router check: Iteration {iteration_number}/{max_iteration}")

    if iteration_number >= max_iteration:
        logger.info("Max iterations reached. Ending workflow.")
        return END
    
    scores = state["project_risk_score_iterations"]
    if len(scores) > 1 and scores[-1] < scores[-2]:
        logger.info(f"Risk improved ({scores[-2]} -> {scores[-1]}). Ending workflow.")
        return END
    else:
        logger.info("Risk did not improve. Generating insights for next loop.")
        return "insight_generator"

def create_graph():
    """Creates and compiles the LangGraph agent."""
    workflow = StateGraph(AgentState)

    # Add nodes
    workflow.add_node("task_generation", task_generation_node)
    workflow.add_node("task_dependencies", task_dependency_node)
    workflow.add_node("task_scheduler", task_scheduler_node)
    workflow.add_node("task_allocator", task_allocation_node)
    workflow.add_node("risk_assessor", risk_assessment_node)
    workflow.add_node("insight_generator", insight_generation_node)

    # Define edges
    workflow.set_entry_point("task_generation")
    workflow.add_edge("task_generation", "task_dependencies")
    workflow.add_edge("task_dependencies", "task_scheduler")
    workflow.add_edge("task_scheduler", "task_allocator")
    workflow.add_edge("task_allocator", "risk_assessor")
    workflow.add_conditional_edges("risk_assessor", router, {
        "insight_generator": "insight_generator",
        END: END
    })
    workflow.add_edge("insight_generator", "task_scheduler")
    
    # Add memory/checkpointing
    memory = MemorySaver()
    
    # Compile the graph
    graph = workflow.compile(checkpointer=memory)
    logger.info("Agent graph compiled successfully.")
    return graph

# Create a global graph instance
agent_graph = create_graph()

def run_agent(initial_state: dict):
    """
    Main entry point to run the agent.
    This function will be called by the RQ worker.
    """
    config = {"configurable": {"thread_id": "1"}} # A unique thread_id should be used per run
    
    # The stream will execute the graph
    for event in agent_graph.stream(initial_state, config, stream_mode="values"):
        logger.info(f"Agent state updated: {event}")
    
    # Retrieve the final state
    final_state = agent_graph.get_state(config)
    return final_state.values 