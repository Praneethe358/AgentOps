import re
from app.core.state import AgentOpsState
from app.services.llm import llm_service

async def analyst_node(state: AgentOpsState) -> dict:
    """Analyze the task description and code context to form a fix plan."""
    print("🔍 [Analyst Node] Analyzing problem and planning fix...")
    
    system_prompt = (
        "You are an expert Lead Software Architect. Analyze the task and code context. "
        "Formulate a precise, step-by-step plan to resolve the issue."
    )
    user_prompt = f"Task: {state['task_description']}\nCode Context:\n{state['code_context']}"
    
    plan = await llm_service.generate(system_prompt, user_prompt)
    
    return {
        "messages": [{"role": "assistant", "name": "Analyst", "content": plan}]
    }


async def developer_node(state: AgentOpsState) -> dict:
    """Generate or update Python code based on the plan and execution logs."""
    print("💻 [Developer Node] Writing fix code...")
    
    system_prompt = (
        "You are a Senior Python Developer. Output ONLY valid Python code inside triple "
        "backticks ```python ... ```. Do not include markdown text outside code blocks."
    )
    
    user_prompt = (
        f"Task: {state['task_description']}\n"
        f"Code Context:\n{state['code_context']}\n"
    )
    
    # If this is a retry attempt, feed back the error logs!
    if state.get("execution_logs") and not state.get("test_passed"):
        user_prompt += f"\nPrevious attempt failed with errors:\n{state['execution_logs']}\nFix the error!"

    raw_response = await llm_service.generate(system_prompt, user_prompt)
    
    # Extract code from markdown backticks
    code_match = re.search(r"```python\s*(.*?)\s*```", raw_response, re.DOTALL)
    extracted_code = code_match.group(1) if code_match else raw_response
    
    return {
        "generated_code": extracted_code,
        "messages": [{"role": "assistant", "name": "Developer", "content": "Code generated."}]
    }


async def mock_sandbox_node(state: AgentOpsState) -> dict:
    """
    Mock sandbox for testing topology.
    In Phase 3, this will be replaced with real ephemeral Docker container execution!
    """
    print("🧪 [Mock Sandbox Node] Simulating code execution...")
    code = state.get("generated_code", "")
    
    # Simple check for simulation: pass if code is non-empty and contains a function definition
    if "def " in code:
        print("✅ [Mock Sandbox] Simulated tests PASSED.")
        return {
            "test_passed": True,
            "execution_logs": "Mock Test Output: 2 tests run, 2 passed."
        }
    else:
        print("❌ [Mock Sandbox] Simulated tests FAILED.")
        return {
            "test_passed": False,
            "execution_logs": "SyntaxError / TestFailure: No function definition found."
        }
