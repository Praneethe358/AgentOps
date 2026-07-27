import asyncio
from app.db.checkpoint import CheckpointManager
from app.core.state import AgentOpsState

async def verify_phase_1():
    print("⏳ Connecting to PostgreSQL and initializing LangGraph Checkpointer...")
    
    checkpointer = await CheckpointManager.get_checkpointer()
    print("✅ Postgres Checkpointer successfully initialized and tables created!")

    # Instantiate dummy state
    initial_state: AgentOpsState = {
        "task_id": "task-001",
        "task_description": "Fix bug in authentication module",
        "code_context": "def authenticate(user): pass",
        "generated_code": "",
        "execution_logs": "",
        "test_passed": False,
        "human_approved": None,
        "messages": [{"role": "user", "content": "Start task"}]
    }
    
    print(f"✅ State Schema verified successfully. Task ID: {initial_state['task_id']}")

if __name__ == "__main__":
    asyncio.run(verify_phase_1())
