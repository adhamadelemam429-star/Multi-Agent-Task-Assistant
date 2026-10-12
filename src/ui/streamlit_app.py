from __future__ import annotations

import subprocess
import sys
import time
import urllib.request
from pathlib import Path

import streamlit as st

from src.core.orchestrator import Orchestrator
from src.memory.session_manager import SessionManager
from src.tools.registry import execute_tool

PROJECT_ROOT = Path(__file__).resolve().parents[2]
API_HOST = "127.0.0.1"
API_PORT = 8001


def ensure_api_server() -> bool:
    url = f"http://{API_HOST}:{API_PORT}/health"
    try:
        with urllib.request.urlopen(url, timeout=2) as response:
            if response.status == 200:
                return True
    except Exception:
        pass

    venv_python = PROJECT_ROOT / ".venv" / "Scripts" / "python.exe"
    if not venv_python.exists():
        return False

    subprocess.Popen(
        [str(venv_python), "-m", "uvicorn", "src.api.main:app", "--host", API_HOST, "--port", str(API_PORT)],
        cwd=str(PROJECT_ROOT),
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
        start_new_session=True,
    )

    for _ in range(30):
        time.sleep(0.5)
        try:
            with urllib.request.urlopen(url, timeout=2) as response:
                if response.status == 200:
                    return True
        except Exception:
            continue
    return False


def render_app() -> None:
    st.set_page_config(page_title="Multi-Agent AI Task Assistant", page_icon="🤖", layout="wide")
    st.title("Multi-Agent AI Task Assistant")

    session_manager = SessionManager()
    orchestrator = Orchestrator()

    if "session_id" not in st.session_state:
        session = session_manager.create_session(language="en", mode="demo")
        st.session_state.session_id = session["session_id"]

    left_col, right_col = st.columns([2, 1])
    with left_col:
        st.subheader("Chat")
        if "messages" not in st.session_state:
            st.session_state.messages = []
        for message in st.session_state.messages:
            with st.chat_message(message["role"]):
                st.write(message["content"])

        user_input = st.chat_input("Describe the task you want to execute")
        if user_input:
            st.session_state.messages.append({"role": "user", "content": user_input})
            with st.chat_message("user"):
                st.write(user_input)
            result = orchestrator.handle_request(user_input, session_id=st.session_state.session_id)
            st.session_state.messages.append({"role": "assistant", "content": result["response"]})
            with st.chat_message("assistant"):
                st.write(result["response"])

    with right_col:
        st.subheader("Session")
        st.write(f"Session ID: {st.session_state.session_id}")
        st.write("Mode: Demo")
        if st.button("Run Project"):
            started = ensure_api_server()
            if started:
                st.success("Project started successfully on http://127.0.0.1:8001")
            else:
                st.warning("Could not start the local API server automatically.")

        if st.button("Run Agent Demo"):
            result = orchestrator.handle_request(
                "Analyze a CSV sales file and summarize missing values.",
                session_id=st.session_state.session_id,
            )
            st.session_state.messages.append({"role": "assistant", "content": result["response"]})
            st.success("Agent demo completed")
            st.json(result["plan"])

        if st.button("New Session"):
            session = session_manager.create_session(language="en", mode="demo")
            st.session_state.session_id = session["session_id"]
            st.session_state.messages = []
            st.rerun()
        if st.button("Clear Session"):
            session_manager.clear_session(st.session_state.session_id)
            st.session_state.messages = []
            st.rerun()

        st.subheader("Tool Demo")
        tool_result = execute_tool("calculator", {"expression": "12 + 8 * 3"})
        st.code(str(tool_result), language="json")

        st.subheader("Knowledge")
        uploaded_file = st.file_uploader("Upload a text or CSV file", type=["txt", "md", "csv", "json", "log"])
        if uploaded_file is not None:
            file_bytes = uploaded_file.read()
            target_dir = Path("storage/uploads")
            target_dir.mkdir(parents=True, exist_ok=True)
            destination = target_dir / uploaded_file.name
            destination.write_bytes(file_bytes)
            st.success(f"Saved: {destination}")

        st.subheader("Output")
        output_dir = Path("outputs")
        output_dir.mkdir(exist_ok=True)
        st.write(f"Output folder: {output_dir.resolve()}")

        st.subheader("Task Plan")
        sample = orchestrator.planner.create_plan("Analyze a CSV file and summarise its missing values.")
        st.json(sample.model_dump())
