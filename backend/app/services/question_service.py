import json
import random
from openai import OpenAI
from app.core.config import settings


class QuestionService:
    def __init__(self):
        self.client = OpenAI(api_key=settings.OPENAI_API_KEY) if settings.OPENAI_API_KEY else None

    def generate_question(
        self,
        role: str,
        profile: dict,
        contexts: list[dict],
        previous_qa: list[dict]
    ) -> dict:
        context_text = "\n\n".join(c.get("content", "") for c in contexts)[:3500]

        skills_list = profile.get("skills", [])
        projects_list = profile.get("projects", [])

        skills = ", ".join(skills_list) or "not clearly found"
        projects = "; ".join(projects_list[:3]) or "not clearly found"

        asked_questions = [x.get("question", "") for x in previous_qa]
        asked = "\n".join(
            [f"Q: {x.get('question', '')}\nA: {x.get('answer') or ''}" for x in previous_qa[-3:]]
        )

        # Fallback mode when OpenAI API key is not available
        if not self.client:
            used_topics = [x.get("topic") for x in previous_qa if x.get("topic")]

            available_topics = [s for s in skills_list if s not in used_topics]

            if available_topics:
                topic = available_topics[0]
            elif skills_list:
                topic = skills_list[len(previous_qa) % len(skills_list)]
            else:
                topic = f"{role} fundamentals"

            question_templates = [
                f"Explain how you used {topic} in one of your projects and what problem it solved.",
                f"For the {role} role, describe one real-world use case of {topic}. What trade-off would you consider?",
                f"How would you validate a solution built using {topic}? Mention suitable metrics or testing methods.",
                f"What challenges can occur while applying {topic} in production, and how would you handle them?",
                f"Explain the concept of {topic} with an example from your resume or project work.",
                f"How would you improve performance, scalability, or reliability in a project that uses {topic}?",
                f"What mistakes should be avoided while using {topic} in a real-world system?"
            ]

            index = len(previous_qa) % len(question_templates)
            question = question_templates[index]

            # Extra safety to reduce repeated questions
            if question in asked_questions:
                remaining = [q for q in question_templates if q not in asked_questions]
                question = remaining[0] if remaining else random.choice(question_templates)

            return {
                "question": question,
                "topic": topic,
                "difficulty": "medium",
                "reasoning_trace": (
                    "Generated locally because OpenAI API key was not configured. "
                    "Question was selected using resume skills, selected role, and previous interview history."
                ),
                "trace": {
                    "used_context": context_text[:900],
                    "mode": "local-fallback"
                }
            }

        prompt = f"""
You are an expert technical interviewer. Generate ONE new interview question.

Role: {role}

Candidate skills:
{skills}

Candidate projects:
{projects}

Previous QA:
{asked}

Grounding context from knowledge base:
{context_text}

Rules:
- Ask only one question.
- Do not repeat any previous question.
- Make it role-specific and influenced by the resume.
- Avoid generic HR questions.
- Prefer conceptual + applied depth.
- The question must test real understanding, not memorization.
- Return valid JSON only.
- JSON keys must be: question, topic, difficulty, reasoning_trace.
"""

        try:
            res = self.client.chat.completions.create(
                model=settings.LLM_MODEL,
                messages=[{"role": "user", "content": prompt}],
                temperature=0.5,
            )

            raw = res.choices[0].message.content

            try:
                parsed = json.loads(raw)
            except Exception:
                parsed = {
                    "question": raw,
                    "topic": "mixed",
                    "difficulty": "medium",
                    "reasoning_trace": "LLM output was not strict JSON"
                }

            if parsed.get("question") in asked_questions:
                parsed["question"] = (
                    f"Based on your previous answers, explain another practical challenge related to "
                    f"{parsed.get('topic', role)} and how you would solve it."
                )

            parsed["trace"] = {
                "used_context": context_text[:900],
                "mode": "openai"
            }

            return parsed

        except Exception as e:
            topic = skills_list[len(previous_qa) % len(skills_list)] if skills_list else f"{role} fundamentals"

            return {
                "question": f"Explain one practical project where you used {topic}. What was your approach, challenge, and validation method?",
                "topic": topic,
                "difficulty": "medium",
                "reasoning_trace": f"Fallback question generated because LLM call failed: {str(e)}",
                "trace": {
                    "used_context": context_text[:900],
                    "mode": "error-fallback"
                }
            }

    def summarize(self, role: str, profile: dict, qa: list[dict]) -> str:
        answered = [x for x in qa if x.get("answer")]

        if not answered:
            return "No answers were submitted yet."

        topics = sorted({x.get("topic") or "general" for x in answered})

        strong_answers = 0
        short_answers = 0

        for item in answered:
            answer = item.get("answer", "")
            word_count = len(answer.split())

            if word_count >= 35:
                strong_answers += 1
            else:
                short_answers += 1

        return (
            f"Interview summary for {role}: {len(answered)} answers recorded. "
            f"Covered topics: {', '.join(topics)}. "
            f"{strong_answers} answer(s) showed good explanation depth, while "
            f"{short_answers} answer(s) may need more detail. "
            "Basic insight: review conceptual accuracy, project relevance, examples, trade-off awareness, "
            "and communication clarity."
        )