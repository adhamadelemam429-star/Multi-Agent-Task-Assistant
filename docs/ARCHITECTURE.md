# Architecture Overview

The project follows a layered architecture that balances flexibility, clear responsibilities, and safe local execution.

## Layer 1: User interfaces

- Streamlit app provides the chat UI and quick demo interactions.
- FastAPI serves the REST API and can be used for automation or testing.

## Layer 2: Orchestration

- Orchestrator receives user requests and coordinates the workflow.
- Planner converts natural language into a valid task flow.
- Task Engine runs steps while enforcing limits, dependency checks, and retries.

## Layer 3: Specialized agents

- Research Agent collects context.
- Data Analyst Agent handles structured data inspection.
- Coding Agent prepares task execution suggestions.
- Reviewer Agent verifies answer completeness and missing evidence.

## Layer 4: Tools and safety boundary

- All tool calls pass through a registry and must be pre-registered.
- Tools are intentionally limited and validate inputs before executing.
- File access is restricted to safe local paths.

## Layer 5: Memory and knowledge

- SQLite stores sessions, messages, tasks, and knowledge documents.
- Chunker and retriever provide a simple local search layer.
- Content from documents is treated as untrusted data and never as system instructions.

## Layer 6: LLM provider abstraction

- Demo provider runs by default, with explicit knowledge of its limitations.
- A real provider can be added without rewriting orchestrators or tools.

## Safety posture

This project is designed for local use and demonstration quality. It is not a public-facing internet service without authentication and hardening.
