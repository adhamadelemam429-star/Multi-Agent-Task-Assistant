from __future__ import annotations

from pathlib import Path

from fastapi.testclient import TestClient

from src.api.main import app
from src.core.orchestrator import Orchestrator
from src.core.planner import Planner
from src.core.task_engine import TaskEngine
from src.llm.demo_provider import DemoLLMProvider
from src.memory.session_manager import SessionManager
from src.tools.calculator import safe_calculate
from src.tools.csv_analyzer import analyze_csv
from src.tools.document_reader import read_text_file
from src.tools.registry import execute_tool
from src.tools.text_search import search_text


def test_calculator_success():
    assert safe_calculate("2 + 3 * 4") == 14.0


def test_orchestrator_answers_arithmetic_in_chat():
    result = Orchestrator().handle_request("احسب 4*25")
    assert result["response"] == "نتيجة الحساب: 100"
    assert result["execution"]["tool_results"][0]["result"] == 100.0


def test_orchestrator_explains_arithmetic_in_arabic():
    result = Orchestrator().handle_request("احسب 12 + 8 ثم اشرح النتيجة")
    assert result["response"] == "نتيجة الحساب: 20\nالشرح: حسبت التعبير 12 + 8، والناتج هو 20."


def test_orchestrator_returns_arabic_plan_in_demo_mode():
    result = Orchestrator().handle_request("اعمل لي خطة 3 خطوات لإنشاء تطبيق صغير")
    assert result["response"].startswith("خطة من 3 خطوات")
    assert "3. اختبر" in result["response"]


def test_demo_provider_classifies_requests_without_execution_metadata():
    provider = DemoLLMProvider()
    assert "print(\"مرحبا\")" in provider.generate_response("اكتب كود بايثون يطبع مرحبا")
    assert "local token similarity" in provider.generate_response("What is RAG?")
    assert "ارفع ملف CSV" in provider.generate_response("حلل ملف CSV")


def test_demo_provider_does_not_treat_unrelated_requests_as_plans():
    provider = DemoLLMProvider()
    response = provider.generate_response("ما الوقت الآن؟")
    assert "خطة من 3 خطوات" not in response
    assert "نموذجًا لغويًا عامًا" in response


def test_orchestrator_returns_local_datetime_from_tool():
    result = Orchestrator().handle_request("ما الوقت الآن؟")
    assert result["response"].startswith("التاريخ والوقت المحلي:")
    assert result["execution"]["tool_results"][0]["tool_name"] == "datetime_tool"


def test_calculator_invalid_expression():
    try:
        safe_calculate("__import__('os').system('echo hi')")
        assert False, "expected ValueError"
    except ValueError:
        pass


def test_text_search_matches():
    text = "Alpha beta gamma\nBeta delta\nGamma" 
    matches = search_text(text, "beta")
    assert matches
    assert any("beta" in item["match"].lower() for item in matches)


def test_document_reader_valid_file(tmp_path):
    file_path = tmp_path / "sample.txt"
    file_path.write_text("This is a sample file.", encoding="utf-8")
    payload = read_text_file(str(file_path), allowed_base_dir=str(tmp_path))
    assert payload["content"] == "This is a sample file."


def test_document_reader_rejects_traversal(tmp_path):
    outside = tmp_path / "outside.txt"
    outside.write_text("hello", encoding="utf-8")
    base_dir = tmp_path / "safe"
    base_dir.mkdir()
    try:
        read_text_file(str(outside), allowed_base_dir=str(base_dir))
        assert False, "expected ValidationError"
    except Exception:
        pass


def test_csv_analysis_valid(tmp_path):
    sample = tmp_path / "sample.csv"
    sample.write_text("name,score\nAlice,10\nBob,20\n", encoding="utf-8")
    result = analyze_csv(str(sample))
    assert result["row_count"] == 2
    assert result["column_count"] == 2


def test_registry_rejects_unknown_tool():
    try:
        execute_tool("not_a_real_tool", {})
        assert False, "expected ValidationError"
    except Exception:
        pass


def test_planner_creates_valid_plan():
    plan = Planner().create_plan("Analyze CSV sales data and write a report.")
    assert plan.plan_id
    assert plan.steps


def test_task_engine_works_with_dependencies():
    engine = TaskEngine(max_steps=5)
    plan = Planner().create_plan("Analyze data")
    result = engine.execute_plan(plan, {"execute_tool": True})
    assert result["status"] == "completed"


def test_session_manager_round_trip():
    session_manager = SessionManager()
    session = session_manager.create_session(language="en", mode="demo")
    session_manager.save_message(session["session_id"], "user", "hello")
    history = session_manager.get_conversation_history(session["session_id"])
    assert len(history) == 1
    session_manager.clear_session(session["session_id"])
    assert session_manager.get_conversation_history(session["session_id"]) == []


def test_api_healthcheck():
    client = TestClient(app)
    r = client.get("/health")
    assert r.status_code == 200
    assert r.json()["status"] == "ok"


def test_api_chat_requires_session():
    client = TestClient(app)
    r = client.post("/api/v1/chat", json={"session_id": "missing", "message": "hello"})
    assert r.status_code == 404


def test_end_to_end_csv_analysis_flow(tmp_path):
    csv_path = tmp_path / "sales.csv"
    csv_path.write_text("region,sales\nA,10\nB,\nC,30\n", encoding="utf-8")

    plan = Planner().create_plan("Analyze a CSV sales file and write a short report.")
    assert plan.steps

    analysis = execute_tool("csv_analyzer", {"file_path": str(csv_path)})
    assert analysis["status"] == "success"
    assert analysis["result"]["row_count"] == 3

    report = execute_tool(
        "report_writer",
        {"content": "# Sales Summary\n\n- Rows analyzed: 3\n- Missing values: 1\n", "output_dir": str(tmp_path / "outputs")},
    )
    assert report["status"] == "success"
    report_path = tmp_path / "outputs"
    assert report_path.exists()

    engine = TaskEngine(max_steps=5)
    result = engine.execute_plan(plan, {"execute_tool": True})
    assert result["status"] == "completed"
