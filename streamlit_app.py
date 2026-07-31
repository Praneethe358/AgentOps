import streamlit as st
import httpx
from httpx_sse import connect_sse
import json
import time

# Page Configuration
st.set_page_config(
    page_title="AgentOps | Multi-Agent Orchestrator",
    page_icon="🤖",
    layout="wide"
)

API_BASE_URL = "http://localhost:8000/api/v1/tasks"

# Header Title
st.title("🤖 AgentOps Dashboard")
st.caption("Multi-Agent Task Orchestrator with Ephemeral Docker Sandboxing & Human-in-the-Loop Controls")
st.divider()

# Session State Initialization
if "thread_id" not in st.session_state:
    st.session_state.thread_id = None
if "execution_logs" not in st.session_state:
    st.session_state.execution_logs = []
if "is_paused" not in st.session_state:
    st.session_state.is_paused = False
if "interrupt_data" not in st.session_state:
    st.session_state.interrupt_data = None

# Sidebar Configuration
with st.sidebar:
    st.header("⚙️ System Status")
    try:
        health_resp = httpx.get("http://localhost:8000/health", timeout=3.0)
        if health_resp.status_code == 200:
            st.success("FastAPI Backend: ONLINE")
        else:
            st.error("FastAPI Backend: OFFLINE")
    except Exception:
        st.error("FastAPI Backend: OFFLINE")

    st.markdown("---")
    st.markdown("### Active Thread")
    st.code(st.session_state.thread_id or "No Active Task", language="text")
    
    if st.button("Reset Session", use_container_width=True):
        st.session_state.thread_id = None
        st.session_state.execution_logs = []
        st.session_state.is_paused = False
        st.session_state.interrupt_data = None
        st.rerun()

# Layout: Task Input Form
st.subheader("1. Submit Coding Task")
with st.form("task_form"):
    task_description = st.text_area(
        "Task Description",
        placeholder="e.g., Write a python function `is_palindrome(s)` that returns True if string s is a palindrome.",
        height=100
    )
    code_context = st.text_area(
        "Code Context (Optional)",
        placeholder="Existing code or module structure...",
        height=70
    )
    submit_button = st.form_submit_button("Launch AgentOps Pipeline", use_container_width=True)

if submit_button and task_description:
    st.session_state.execution_logs = []
    st.session_state.is_paused = False
    st.session_state.interrupt_data = None

    # Step 1: Submit Task to FastAPI
    with st.spinner("Initializing task and establishing PostgreSQL checkpointer..."):
        try:
            resp = httpx.post(
                f"{API_BASE_URL}/submit",
                json={"task_description": task_description, "code_context": code_context},
                timeout=10.0
            )
            if resp.status_code == 200:
                data = resp.json()
                st.session_state.thread_id = data["thread_id"]
                st.success(f"Task Submitted! Thread ID: {st.session_state.thread_id}")
            else:
                st.error(f"Failed to submit task: {resp.text}")
        except Exception as e:
            st.error(f"Connection Error: {e}")

st.divider()

# Layout: Live Terminal Streaming
st.subheader("2. Live Agent Execution Stream")
log_container = st.empty()

def render_logs():
    formatted_logs = "\n".join(st.session_state.execution_logs)
    log_container.code(formatted_logs or "Awaiting task submission...", language="text")

render_logs()

# Function to listen to SSE stream
def listen_to_sse_stream(thread_id: str):
    stream_url = f"{API_BASE_URL}/{thread_id}/stream"
    
    try:
        with httpx.Client(timeout=None) as client:
            with connect_sse(client, "GET", stream_url) as event_source:
                for sse in event_source.iter_sse():
                    if sse.event == "node_update":
                        payload = json.loads(sse.data)
                        node_name = payload.get("node", "Unknown")
                        log_line = f"➔ [NODE EXECUTED]: {node_name.upper()}"
                        st.session_state.execution_logs.append(log_line)
                        render_logs()

                    elif sse.event == "human_approval_required":
                        payload = json.loads(sse.data)
                        st.session_state.is_paused = True
                        st.session_state.interrupt_data = payload
                        st.session_state.execution_logs.append("⏸️ [SYSTEM PAUSED]: Human Approval Required!")
                        render_logs()
                        st.rerun()
                        break

                    elif sse.event == "complete":
                        st.session_state.execution_logs.append("🎉 [WORKFLOW COMPLETE]: Task finished successfully!")
                        render_logs()
                        break

    except Exception as e:
        st.error(f"Stream Error: {e}")

# Trigger SSE listening if thread_id is active and not currently paused
if st.session_state.thread_id and not st.session_state.is_paused:
    # Only run stream if execution isn't marked complete yet
    if not any("WORKFLOW COMPLETE" in log for log in st.session_state.execution_logs):
        listen_to_sse_stream(st.session_state.thread_id)

st.divider()

# Layout: Human-in-the-Loop Gate Modal/Banner
if st.session_state.is_paused and st.session_state.interrupt_data:
    st.warning("⚠️ **ACTION REQUIRED: Human-in-the-Loop Review Gate**")
    
    payload = st.session_state.interrupt_data.get("payload", {})
    code_to_review = payload.get("generated_code", "# No code provided")
    sandbox_logs = payload.get("sandbox_logs", "No logs")

    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("### Generated Fix Code")
        st.code(code_to_review, language="python")

    with col2:
        st.markdown("### Ephemeral Docker Sandbox Output")
        st.code(sandbox_logs, language="text")

    st.markdown("---")
    
    btn_col1, btn_col2, _ = st.columns([1, 1, 3])
    
    with btn_col1:
        if st.button("✅ Approve & Execute", type="primary", use_container_width=True):
            try:
                approve_resp = httpx.post(
                    f"{API_BASE_URL}/{st.session_state.thread_id}/approve",
                    json={"approved": True},
                    timeout=10.0
                )
                if approve_resp.status_code == 200:
                    st.success("Approved! Resuming execution...")
                    st.session_state.is_paused = False
                    st.session_state.interrupt_data = None
                    time.sleep(1)
                    st.rerun()
                else:
                    st.error("Failed to approve.")
            except Exception as e:
                st.error(f"Approval error: {e}")

    with btn_col2:
        if st.button("❌ Reject & Abort", use_container_width=True):
            try:
                reject_resp = httpx.post(
                    f"{API_BASE_URL}/{st.session_state.thread_id}/approve",
                    json={"approved": False},
                    timeout=10.0
                )
                if reject_resp.status_code == 200:
                    st.error("Rejected! Workflow aborted.")
                    st.session_state.is_paused = False
                    st.session_state.interrupt_data = None
                    st.session_state.execution_logs.append("🚫 [WORKFLOW ABORTED]: Rejected by Human Reviewer.")
                    time.sleep(1)
                    st.rerun()
            except Exception as e:
                st.error(f"Rejection error: {e}")
