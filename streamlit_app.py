import streamlit as st
import httpx
from httpx_sse import connect_sse
import json
import time

# Page Configuration
st.set_page_config(
    page_title="AgentOps Enterprise | Orchestration Studio",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for Enterprise Software Aesthetic (Vercel / Linear / Datadog styled)
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&family=JetBrains+Mono:wght@400;500;600&display=swap');

    html, body, [class*="css"] {
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
    }

    /* Dark Enterprise Palette */
    .stApp {
        background-color: #0b0f19;
        color: #e2e8f0;
    }

    /* Sidebar Base Styling */
    [data-testid="stSidebar"] {
        background-color: #0d1322 !important;
        border-right: 1px solid #1e293b !important;
    }

    /* Sidebar Header Card */
    .sidebar-brand-card {
        background: #161e31;
        border: 1px solid #283548;
        border-radius: 8px;
        padding: 14px 16px;
        margin-bottom: 20px;
    }
    
    .sidebar-brand-title {
        font-size: 0.95rem;
        font-weight: 700;
        color: #f8fafc;
        display: flex;
        align-items: center;
        gap: 8px;
    }
    
    .sidebar-brand-env {
        font-size: 0.7rem;
        font-weight: 600;
        color: #38bdf8;
        background: rgba(56, 189, 248, 0.1);
        border: 1px solid rgba(56, 189, 248, 0.25);
        padding: 2px 6px;
        border-radius: 4px;
    }

    /* Sidebar Section Title */
    .sidebar-section-label {
        font-size: 0.72rem;
        font-weight: 700;
        text-transform: uppercase;
        letter-spacing: 0.8px;
        color: #64748b;
        margin-top: 18px;
        margin-bottom: 10px;
    }

    /* Sidebar System Metric Grid */
    .sys-metric-item {
        background: #111827;
        border: 1px solid #1f2937;
        border-radius: 6px;
        padding: 10px 12px;
        margin-bottom: 8px;
        display: flex;
        align-items: center;
        justify-content: space-between;
    }
    .sys-metric-name {
        font-size: 0.78rem;
        color: #9ca3af;
        font-weight: 500;
    }
    .sys-metric-val {
        font-size: 0.78rem;
        font-weight: 600;
        color: #10b981;
        font-family: 'JetBrains Mono', monospace;
    }

    /* Sidebar Step Item */
    .pipeline-step-item {
        background: #111827;
        border: 1px solid #1f2937;
        border-radius: 6px;
        padding: 10px 12px;
        margin-bottom: 6px;
        display: flex;
        align-items: center;
        justify-content: space-between;
        font-size: 0.8rem;
    }

    /* Top Navigation Header */
    .top-nav {
        display: flex;
        justify-content: space-between;
        align-items: center;
        padding: 16px 24px;
        background: #0f172a;
        border: 1px solid #1e293b;
        border-radius: 10px;
        margin-bottom: 24px;
    }

    .brand-title-enterprise {
        font-size: 1.25rem;
        font-weight: 700;
        color: #f8fafc;
        letter-spacing: -0.3px;
        display: flex;
        align-items: center;
        gap: 10px;
    }

    .brand-subtitle-enterprise {
        font-size: 0.82rem;
        color: #94a3b8;
        margin: 0;
    }

    /* Enterprise Status Badge */
    .badge-status {
        display: inline-flex;
        align-items: center;
        gap: 6px;
        padding: 4px 10px;
        border-radius: 6px;
        font-size: 0.75rem;
        font-weight: 600;
        letter-spacing: 0.3px;
        text-transform: uppercase;
    }

    .badge-online {
        background: rgba(16, 185, 129, 0.1);
        color: #10b981;
        border: 1px solid rgba(16, 185, 129, 0.3);
    }

    .badge-offline {
        background: rgba(239, 68, 68, 0.1);
        color: #ef4444;
        border: 1px solid rgba(239, 68, 68, 0.3);
    }

    .status-indicator-dot {
        width: 6px;
        height: 6px;
        border-radius: 50%;
        background-color: currentColor;
    }

    /* Section Containers */
    .panel-header {
        font-size: 0.95rem;
        font-weight: 600;
        color: #f1f5f9;
        margin-bottom: 14px;
        display: flex;
        align-items: center;
        justify-content: space-between;
    }

    /* Form Fields */
    div[data-baseweb="textarea"] {
        background-color: #0b0f19 !important;
        border: 1px solid #334155 !important;
        border-radius: 6px !important;
        color: #f8fafc !important;
    }

    div[data-baseweb="textarea"]:focus-within {
        border-color: #3b82f6 !important;
    }

    /* Buttons */
    div.stButton > button {
        border-radius: 6px !important;
        font-weight: 600 !important;
        font-size: 0.88rem !important;
        padding: 8px 16px !important;
        transition: background-color 0.15s ease !important;
    }

    div.stFormSubmitButton > button {
        background-color: #2563eb !important;
        color: #ffffff !important;
        border: 1px solid #3b82f6 !important;
        border-radius: 6px !important;
        font-weight: 600 !important;
    }

    div.stFormSubmitButton > button:hover {
        background-color: #1d4ed8 !important;
    }

    div.stButton > button[kind="primary"] {
        background-color: #059669 !important;
        color: #ffffff !important;
        border: 1px solid #10b981 !important;
    }

    div.stButton > button[kind="primary"]:hover {
        background-color: #047857 !important;
    }

    /* Code & Terminal Font */
    code, pre {
        font-family: 'JetBrains Mono', monospace !important;
        font-size: 0.85rem !important;
    }

    /* HITL Review Box */
    .hitl-review-container {
        background: #111827;
        border: 1px solid #374151;
        border-left: 4px solid #f59e0b;
        border-radius: 8px;
        padding: 20px;
        margin-top: 16px;
        margin-bottom: 24px;
    }
</style>
""", unsafe_allow_html=True)

API_BASE_URL = "http://localhost:8000/api/v1/tasks"

# Check Backend Health
backend_online = False
try:
    health_resp = httpx.get("http://localhost:8000/health", timeout=2.0)
    if health_resp.status_code == 200:
        backend_online = True
except Exception:
    backend_online = False

# Top Navigation Bar
st.markdown(f"""
<div class="top-nav">
    <div>
        <div class="brand-title-enterprise">
            <span>AgentOps Studio</span>
            <span style="font-size: 0.75rem; background: #1e293b; color: #94a3b8; padding: 2px 8px; border-radius: 4px; font-weight: 500;">v0.1.0-enterprise</span>
        </div>
        <p class="brand-subtitle-enterprise">Multi-Agent Task Orchestration Engine & Ephemeral Docker Sandbox</p>
    </div>
    <div>
        <span class="badge-status {'badge-online' if backend_online else 'badge-offline'}">
            <span class="status-indicator-dot"></span>
            {'FastAPI Service Operational' if backend_online else 'Service Disconnected'}
        </span>
    </div>
</div>
""", unsafe_allow_html=True)

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
    st.markdown("""
    <div class="sidebar-brand-card">
        <div class="sidebar-brand-title">
            <span>AgentOps</span>
            <span class="sidebar-brand-env">PROD</span>
        </div>
        <div style="font-size: 0.75rem; color: #94a3b8; margin-top: 4px;">LangGraph + Docker Stack</div>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("<div class='sidebar-section-label'>Infrastructure Health</div>", unsafe_allow_html=True)
    
    st.markdown(f"""
    <div class="sys-metric-item">
        <span class="sys-metric-name">FastAPI Core</span>
        <span class="sys-metric-val" style="color: {'#10b981' if backend_online else '#ef4444'};">{'ONLINE' if backend_online else 'OFFLINE'}</span>
    </div>
    <div class="sys-metric-item">
        <span class="sys-metric-name">Postgres DB</span>
        <span class="sys-metric-val">PORT 5433</span>
    </div>
    <div class="sys-metric-item">
        <span class="sys-metric-name">LLM Engine</span>
        <span class="sys-metric-val" style="color: #38bdf8;">Llama-3.3-70B</span>
    </div>
    <div class="sys-metric-item">
        <span class="sys-metric-name">Docker Sandbox</span>
        <span class="sys-metric-val">ACTIVE</span>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("<div class='sidebar-section-label'>Active Session</div>", unsafe_allow_html=True)
    
    st.markdown(f"""
    <div style="background: #111827; border: 1px solid #1f2937; border-radius: 6px; padding: 12px;">
        <div style="font-size: 0.7rem; color: #64748b; font-weight: 600; text-transform: uppercase;">State Thread Key</div>
        <div style="font-family: 'JetBrains Mono', monospace; font-size: 0.88rem; color: #38bdf8; font-weight: 600; margin-top: 4px; word-break: break-all;">
            {st.session_state.thread_id or 'IDLE_WAITING'}
        </div>
        <div style="font-size: 0.72rem; color: #9ca3af; margin-top: 8px; display: flex; justify-content: space-between;">
            <span>Events Recorded:</span>
            <span style="font-weight: 600; color: #f3f4f6;">{len(st.session_state.execution_logs)}</span>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("<div class='sidebar-section-label'>Topology Pipeline</div>", unsafe_allow_html=True)
    
    step1_st = "[DONE]" if st.session_state.thread_id else "[IDLE]"
    step2_st = "[PAUSED]" if st.session_state.is_paused else ("[DONE]" if any("COMPLETE" in l for l in st.session_state.execution_logs) else ("[BUSY]" if st.session_state.thread_id else "[IDLE]"))
    
    st.markdown(f"""
    <div class="pipeline-step-item">
        <span style="color: #d1d5db;">1. Analyst Agent</span>
        <span style="font-family: 'JetBrains Mono', monospace; font-size: 0.7rem; color: #38bdf8;">{step1_st}</span>
    </div>
    <div class="pipeline-step-item">
        <span style="color: #d1d5db;">2. Developer Agent</span>
        <span style="font-family: 'JetBrains Mono', monospace; font-size: 0.7rem; color: #38bdf8;">{step2_st}</span>
    </div>
    <div class="pipeline-step-item">
        <span style="color: #d1d5db;">3. Docker Sandbox</span>
        <span style="font-family: 'JetBrains Mono', monospace; font-size: 0.7rem; color: #38bdf8;">{step2_st}</span>
    </div>
    <div class="pipeline-step-item">
        <span style="color: #d1d5db;">4. Human Approval</span>
        <span style="font-family: 'JetBrains Mono', monospace; font-size: 0.7rem; color: #38bdf8;">{step2_st}</span>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("<div style='margin-top: 20px;'></div>", unsafe_allow_html=True)
    
    if st.button("Reset Thread State", use_container_width=True):
        st.session_state.thread_id = None
        st.session_state.execution_logs = []
        st.session_state.is_paused = False
        st.session_state.interrupt_data = None
        st.rerun()

# Workspace Split View
col1, col2 = st.columns([1, 1], gap="medium")

with col1:
    st.markdown("""
    <div class="panel-header">
        <span>Task Dispatch Console</span>
        <span style="font-size: 0.75rem; color: #64748b;">POST /api/v1/tasks/submit</span>
    </div>
    """, unsafe_allow_html=True)
    
    with st.form("task_dispatch_form"):
        task_description = st.text_area(
            "Specification / Requirements",
            placeholder="Enter task requirement (e.g., Write a python function `is_palindrome(s)` to check string palindromes).",
            height=120
        )
        code_context = st.text_area(
            "Code Base Context (Optional)",
            placeholder="Existing source code or type definitions...",
            height=80
        )
        submit_btn = st.form_submit_button("Run Task Orchestration", use_container_width=True)

    if submit_btn and task_description:
        st.session_state.execution_logs = []
        st.session_state.is_paused = False
        st.session_state.interrupt_data = None

        try:
            resp = httpx.post(
                f"{API_BASE_URL}/submit",
                json={"task_description": task_description, "code_context": code_context},
                timeout=10.0
            )
            if resp.status_code == 200:
                data = resp.json()
                st.session_state.thread_id = data["thread_id"]
                st.toast(f"Thread initialized: {st.session_state.thread_id}")
                st.rerun()
            else:
                st.error(f"Error submitting task: {resp.text}")
        except Exception as e:
            st.error(f"Network error: {e}")

with col2:
    st.markdown("""
    <div class="panel-header">
        <span>Live Execution Output</span>
        <span style="font-size: 0.75rem; color: #64748b;">GET /api/v1/tasks/stream</span>
    </div>
    """, unsafe_allow_html=True)
    
    log_container = st.empty()

    def render_logs():
        formatted_logs = "\n".join(st.session_state.execution_logs)
        log_container.code(formatted_logs or "[IDLE] System ready. Submit a task to begin stream.", language="text")

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
                        timestamp = time.strftime("%H:%M:%S")
                        log_line = f"[{timestamp}] INFO  - Node Completed: {node_name.upper()}"
                        st.session_state.execution_logs.append(log_line)
                        render_logs()

                    elif sse.event == "human_approval_required":
                        payload = json.loads(sse.data)
                        st.session_state.is_paused = True
                        st.session_state.interrupt_data = payload
                        timestamp = time.strftime("%H:%M:%S")
                        st.session_state.execution_logs.append(f"[{timestamp}] PAUSE - Graph Suspended: Waiting for Human Approval Signal")
                        render_logs()
                        st.rerun()
                        break

                    elif sse.event == "complete":
                        timestamp = time.strftime("%H:%M:%S")
                        st.session_state.execution_logs.append(f"[{timestamp}] SUCCESS - Execution Graph Completed")
                        render_logs()
                        break

    except Exception as e:
        st.error(f"Stream exception: {e}")

# Stream Listener Trigger
if st.session_state.thread_id and not st.session_state.is_paused:
    if not any("SUCCESS" in log for log in st.session_state.execution_logs):
        listen_to_sse_stream(st.session_state.thread_id)

# Human-in-the-Loop Review Section
if st.session_state.is_paused and st.session_state.interrupt_data:
    st.markdown("""
    <div class="hitl-review-container">
        <div style="font-weight: 700; font-size: 1rem; color: #f59e0b; margin-bottom: 6px;">
            [ATTENTION] Approval Gate Triggered - Code Verification Required
        </div>
        <div style="font-size: 0.85rem; color: #9ca3af;">
            Review generated code artifacts and sandbox container output before signaling continuation.
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    payload = st.session_state.interrupt_data.get("payload", {})
    code_to_review = payload.get("generated_code", "# No code output")
    sandbox_logs = payload.get("sandbox_logs", "No logs recorded")

    r_col1, r_col2 = st.columns(2, gap="medium")
    
    with r_col1:
        st.markdown("<div style='font-size: 0.85rem; font-weight: 600; color: #e2e8f0; margin-bottom: 6px;'>Generated Artifact (solution.py)</div>", unsafe_allow_html=True)
        st.code(code_to_review, language="python")

    with r_col2:
        st.markdown("<div style='font-size: 0.85rem; font-weight: 600; color: #e2e8f0; margin-bottom: 6px;'>Sandbox Logs (Docker Container)</div>", unsafe_allow_html=True)
        st.code(sandbox_logs, language="text")

    st.markdown("<div style='margin-top: 16px;'></div>", unsafe_allow_html=True)
    
    btn1, btn2, _ = st.columns([1.5, 1.5, 3])
    
    with btn1:
        if st.button("Approve & Continue", type="primary", use_container_width=True):
            try:
                approve_resp = httpx.post(
                    f"{API_BASE_URL}/{st.session_state.thread_id}/approve",
                    json={"approved": True},
                    timeout=10.0
                )
                if approve_resp.status_code == 200:
                    st.toast("Approved. Execution resumed.")
                    st.session_state.is_paused = False
                    st.session_state.interrupt_data = None
                    time.sleep(1)
                    st.rerun()
            except Exception as e:
                st.error(f"Approval error: {e}")

    with btn2:
        if st.button("Reject & Abort", use_container_width=True):
            try:
                reject_resp = httpx.post(
                    f"{API_BASE_URL}/{st.session_state.thread_id}/approve",
                    json={"approved": False},
                    timeout=10.0
                )
                if reject_resp.status_code == 200:
                    st.toast("Execution aborted.")
                    st.session_state.is_paused = False
                    st.session_state.interrupt_data = None
                    st.session_state.execution_logs.append("ABORT - User rejected execution.")
                    time.sleep(1)
                    st.rerun()
            except Exception as e:
                st.error(f"Rejection error: {e}")
