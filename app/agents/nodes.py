import re
from app.core.state import AgentOpsState
from app.services.llm import llm_service
from app.services.sandbox import sandbox_runner

async def analyst_node(state: AgentOpsState) -> dict:
    print("🔍 [Analyst Node] Analyzing problem and planning fix...")
    system_prompt = (
        "You are an expert Lead Software Architect. Analyze the task and code context. "
        "Formulate a precise, step-by-step plan to resolve the issue."
    )
    user_prompt = f"Task: {state['task_description']}\nCode Context:\n{state['code_context']}"
    plan = await llm_service.generate(system_prompt, user_prompt)
    return {"messages": [{"role": "assistant", "name": "Analyst", "content": plan}]}


async def developer_node(state: AgentOpsState) -> dict:
    print("💻 [Developer Node] Writing fix code...")
    system_prompt = (
        "You are a Senior Python Developer. Output ONLY valid Python code inside triple "
        "backticks ```python ... ```. Do not include markdown text outside code blocks."
    )
    
    user_prompt = f"Task: {state['task_description']}\nCode Context:\n{state['code_context']}\n"
    
    if state.get("execution_logs") and not state.get("test_passed"):
        user_prompt += f"\nPrevious attempt failed inside Docker sandbox:\n{state['execution_logs']}\nFix the error!"

    raw_response = await llm_service.generate(system_prompt, user_prompt)
    
    code_match = re.search(r"```python\s*(.*?)\s*```", raw_response, re.DOTALL)
    extracted_code = code_match.group(1) if code_match else raw_response
    
    return {
        "generated_code": extracted_code,
        "messages": [{"role": "assistant", "name": "Developer", "content": "Code generated."}]
    }


async def docker_sandbox_node(state: AgentOpsState) -> dict:
    """Executes generated code in an isolated Docker container."""
    print("🐳 [Docker Sandbox Node] Executing code in isolated container...")
    code = state.get("generated_code", "")
    
    # Run in real ephemeral sandbox
    result = sandbox_runner.run_code_in_sandbox(code_content=code)
    
    if result["test_passed"]:
        print("✅ [Docker Sandbox] Container Execution PASSED.")
    else:
        print("❌ [Docker Sandbox] Container Execution FAILED.")
        
    return {
        "test_passed": result["test_passed"],
        "execution_logs": result["execution_logs"]
    }
