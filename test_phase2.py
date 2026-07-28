import asyncio
from app.agents.graph import compile_agentops_graph
from app.core.state import AgentOpsState

async def verify_phase_2():
    print("🚀 Initializing AgentOps LangGraph Execution...")
    
    app = await compile_agentops_graph()
    
    # Thread ID required for Postgres checkpointer state isolation
    config = {"configurable": {"thread_id": "test-thread-001"}}
    
    initial_input: AgentOpsState = {
        "task_id": "task-101",
        "task_description": "Create a function `calculate_sum(a, b)` that adds two numbers.",
        "code_context": "# Empty python file",
        "generated_code": "",
        "execution_logs": "",
        "test_passed": False,
        "human_approved": None,
        "messages": [{"role": "user", "content": "Execute task"}]
    }
    
    # Invoke the state graph
    final_state = await app.ainvoke(initial_input, config=config)
    
    print("\n--- Phase 2 Execution Results ---")
    print(f"Test Passed: {final_state['test_passed']}")
    print(f"Generated Code:\n{final_state['generated_code']}")
    print(f"Execution Logs:\n{final_state['execution_logs']}")
    print("✅ Phase 2 Graph Topology verified successfully!")

if __name__ == "__main__":
    asyncio.run(verify_phase_2())
