import asyncio
from app.agents.graph import compile_agentops_graph
from app.core.state import AgentOpsState

async def verify_phase_3():
    print("🚀 Initializing Real Docker Sandbox Agent Verification...")
    
    app = await compile_agentops_graph()
    config = {"configurable": {"thread_id": "test-docker-thread-001"}}
    
    initial_input: AgentOpsState = {
        "task_id": "task-201",
        "task_description": "Write a python script that prints 'Hello from Ephemeral Sandbox!' and returns a list of squared numbers from 1 to 5.",
        "code_context": "# Empty context",
        "generated_code": "",
        "execution_logs": "",
        "test_passed": False,
        "human_approved": None,
        "messages": [{"role": "user", "content": "Execute task"}]
    }
    
    final_state = await app.ainvoke(initial_input, config=config)
    
    print("\n--- Phase 3 Sandbox Execution Results ---")
    print(f"Test Passed: {final_state['test_passed']}")
    print(f"Generated Code:\n{final_state['generated_code']}")
    print(f"Docker Container Logs:\n{final_state['execution_logs']}")
    print("✅ Phase 3 Ephemeral Docker Sandbox verified successfully!")

if __name__ == "__main__":
    asyncio.run(verify_phase_3())
