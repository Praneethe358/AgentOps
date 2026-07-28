from langgraph.graph import StateGraph, START, END
from app.core.state import AgentOpsState
from app.agents.nodes import analyst_node, developer_node, docker_sandbox_node
from app.db.checkpoint import CheckpointManager

def route_after_sandbox(state: AgentOpsState) -> str:
    if state.get("test_passed"):
        print("➡️ Routing: Real Sandbox Passed -> END")
        return END
    else:
        print("🔄 Routing: Real Sandbox Failed -> Developer (Self-Correction Loop)")
        return "developer"

builder = StateGraph(AgentOpsState)

builder.add_node("analyst", analyst_node)
builder.add_node("developer", developer_node)
builder.add_node("sandbox", docker_sandbox_node)

builder.add_edge(START, "analyst")
builder.add_edge("analyst", "developer")
builder.add_edge("developer", "sandbox")

builder.add_conditional_edges(
    "sandbox",
    route_after_sandbox,
    {
        END: END,
        "developer": "developer"
    }
)

async def compile_agentops_graph():
    checkpointer = await CheckpointManager.get_checkpointer()
    return builder.compile(checkpointer=checkpointer)
