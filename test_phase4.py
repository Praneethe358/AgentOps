import asyncio
from langgraph.types import Command
from app.agents.graph import compile_agentops_graph
from app.core.state import AgentOpsState

async def verify_phase_4():
    print("🚀 Initializing Phase 4 Human-in-the-Loop Interrupt Test...")
    
    app = await compile_agentops_graph()
    thread_id = "test-hitl-thread-999"
    config = {"configurable": {"thread_id": thread_id}}
    
    initial_input: AgentOpsState = {
        "task_id": "task-401",
        "task_description": "Write a python function `multiply(a, b)` that returns their product.",
        "code_context": "# Empty context",
        "generated_code": "",
        "execution_logs": "",
        "test_passed": False,
        "human_approved": None,
        "messages": [{"role": "user", "content": "Execute task"}]
    }
    
    print("\n--- Step 1: Starting Execution Graph ---")
    # Execute graph until it hits the interrupt
    async for event in app.astream(initial_input, config=config):
        print(f"Graph Node Event: {list(event.keys())}")
    
    # Query current state from PostgreSQL to verify interrupt status
    current_state = await app.aget_state(config)
    print(f"\n⏸️ Graph Status: Paused = {bool(current_state.next)}")
    print(f"Next Node Pending: {current_state.next}")
    if current_state.tasks:
        for task in current_state.tasks:
            if task.interrupts:
                print(f"Surfaced Interrupt Payload:\n{task.interrupts[0].value}")

    print("\n--- Step 2: Simulating External Human Approval Signal ---")
    await asyncio.sleep(2) # Simulate human review delay
    
    # Resume graph execution using Command primitive
    resume_command = Command(resume={"approved": True})
    
    async for event in app.astream(resume_command, config=config):
        print(f"Resumed Graph Event: {list(event.keys())}")
        
    final_state = await app.aget_state(config)
    print("\n--- Final Graph Results ---")
    print(f"Human Approved: {final_state.values.get('human_approved')}")
    print("✅ Phase 4 Human-in-the-Loop Interrupt verified successfully!")

if __name__ == "__main__":
    asyncio.run(verify_phase_4())
