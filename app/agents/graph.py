from langgraph.graph import StateGraph, START, END
from app.core.state import AgentOpsState
from app.agents.nodes import analyst_node, developer_node, mock_sandbox_node
from app.db.checkpoint import CheckpointManager

# 1. Router function for conditional edge
def route_after_sandbox(state: AgentOpsState) -> str:
    """Route back to Developer if tests fail; otherwise proceed to END."""
    if state.get("test_passed"):
        print("➡️ Routing: Sandbox Passed -> END")
        return END
    else:
        print("🔄 Routing: Sandbox Failed -> Developer (Self-Correction Loop)")
        return "developer"

# 2. Build graph builder
builder = StateGraph(AgentOpsState)

# Add nodes
builder.add_node("analyst", analyst_node)
builder.add_node("developer", developer_node)
builder.add_node("sandbox", mock_sandbox_node)

# Add standard edges
builder.add_edge(START, "analyst")
builder.add_edge("analyst", "developer")
builder.add_edge("developer", "sandbox")

# Add conditional edge from sandbox
builder.add_conditional_edges(
    "sandbox",
    route_after_sandbox,
    {
        END: END,
        "developer": "developer"
    }
)

async def compile_agentops_graph():
    """Compiles graph bound to AsyncPostgresSaver checkpointer."""
    checkpointer = await CheckpointManager.get_checkpointer()
    return builder.compile(checkpointer=checkpointer)
