"""
ai_handler.py
-------------
Handles all AI model interactions.
Priority order:
  1. Ollama (local LLM — Mistral, Llama 3, Gemma, etc.)
  2. Groq API (free tier, very fast)
  3. Intelligent template fallback (structured, content-aware)
"""

import re
import requests
from typing import Optional


# ─────────────────────────────────────────────
# Ollama (Local LLM)
# ─────────────────────────────────────────────

OLLAMA_URL = "http://localhost:11434/api/generate"
OLLAMA_MODELS = ["mistral", "llama3", "gemma", "phi3", "llama2"]


def call_ollama(prompt: str, model: str = "mistral") -> Optional[str]:
    """Send a prompt to a locally running Ollama model."""
    try:
        payload = {
            "model": model,
            "prompt": prompt,
            "stream": False
        }
        resp = requests.post(OLLAMA_URL, json=payload, timeout=60)
        resp.raise_for_status()
        data = resp.json()
        return data.get("response", "").strip()
    except Exception:
        return None


def get_available_ollama_model() -> Optional[str]:
    """Return the first available Ollama model, or None."""
    try:
        resp = requests.get("http://localhost:11434/api/tags", timeout=5)
        if resp.status_code == 200:
            models = [m["name"].split(":")[0] for m in resp.json().get("models", [])]
            for preferred in OLLAMA_MODELS:
                if preferred in models:
                    return preferred
            if models:
                return models[0]
    except Exception:
        pass
    return None


# ─────────────────────────────────────────────
# Groq API (Free Tier)
# ─────────────────────────────────────────────

def call_groq(prompt: str, api_key: str) -> Optional[str]:
    """Call Groq's free-tier LLM API (llama3-8b-8192)."""
    try:
        import groq
        client = groq.Groq(api_key=api_key)
        chat = client.chat.completions.create(
            messages=[{"role": "user", "content": prompt}],
            model="llama3-8b-8192",
            max_tokens=2048,
            temperature=0.7
        )
        return chat.choices[0].message.content.strip()
    except Exception:
        return None


# ─────────────────────────────────────────────
# Intelligent Template Fallback
# ─────────────────────────────────────────────

def smart_fallback(feature: str, topic: str) -> str:
    """
    Content-aware fallback responses.
    Uses the actual topic to produce structured, useful output
    rather than generic placeholders.
    """
    t = topic.strip()
    short = t[:80] + ("..." if len(t) > 80 else "")

    if feature == "summarize":
        words = t.split()
        first_sent = " ".join(words[:30])
        return f"""## 📋 Summary

{first_sent}{"..." if len(words) > 30 else ""}

---

## 🔑 Key Points

- **Core Idea:** {short}
- Understand the fundamental principles and terminology associated with this topic.
- Recognise real-world applications and where this concept appears in practice.
- Note the advantages, limitations, and any trade-offs involved.
- Be prepared to compare this concept with related alternatives.

---

## 📝 Exam Revision Notes

> **Topic:** {short}
> Focus on: definitions, applications, advantages vs limitations, and real-world examples.
> Common exam angles: explain, compare, justify, or critically evaluate.
"""

    if feature == "explain":
        return f"""## 💡 Explanation: {short}

### Definition
**{short}** refers to a concept or topic that involves key principles important in its field.
Understanding this requires grasping its foundational ideas and how they interconnect.

### Key Concepts
- **Principle 1:** The core mechanism or idea behind {short}.
- **Principle 2:** Supporting theories or models that describe its behaviour.
- **Principle 3:** The conditions under which {short} operates or applies.

### Real-World Applications
- Used in industry for solving practical problems related to {short}.
- Found in academic and research contexts as a foundational topic.
- Applied in technology, science, or social domains depending on the field.

### Advantages
- Provides a clear framework for understanding complex problems.
- Enables efficient solutions in its area of application.
- Well-documented and widely studied.

### Limitations
- May require prerequisite knowledge to fully understand.
- Has scope boundaries — not universally applicable in all contexts.
- Ongoing research may update or refine current understanding.

### Example
Consider a scenario where {short} is applied: in practice, one would observe the core
principles at work, producing results that align with theoretical predictions.

---
*⚠️ Connect to Ollama or add a Groq API key in the sidebar for AI-generated explanations.*
"""

    if feature == "model_questions":
        return f"""## 📚 Model Questions — {short}

### Short Answer Questions (2–5 marks each)
1. Define **{short}** in your own words.
2. List two key characteristics of {short}.
3. Where is {short} commonly applied? Give one example.
4. What are the main advantages of {short}?
5. Mention one limitation or challenge associated with {short}.

---

### Long Answer Questions (10–15 marks each)
1. Explain **{short}** in detail. Include its definition, working principles, and significance.
2. Discuss the real-world applications of {short} with suitable examples.
3. Compare {short} with a related concept, highlighting similarities and differences.
4. Critically evaluate the advantages and limitations of {short}.
5. How has {short} evolved over time? Discuss its historical development and current relevance.

---

### Viva / Oral Questions
1. Can you explain {short} in one sentence?
2. What would happen if {short} did not exist or was unavailable?
3. How does {short} relate to other concepts in the same field?
4. What is the most important thing to remember about {short}?
5. If you had to teach {short} to a beginner, how would you start?
"""

    if feature == "quiz":
        return f"""## 🧠 Quiz — {short}

### Multiple Choice Questions

**Q1. What best describes {short}?**
- A) A method used to solve unrelated problems
- B) A fundamental concept with defined principles and applications ✅
- C) An outdated theory with no modern relevance
- D) A term exclusive to one industry

**Q2. Which of the following is a key benefit of {short}?**
- A) It eliminates all complexity in the field
- B) It provides a structured approach to understanding key ideas ✅
- C) It requires no prior knowledge
- D) It applies only in theoretical settings

**Q3. {short} is MOST commonly associated with:**
- A) Irrelevant domains
- B) Its direct field of origin and closely related disciplines ✅
- C) Historical contexts only
- D) Experimental science exclusively

**Q4. Which statement about {short} is FALSE?**
- A) It has real-world applications
- B) It can be studied and learned
- C) It is completely without limitations ✅
- D) It has a defined scope

**Q5. A student studying {short} should focus on:**
- A) Memorising unrelated facts
- B) Definitions, applications, advantages, and examples ✅
- C) Ignoring its limitations
- D) Studying it in isolation from other topics

---

### True / False

1. **{short} has practical real-world applications.** → ✅ **True**
2. **{short} is only relevant in one narrow context.** → ❌ **False**
3. **Understanding {short} requires knowing its core principles.** → ✅ **True**

---

### Fill in the Blanks

1. **{short}** is a concept that involves __________ as its core principle.
   → *Answer: its defining mechanism or foundational idea*

2. One real-world application of **{short}** is seen in the field of __________.
   → *Answer: its primary domain or industry*
"""

    if feature == "enhancements":
        return f"""## 🚀 Learning Enhancements — {short}

### 🏷️ Important Keywords
`{short}` · `core principles` · `applications` · `advantages` · `limitations` · `examples` · `definition` · `analysis` · `evaluation` · `comparison`

---

### 🎯 Learning Objectives
By the end of studying **{short}**, you should be able to:
1. Define and explain {short} clearly in your own words.
2. Identify the key principles and components involved.
3. Apply knowledge of {short} to practical or hypothetical scenarios.
4. Evaluate the advantages and limitations critically.
5. Compare {short} with related concepts in the field.

---

### 💼 Interview Questions
1. *"Walk me through what you know about {short}."*
2. *"Can you give a real-world example where {short} is used?"*
3. *"What challenges exist when working with {short}?"*
4. *"How would you explain {short} to someone with no background in this field?"*
5. *"What recent developments have changed how we think about {short}?"*

---

### 📌 Exam Tips
- **Start with the definition** — examiners reward clarity early in your answer.
- **Use examples** — even one concrete example strengthens any answer.
- **Cover both sides** — always mention advantages AND limitations.
- **Link to related topics** — showing connections earns extra marks.
- **Time management** — allocate time proportionally to marks per question.
"""

    return "Feature not recognised. Please select a valid option."


# ─────────────────────────────────────────────
# Main Entry Point
# ─────────────────────────────────────────────

def generate_response(
    feature: str,
    topic: str,
    groq_api_key: str = "",
    use_ollama: bool = True
) -> tuple[str, str]:
    """
    Generate a response for the given feature and topic.

    Returns:
        (response_text, model_used)
    """
    prompt_map = {
        "summarize": f"""You are an expert educational assistant. Given the following study material or topic, produce:
1. A concise summary (3-5 sentences).
2. Key Points as bullet points (at least 5).
3. A short "Exam Revision Notes" section.

Topic/Text:
{topic}

Format your response with clear Markdown headings: ## Summary, ## Key Points, ## Exam Revision Notes""",

        "explain": f"""You are a student-friendly tutor. Explain the following topic clearly and thoroughly.
Structure your response with these exact sections:
- Definition
- Key Concepts
- Real-World Applications
- Advantages
- Limitations
- Example

Topic: {topic}

Use simple language. Be thorough but accessible.""",

        "model_questions": f"""You are an experienced teacher. Generate model exam questions for the topic below.
Create exactly:
- 5 Short Answer Questions (worth 2-5 marks each)
- 5 Long Answer Questions (worth 10-15 marks each)
- 5 Viva/Oral Questions

Topic: {topic}

Number each question clearly. Make questions specific to the topic.""",

        "quiz": f"""You are a quiz creator. Generate an interactive quiz for the topic below.
Create exactly:
- 5 Multiple Choice Questions (each with 4 options, mark the correct answer with ✅)
- 3 True/False Questions (state True or False answer)
- 2 Fill-in-the-Blank Questions (provide the answer)

Topic: {topic}

Make all questions directly relevant to the topic.""",

        "enhancements": f"""You are an educational content strategist. For the topic below, generate:
1. Important Keywords (10 relevant terms as a comma-separated list)
2. Learning Objectives (5 clear, measurable objectives)
3. Interview Questions (5 questions a recruiter might ask)
4. Exam Tips (5 specific tips for this topic)

Topic: {topic}

Use Markdown formatting with clear section headers.""",
    }

    prompt = prompt_map.get(feature, "")
    if not prompt:
        return smart_fallback(feature, topic), "template"

    # Try Ollama first
    if use_ollama:
        model = get_available_ollama_model()
        if model:
            result = call_ollama(prompt, model)
            if result:
                return result, f"Ollama ({model})"

    # Try Groq
    if groq_api_key:
        result = call_groq(prompt, groq_api_key)
        if result:
            return result, "Groq (llama3-8b)"

    # Fallback
    return smart_fallback(feature, topic), "Smart Template"
