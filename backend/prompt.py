"""
Prompt builder — assembles the final prompt sent to the LLM.

Takes the user question + retrieved corpus chunks and produces a
structured system + user message list for llama-cpp-python's
create_chat_completion API.
"""

SYSTEM_PROMPT = """You are a WASSCE/BECE exam tutor for West African secondary-school students.
You help students understand Mathematics and Integrated Science.
When answering, always show step-by-step working so the student can follow the reasoning.
Be accurate, clear, and encouraging."""


def build_prompt(question: str, retrieved: list[dict]) -> list[dict]:
    """
    Build a chat message list with relevant corpus examples in context.
    Returns a list of {role, content} dicts for create_chat_completion.
    """
    if retrieved:
        examples = []
        for i, r in enumerate(retrieved, 1):
            examples.append(
                f"Example {i} ({r['exam']} {r['subject']} — {r['topic']}):\n"
                f"Q: {r['question'].strip()}\n"
                f"Working: {r['solution'].strip()}\n"
                f"Answer: {r['answer'].strip()}"
            )
        context_block = (
            "Here are some relevant worked examples from the WASSCE/BECE syllabus "
            "that may help you answer the question:\n\n"
            + "\n\n".join(examples)
            + "\n\nUsing the above as guidance, now answer the student's question "
            "with full step-by-step working."
        )
    else:
        context_block = "Answer the student's question with full step-by-step working."

    return [
        {"role": "system", "content": SYSTEM_PROMPT},
        {
            "role": "user",
            "content": f"{context_block}\n\nStudent's question:\n{question.strip()}",
        },
    ]
