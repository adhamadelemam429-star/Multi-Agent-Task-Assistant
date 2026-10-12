from __future__ import annotations

from typing import Any

from src.llm.base_provider import BaseLLMProvider


class DemoLLMProvider(BaseLLMProvider):
    name = "demo"

    def generate_response(self, prompt: str, **kwargs: Any) -> str:
        prompt_lower = prompt.lower()
        is_arabic = any("\u0600" <= character <= "\u06ff" for character in prompt)
        if any(term in prompt_lower for term in ("csv", "excel", "spreadsheet", "اكسل", "إكسل", "جدول بيانات")):
            if is_arabic:
                return "وضع Demo: ارفع ملف CSV أو Excel أولًا، ثم أرسل طلب التحليل لأتمكن من تلخيص الصفوف والأعمدة والقيم الناقصة."
            return "Demo mode: I detected a CSV/data analysis task. I would validate the file, inspect schema, summarize missing values, and produce a brief report with clear limits."
        if any(term in prompt_lower for term in ("خطة", "خطوات", "plan", "steps")):
            if not is_arabic:
                return (
                    "A 3-step plan for a small app:\n"
                    "1. Define the app's goal, core features, and a simple interface.\n"
                    "2. Build the interface and main behavior, adding suitable data storage.\n"
                    "3. Test common cases, fix issues, and prepare the app to run."
                )
            return (
                "خطة من 3 خطوات لإنشاء تطبيق صغير:\n"
                "1. حدد هدف التطبيق وميزاته الأساسية وارسم واجهته.\n"
                "2. نفّذ الواجهة والوظائف الرئيسية، وأضف تخزينًا مناسبًا للبيانات.\n"
                "3. اختبر الحالات الشائعة والأخطاء، ثم أصلحها وجهّز التطبيق للتشغيل."
            )
        if any(term in prompt_lower for term in ("rag", "استرجاع معزز", "توليد معزز بالاسترجاع")):
            if is_arabic:
                return "RAG هو التوليد المعزز بالاسترجاع: يبحث النظام أولًا في مستندات المعرفة عن مقاطع مناسبة، ثم يستخدمها لصياغة الإجابة. في هذا المشروع يتم البحث محليًا بتشابه الكلمات، من دون نموذج لغوي خارجي في Demo mode."
            return "RAG (retrieval-augmented generation) retrieves relevant passages from a knowledge source and provides them as context for an answer. This project's Demo mode uses local token similarity and no external language model."
        if any(term in prompt_lower for term in ("code", "python", "كود", "بايثون", "برمج", "اكتب برنامج")):
            if any(term in prompt_lower for term in ("يطبع", "اطبع", "print")) and any(
                term in prompt_lower for term in ("مرحبا", "hello")
            ):
                greeting = "مرحبا" if is_arabic else "Hello, world!"
                return f'```python\nprint("{greeting}")\n```'
            if is_arabic:
                return "وضع Demo: فهمت أنه طلب برمجي. اذكر اللغة والسلوك المطلوبين بوضوح؛ ويمكنني في Demo mode تقديم أمثلة صغيرة وخطة تنفيذ، لكنني لا أنفذ تغييرات تلقائيًا."
            return "Demo mode: I detected a coding task. I would create a short implementation plan, inspect the workspace, and propose a minimal safe solution."
        if is_arabic:
            return "وضع Demo لا يملك نموذجًا لغويًا عامًا. أستطيع تنفيذ الحسابات، إعداد خطة أساسية، وإرشادك لاستخدام أدوات الملفات والبيانات المحلية."
        return "Demo mode: I can support planning, tool execution, and structured result generation without an external LLM provider."

    def generate_structured_output(self, prompt: str, schema: Any | None = None, **kwargs: Any) -> dict[str, Any]:
        return {
            "provider": "demo",
            "summary": self.generate_response(prompt, **kwargs),
            "mode": "demo",
            "status": "ok",
        }

    def is_available(self) -> bool:
        return True
