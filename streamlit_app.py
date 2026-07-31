import streamlit as st
import httpx
from httpx_sse import connect_sse
import json
import time

# Page Configuration
st.set_page_config(
    page_title="AgentOps | Mission Control",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for Futuristic Premium UI
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Fira+Code:wght@400;600&family=Inter:wght@300;400;600;700;800&family=Outfit:wght@400;600;700&display=swap');

    html, body, [class*="css"] {
        font-family: 'Inter', sans-serif;
    }

    /* Main background & glassmorphism theme */
    .stApp {
        background: radial-gradient(circle at 10% 20%, rgba(15, 23, 42, 1) 0%, rgba(10, 15, 29, 1) 90%);
        color: #f8fafc;
    }

    /* Header styling */
    .brand-header {
        background: linear-gradient(135deg, rgba(30, 41, 59, 0.7) 0%, rgba(15, 23, 42, 0.8) 100%);
        border: 1px solid rgba(255, 255, 255, 0.08);
        border-radius: 16px;
        padding: 24px 32px;
        margin-bottom: 24px;
        backdrop-filter: blur(12px);
        box-shadow: 0 10px 30px -10px rgba(0, 0, 0, 0.5), 0 0 20px rgba(99, 102, 241, 0.15);
    }
    
    .brand-title {
        font-family: 'Outfit', sans-serif;
        font-size: 2.2rem;
        font-weight: 800;
        background: linear-gradient(90deg, #6366f1 0%, #a855f7 50%, #ec4899 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin: 0;
        letter-spacing: -0.5px;
    }

    .brand-subtitle {
        color: #94a3b8;
        font-size: 0.95rem;
        margin-top: 6px;
    }

    /* Status Pill */
    .status-pill {
        display: inline-flex;
        align-items: center;
        gap: 8px;
        padding: 6px 14px;
        border-radius: 20px;
        font-weight: 600;
        font-size: 0.82rem;
        letter-spacing: 0.5px;
        text-transform: uppercase;
    }
    .status-online {
        background: rgba(16, 185, 129, 0.15);
        color: #10b981;
        border: 1px solid rgba(16, 185, 129, 0.3);
        box-shadow: 0 0 10px rgba(16, 185, 129, 0.2);
    }
    .status-offline {
        background: rgba(239, 68, 68, 0.15);
        color: #ef4444;
        border: 1px solid rgba(239, 68, 68, 0.3);
    }
    .status-dot {
        width: 8px;
        height: 8px;
        border-radius: 50%;
        background-color: currentColor;
        animation: pulse 2s infinite;
    }

    @keyframes pulse {
        0% { opacity: 1; transform: scale(1); }
        50% { opacity: 0.4; transform: scale(1.2); }
        100% { opacity: 1; transform: scale(1); }
    }

    /* Cards */
    .card-box {
        background: rgba(30, 41, 59, 0.5);
        border: 1px solid rgba(255, 255, 255, 0.08);
        border-radius: 14px;
        padding: 20px;
        margin-bottom: 20px;
        backdrop-filter: blur(10px);
        transition: transform 0.2s ease, border-color 0.2s ease;
    }
    .card-box:hover {
        border-color: rgba(99, 102, 241, 0.4);
    }

    /* Section Titles */
    .section-header {
        font-family: 'Outfit', sans-serif;
        font-size: 1.25rem;
        font-weight: 700;
        color: #f1f5f9;
        display: flex;
        align-items: center;
        gap: 10px;
        margin-bottom: 16px;
    }
    
    .section-icon {
        background: linear-gradient(135deg, #6366f1 0%, #a855f7 100%);
        border-radius: 8px;
        width: 32px;
        height: 32px;
        display: inline-flex;
        align-items: center;
        justify-content: center;
        font-size: 1rem;
    }

    /* HITL Warning Banner */
    .hitl-banner {
        background: linear-gradient(135deg, rgba(245, 158, 11, 0.15) 0%, rgba(217, 119, 6, 0.05) 100%);
        border: 1px solid rgba(245, 158, 11, 0.4);
        border-radius: 14px;
        padding: 20px;
        margin-top: 20px;
        margin-bottom: 24px;
        box-shadow: 0 0 25px rgba(245, 158, 11, 0.15);
    }
    .hitl-title {
        color: #fbbf24;
        font-family: 'Outfit', sans-serif;
        font-weight: 700;
        font-size: 1.15rem;
        display: flex;
        align-items: center;
        gap: 8px;
        margin-bottom: 12px;
    }

    /* Code & Terminal Styling */
    code, stCode {
        font-family: 'Fira Code', monospace !important;
    }

    /* Primary Buttons */
    div.stButton > button[kind="primary"] {
        background: linear-gradient(135deg, #10b981 0%, #059669 100%) !important;
        border: none !important;
        color: white !important;
        font-weight: 700 !important;
        border-radius: 10px !important;
        padding: 10px 24px !important;
        box-shadow: 0 4px 14px rgba(16, 185, 129, 0.3) !important;
        transition: all 0.2s ease !important;
    }
    div.stButton > button[kind="primary"]:hover {
        transform: translateY(-1px) !important;
        box-shadow: 0 6px 20px rgba(16, 185, 129, 0.5) !important;
    }

    /* Form Submit Button */
    div.stFormSubmitButton > button {
        background: linear-gradient(135deg, #6366f1 0%, #8b5cf6 100%) !important;
        border: none !important;
        color: white !important;
        font-weight: 700 !important;
        border-radius: 10px !important;
        padding: 12px 24px !important;
        box-shadow: 0 4px 14px rgba(99, 102, 241, 0.35) !important;
        transition: all 0.2s ease !important;
    }
    div.stFormSubmitButton > button:hover {
        transform: translateY(-1px) !important;
        box-shadow: 0 6px 20px rgba(99, 102, 241, 0.55) !important;
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

# Header HTML
st.markdown(f"""
<div class="brand-header">
    <div style="display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap; gap: 16px;">
        <div>
            <h1 class="brand-title">⚡ AgentOps Mission Control</h1>
            <p class="brand-subtitle">Autonomous Multi-Agent Orchestrator with Ephemeral Sandboxing & Human-in-the-Loop Approval</p>
        </div>
        <div>
            <span class="status-pill {'status-online' if backend_online else 'status-offline'}">
                <span class="status-dot"></span>
                FastAPI Engine: {'ONLINE' if backend_online else 'OFFLINE'}
            </span>
        </div>
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
    st.markdown("<h3 style='font-family: Outfit; font-weight: 700; margin-bottom: 20px;'>⚙️ Control Panel</h3>", unsafe_allow_html=True)
    
    # Active Thread Metric Card
    st.markdown(f"""
    <div class="card-box" style="padding: 16px;">
        <div style="font-size: 0.75rem; color: #94a3b8; text-transform: uppercase; font-weight: 700; letter-spacing: 0.5px;">Active State Thread</div>
        <div style="font-family: 'Fira Code', monospace; font-size: 0.95rem; color: #38bdf8; font-weight: 600; margin-top: 6px; word-break: break-all;">
            {st.session_state.thread_id or 'Idle (No Task Running)'}
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("### 📊 Workflow Pipeline")
    
    # Pipeline status steps
    step1_status = "✅" if st.session_state.thread_id else "⚪"
    step2_status = "🔄" if st.session_state.thread_id and not st.session_state.is_paused else ("✅" if st.session_state.is_paused or any("COMPLETE" in l for l in st.session_state.execution_logs) else "⚪")
    step3_status = "⏸️ PAUSED" if st.session_state.is_paused else ("✅ COMPLETE" if any("COMPLETE" in l for l in st.session_state.execution_logs) else "⚪ WAITING")
    
    st.markdown(f"""
    <div style="display: flex; flex-direction: column; gap: 10px; font-size: 0.88rem; color: #cbd5e1; margin-bottom: 20px;">
        <div style="display: flex; align-items: center; gap: 8px;"><span>{step1_status}</span> <span>1. Task Submission</span></div>
        <div style="display: flex; align-items: center; gap: 8px;"><span>{step2_status}</span> <span>2. Agent Reasoning & Fix</span></div>
        <div style="display: flex; align-items: center; gap: 8px;"><span>{step2_status}</span> <span>3. Docker Container Execution</span></div>
        <div style="display: flex; align-items: center; gap: 8px;"><span>{step3_status}</span> <span>4. Human Approval Gate</span></div>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("---")
    
    if st.button("🔄 Reset Session & Clear Logs", use_container_width=True):
        st.session_state.thread_id = None
        st.session_state.execution_logs = []
        st.session_state.is_paused = False
        st.session_state.interrupt_data = None
        st.rerun()

# Layout Columns: Task Submission & Live Stream
col_left, col_right = st.columns([1, 1], gap="large")

with col_left:
    st.markdown("""
    <div class="section-header">
        <div class="section-icon">📝</div>
        <span>1. Dispatch Coding Task</span>
    </div>
    """, unsafe_allow_html=True)
    
    with st.form("task_form"):
        task_description = st.text_area(
            "Task Prompt",
            placeholder="e.g., Write a python function `is_palindrome(s)` that returns True if string s is a palindrome.",
            height=120,
            help="Describe the code feature, function, or bug fix required."
        )
        code_context = st.text_area(
            "Existing Code Context (Optional)",
            placeholder="# Provide existing functions or environment definitions here...",
            height=80
        )
        submit_button = st.form_submit_button("🚀 Launch AgentOps Pipeline", use_container_width=True)

    if submit_button and task_description:
        st.session_state.execution_logs = []
        st.session_state.is_paused = False
        st.session_state.interrupt_data = None

        with st.spinner("Initializing PostgreSQL checkpoint state..."):
            try:
                resp = httpx.post(
                    f"{API_BASE_URL}/submit",
                    json={"task_description": task_description, "code_context": code_context},
                    timeout=10.0
                )
                if resp.status_code == 200:
                    data = resp.json()
                    st.session_state.thread_id = data["thread_id"]
                    st.toast(f"Task Initialized! Thread: {st.session_state.thread_id}", icon="✅")
                    st.rerun()
                else:
                    st.error(f"Submission failed: {resp.text}")
            except Exception as e:
                st.error(f"Connection Error: {e}")

with col_right:
    st.markdown("""
    <div class="section-header">
        <div class="section-icon">📡</div>
        <span>2. Live Agent Execution Stream</span>
    </div>
    """, unsafe_allow_html=True)
    
    log_container = st.empty()

    def render_logs():
        formatted_logs = "\n".join(st.session_state.execution_logs)
        log_container.code(formatted_logs or "Awaiting task dispatch...\nSubmit a prompt to view real-time node state transitions.", language="text")

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
                        log_line = f"[{timestamp}] ➔ [NODE EXECUTED]: {node_name.upper()}"
                        st.session_state.execution_logs.append(log_line)
                        render_logs()

                    elif sse.event == "human_approval_required":
                        payload = json.loads(sse.data)
                        st.session_state.is_paused = True
                        st.session_state.interrupt_data = payload
                        timestamp = time.strftime("%H:%M:%S")
                        st.session_state.execution_logs.append(f"[{timestamp}] ⏸️ [SYSTEM PAUSED]: Interrupt Gate - Human Review Required!")
                        render_logs()
                        st.rerun()
                        break

                    elif sse.event == "complete":
                        timestamp = time.strftime("%H:%M:%S")
                        st.session_state.execution_logs.append(f"[{timestamp}] 🎉 [WORKFLOW COMPLETE]: Task finished successfully!")
                        render_logs()
                        break

    except Exception as e:
        st.error(f"Stream Error: {e}")

# Trigger SSE stream listening
if st.session_state.thread_id and not st.session_state.is_paused:
    if not any("WORKFLOW COMPLETE" in log for log in st.session_state.execution_logs):
        listen_to_sse_stream(st.session_state.thread_id)

# Human-in-the-Loop Gate Banner & Code Review Section
if st.session_state.is_paused and st.session_state.interrupt_data:
    st.markdown("""
    <div class="hitl-banner">
        <div class="hitl-title">⚠️ ACTION REQUIRED: Human-in-the-Loop Review Gate</div>
        <p style="color: #cbd5e1; font-size: 0.9rem; margin-bottom: 0;">
            The execution graph has suspended at the approval gate. Review the code generated by the LLM Developer Agent and the verification output from the Docker Sandbox before proceeding.
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    payload = st.session_state.interrupt_data.get("payload", {})
    code_to_review = payload.get("generated_code", "# No code generated")
    sandbox_logs = payload.get("sandbox_logs", "No execution logs recorded")

    rev_col1, rev_col2 = st.columns(2, gap="large")
    
    with rev_col1:
        st.markdown("#### 💻 Generated Python Fix Code")
        st.code(code_to_review, language="python")

    with rev_col2:
        st.markdown("#### 🐳 Ephemeral Docker Sandbox Output")
        st.code(sandbox_logs, language="text")

    st.markdown("<br>", unsafe_allow_html=True)
    
    btn_col1, btn_col2, _ = st.columns([1.5, 1.5, 3])
    
    with btn_col1:
        if st.button("✅ Approve & Resume Execution", type="primary", use_container_width=True):
            try:
                approve_resp = httpx.post(
                    f"{API_BASE_URL}/{st.session_state.thread_id}/approve",
                    json={"approved": True},
                    timeout=10.0
                )
                if approve_resp.status_code == 200:
                    st.toast("Approved! Resuming workflow graph...", icon="🎉")
                    st.session_state.is_paused = False
                    st.session_state.interrupt_data = None
                    time.sleep(1)
                    st.rerun()
                else:
                    st.error("Failed to submit approval.")
            except Exception as e:
                st.error(f"Approval error: {e}")

    with btn_col2:
        if st.button("❌ Reject & Abort Workflow", use_container_width=True):
            try:
                reject_resp = httpx.post(
                    f"{API_BASE_URL}/{st.session_state.thread_id}/approve",
                    json={"approved": False},
                    timeout=10.0
                )
                if reject_resp.status_code == 200:
                    st.toast("Rejected! Workflow state aborted.", icon="🛑")
                    st.session_state.is_paused = False
                    st.session_state.interrupt_data = None
                    st.session_state.execution_logs.append("🚫 [WORKFLOW ABORTED]: Decision signal REJECTED by Human Reviewer.")
                    time.sleep(1)
                    st.rerun()
            except Exception as e:
                st.error(f"Rejection error: {e}")
