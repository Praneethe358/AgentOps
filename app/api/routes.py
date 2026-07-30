import json
import uuid
import asyncio
from fastapi import APIRouter, HTTPException
from fastapi.responses import StreamingResponse
from langgraph.types import Command

from app.api.schemas import (
    TaskSubmitRequest, 
    TaskSubmitResponse, 
    HumanApprovalRequest, 
    ThreadStateResponse
)
from app.agents.graph import compile_agentops_graph
from app.core.state import AgentOpsState

router = APIRouter(prefix="/api/v1/tasks", tags=["Tasks"])

@router.post("/submit", response_model=TaskSubmitResponse)
async def submit_task(payload: TaskSubmitRequest):
    """
    Submits a new coding task and initializes a PostgreSQL thread checkpoint.
    """
    task_id = f"task-{uuid.uuid4().hex[:8]}"
    thread_id = f"thread-{uuid.uuid4().hex[:8]}"
    
    app = await compile_agentops_graph()
    config = {"configurable": {"thread_id": thread_id}}
    
    initial_input: AgentOpsState = {
        "task_id": task_id,
        "task_description": payload.task_description,
        "code_context": payload.code_context or "",
        "generated_code": "",
        "execution_logs": "",
        "test_passed": False,
        "human_approved": None,
        "messages": [{"role": "user", "content": payload.task_description}]
    }
    
    # Save initial state into Postgres checkpointer
    await app.aupdate_state(config, initial_input)
    
    return TaskSubmitResponse(
        task_id=task_id,
        thread_id=thread_id,
        message="Task initialized successfully. Connect to /stream endpoint to execute."
    )


@router.get("/{thread_id}/stream")
async def stream_task_execution(thread_id: str):
    """
    Server-Sent Events (SSE) endpoint streaming real-time node outputs and logs.
    """
    app = await compile_agentops_graph()
    config = {"configurable": {"thread_id": thread_id}}
    
    # Verify thread exists in DB
    current_state = await app.aget_state(config)
    if not current_state.values:
        raise HTTPException(status_code=404, detail="Thread ID not found.")

    def json_serializer(obj):
        if hasattr(obj, "value"):
            return obj.value
        if hasattr(obj, "__dict__"):
            return obj.__dict__
        return str(obj)

    async def event_generator():
        # Stream events across graph nodes
        async for event in app.astream(None, config=config):
            for node_name, state_update in event.items():
                data_payload = {
                    "node": node_name,
                    "state_update": state_update
                }
                # Standard SSE format: data: <json>\n\n
                yield f"event: node_update\ndata: {json.dumps(data_payload, default=json_serializer)}\n\n"
                await asyncio.sleep(0.1)
                
        # Check if paused at interrupt or finished completely
        final_state = await app.aget_state(config)
        if bool(final_state.next):
            interrupt_info = {
                "status": "PAUSED_FOR_APPROVAL",
                "next_node": list(final_state.next),
                "payload": final_state.tasks[0].interrupts[0].value if final_state.tasks and final_state.tasks[0].interrupts else {}
            }
            yield f"event: human_approval_required\ndata: {json.dumps(interrupt_info, default=json_serializer)}\n\n"
        else:
            yield f"event: complete\ndata: {json.dumps({'status': 'COMPLETED'})}\n\n"

    return StreamingResponse(event_generator(), media_type="text/event-stream")


@router.get("/{thread_id}/state", response_model=ThreadStateResponse)
async def get_task_state(thread_id: str):
    """
    Fetch the current execution state and check if human approval is pending.
    """
    app = await compile_agentops_graph()
    config = {"configurable": {"thread_id": thread_id}}
    
    state = await app.aget_state(config)
    if not state.values:
        raise HTTPException(status_code=404, detail="Thread ID not found.")
        
    interrupt_payload = None
    if state.tasks and state.tasks[0].interrupts:
        interrupt_payload = state.tasks[0].interrupts[0].value
        
    return ThreadStateResponse(
        thread_id=thread_id,
        is_paused=bool(state.next),
        next_node=list(state.next) if state.next else None,
        current_values=state.values,
        interrupt_payload=interrupt_payload
    )


@router.post("/{thread_id}/approve")
async def approve_task(thread_id: str, payload: HumanApprovalRequest):
    """
    Sends a human decision signal (approve/reject) to resume graph execution.
    """
    app = await compile_agentops_graph()
    config = {"configurable": {"thread_id": thread_id}}
    
    current_state = await app.aget_state(config)
    if not bool(current_state.next):
        raise HTTPException(status_code=400, detail="Thread is not currently waiting for approval.")
        
    # Resume execution using Command primitive
    resume_command = Command(resume={"approved": payload.approved})
    
    # Trigger graph resumption asynchronously
    asyncio.create_task(app.ainvoke(resume_command, config=config))
    
    return {
        "status": "RESUMED",
        "message": f"Graph resumed with approval state: {payload.approved}"
    }
