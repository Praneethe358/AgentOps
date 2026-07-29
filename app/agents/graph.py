from langgraph.graph import StateGraph, START, END
from app.core.state import AgentOpsState
from app.agents.nodes import analyst_node, developer_node, docker_sandbox_node, human_review_node
from app.db.checkpoint import CheckpointManager

def route_after_sandbox(state: AgentOpsState) -> str:
    if state.get("test_passed"):
        print("➡️ Routing: Sandbox Passed -> Human Review Gate")
        return "human_review"
    else:
        print("🔄 Routing: Sandbox Failed -> Developer (Self-Correction Loop)")
        return "developer"

def route_after_human_review(state: AgentOpsState) -> str:
    if state.get("human_approved"):
        print("🎉 Routing: Approved by Human -> END (Task Completed)")
        return END
    else:
        print("🚫 Routing: Rejected by Human -> END (Task Aborted)")
        return END

builder = StateGraph(AgentOpsState)

# Add Nodes
builder.add_node("analyst", analyst_node)
builder.add_node("developer", developer_node)
builder.add_node("sandbox", docker_sandbox_node)
builder.add_node("human_review", human_review_node)

# Add Edges
builder.add_edge(START, "analyst")
builder.add_edge("analyst", "developer")
builder.add_edge("developer", "sandbox")

# Add Conditional Edges
builder.add_conditional_edges(
    "sandbox",
    route_after_sandbox,
    {
        "human_review": "human_review",
        "developer": "developer"
    }
)

builder.add_conditional_edges(
    "human_review",
    route_after_human_review,
    {
        END: END
    }
)

async def compile_agentops_graph():
    checkpointer = await CheckpointManager.get_checkpointer()
    return builder.compile(checkpointer=checkpointer)
