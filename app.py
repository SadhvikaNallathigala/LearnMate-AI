"""
app.py — AI Student Learning Assistant (Single File)
======================================================
A professional AI-powered educational tool.

Features:
  • Summarize Text
  • Explain Concept
  • Generate Model Questions
  • Generate Quiz
  • Learning Enhancements (keywords, objectives, interview Qs, exam tips)

AI Backend (priority waterfall):
  1. Ollama  — local LLM (Mistral, Llama 3, Gemma, Phi-3, …)
  2. Groq    — free cloud API (llama3-8b-8192)
  3. Smart Template Fallback — always works, no API needed

Run:
  pip install streamlit requests fpdf2 groq
  streamlit run app.py
"""

import re
import requests
import streamlit as st
from typing import Optional

# ══════════════════════════════════════════════════════════════════════════════
# SECTION 1 — AI BACKEND
# ══════════════════════════════════════════════════════════════════════════════

OLLAMA_URL = "http://localhost:11434/api/generate"
OLLAMA_MODELS = ["mistral", "llama3", "gemma", "phi3", "llama2"]


def call_ollama(prompt: str, model: str = "mistral"):
    try:
        print("=" * 50)
        print("USING MODEL:", model)

        resp = requests.post(
            OLLAMA_URL,
            json={"model": model, "prompt": prompt, "stream": False},
            timeout=120,
        )

        print("STATUS:", resp.status_code)
        print("RAW RESPONSE:")
        print(resp.text[:1000])

        resp.raise_for_status()

        data = resp.json()

        answer = data.get("response", "").strip()

        print("ANSWER LENGTH:", len(answer))

        return answer

    except Exception as e:
        print("OLLAMA ERROR:", str(e))
        return None


def get_available_ollama_model() -> Optional[str]:
    """Return the first available Ollama model name, or None."""
    try:
        resp = requests.get("http://localhost:11434/api/tags", timeout=5)
        if resp.status_code == 200:
            models = [m["name"].split(":")[0] for m in resp.json().get("models", [])]
            for preferred in OLLAMA_MODELS:
                if preferred in models:
                    return preferred
            return models[0] if models else None
    except Exception:
        pass
    return None


def call_groq(prompt: str, api_key: str) -> Optional[str]:
    """Call Groq's free-tier API (llama3-8b-8192)."""
    try:
        import groq

        client = groq.Groq(api_key=api_key)
        chat = client.chat.completions.create(
            messages=[{"role": "user", "content": prompt}],
            model="llama3-8b-8192",
            max_tokens=2048,
            temperature=0.7,
        )
        return chat.choices[0].message.content.strip()
    except Exception:
        return None


def smart_fallback(feature: str, topic: str) -> str:
    """
    Structured, content-aware fallback when no AI model is available.
    Uses the actual topic for all placeholder text — never fully generic.
    """
    t = topic.strip()
    short = t[:80] + ("..." if len(t) > 80 else "")

    if feature == "summarize":
        words = t.split()
        first_sent = " ".join(words[:30])
        return f"""## Summary

{first_sent}{"..." if len(words) > 30 else ""}

---

## Key Points

- **Core Idea:** {short}
- Understand the fundamental principles and terminology associated with this topic.
- Recognise real-world applications and where this concept appears in practice.
- Note the advantages, limitations, and any trade-offs involved.
- Be prepared to compare this concept with related alternatives.

---

## Exam Revision Notes

**Topic:** {short}
Focus on: definitions, applications, advantages vs limitations, and real-world examples.
Common exam angles: explain, compare, justify, or critically evaluate.
"""

    if feature == "explain":
        return f"""## Explanation: {short}

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
- Has scope boundaries -- not universally applicable in all contexts.
- Ongoing research may update or refine current understanding.

### Example
Consider a scenario where {short} is applied: in practice, one would observe the core
principles at work, producing results that align with theoretical predictions.

---
*Connect to Ollama or add a Groq API key in the sidebar for AI-generated explanations.*
"""

    if feature == "model_questions":
        return f"""## Model Questions: {short}

### Short Answer Questions (2-5 marks each)
1. Define **{short}** in your own words.
2. List two key characteristics of {short}.
3. Where is {short} commonly applied? Give one example.
4. What are the main advantages of {short}?
5. Mention one limitation or challenge associated with {short}.

---

### Long Answer Questions (10-15 marks each)
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
        return f"""## Quiz: {short}

### Multiple Choice Questions

**Q1. What best describes {short}?**
- A) A method used to solve unrelated problems
- B) A fundamental concept with defined principles and applications [ANSWER]
- C) An outdated theory with no modern relevance
- D) A term exclusive to one industry

**Q2. Which of the following is a key benefit of {short}?**
- A) It eliminates all complexity in the field
- B) It provides a structured approach to understanding key ideas [ANSWER]
- C) It requires no prior knowledge
- D) It applies only in theoretical settings

**Q3. {short} is MOST commonly associated with:**
- A) Irrelevant domains
- B) Its direct field of origin and closely related disciplines [ANSWER]
- C) Historical contexts only
- D) Experimental science exclusively

**Q4. Which statement about {short} is FALSE?**
- A) It has real-world applications
- B) It can be studied and learned
- C) It is completely without limitations [ANSWER]
- D) It has a defined scope

**Q5. A student studying {short} should focus on:**
- A) Memorising unrelated facts
- B) Definitions, applications, advantages, and examples [ANSWER]
- C) Ignoring its limitations
- D) Studying it in isolation from other topics

---

### True / False

1. **{short} has practical real-world applications.** -> TRUE
2. **{short} is only relevant in one narrow context.** -> FALSE
3. **Understanding {short} requires knowing its core principles.** -> TRUE

---

### Fill in the Blanks

1. **{short}** is a concept that involves __________ as its core principle.
   Answer: its defining mechanism or foundational idea

2. One real-world application of **{short}** is seen in the field of __________.
   Answer: its primary domain or industry
"""

    if feature == "enhancements":
        return f"""## Learning Enhancements: {short}

### Important Keywords
{short}, core principles, applications, advantages, limitations, examples,
definition, analysis, evaluation, comparison, methodology, framework

---

### Learning Objectives
By the end of studying **{short}**, you should be able to:
1. Define and explain {short} clearly in your own words.
2. Identify the key principles and components involved.
3. Apply knowledge of {short} to practical or hypothetical scenarios.
4. Evaluate the advantages and limitations critically.
5. Compare {short} with related concepts in the field.

---

### Interview Questions
1. "Walk me through what you know about {short}."
2. "Can you give a real-world example where {short} is used?"
3. "What challenges exist when working with {short}?"
4. "How would you explain {short} to someone with no background in this field?"
5. "What recent developments have changed how we think about {short}?"

---

### Exam Tips
- **Start with the definition** -- examiners reward clarity early in your answer.
- **Use examples** -- even one concrete example strengthens any answer.
- **Cover both sides** -- always mention advantages AND limitations.
- **Link to related topics** -- showing connections earns extra marks.
- **Time management** -- allocate time proportionally to marks per question.
"""

    return "Feature not recognised. Please select a valid option."


def generate_response(
    feature: str,
    topic: str,
    groq_api_key: str = "",
    use_ollama: bool = True,
) -> tuple[str, str]:
    """
    Generate a response using the best available AI backend.

    Returns:
        (response_text, model_name_used)
    """
    prompts = {
        "summarize": f"""You are an expert educational assistant. Given the study material or topic below, produce:
1. A concise summary (3-5 sentences).
2. Key Points as bullet points (at least 5 points).
3. A short "Exam Revision Notes" section.

Topic/Text: {topic}

Format with clear Markdown headings: ## Summary, ## Key Points, ## Exam Revision Notes""",
        "explain": f"""You are a student-friendly tutor. Explain the topic below clearly and thoroughly.
Use exactly these sections: Definition, Key Concepts, Real-World Applications, Advantages, Limitations, Example.

Topic: {topic}

Use simple language. Be thorough but accessible to a student.""",
        "model_questions": f"""You are an experienced teacher. Generate exam questions for the topic below.
Create exactly:
- 5 Short Answer Questions (2-5 marks each)
- 5 Long Answer Questions (10-15 marks each)
- 5 Viva/Oral Questions

Topic: {topic}

Number each question. Make questions specific and relevant to the topic.""",
        "quiz": f"""
You are an expert exam paper setter.

Generate a professional quiz on the topic:

{topic}

STRICT FORMAT:

# QUIZ: {topic}

## Multiple Choice Questions

Q1. Question

A) Option A

B) Option B

C) Option C

D) Option D

Q2. Question

A) Option A

B) Option B

C) Option C

D) Option D

Q3. Question

A) Option A

B) Option B

C) Option C

D) Option D

Q4. Question

A) Option A

B) Option B

C) Option C

D) Option D

Q5. Question

A) Option A

B) Option B

C) Option C

D) Option D

---

## True / False

Q6. Statement

Q7. Statement

Q8. Statement

---

## Fill in the Blanks

Q9. ________

Q10. ________

---

## Answers of Above Questions

Q1) Correct Option

Q2) Correct Option

Q3) Correct Option

Q4) Correct Option

Q5) Correct Option

Q6) True/False

Q7) True/False

Q8) True/False

Q9) Correct Answer

Q10) Correct Answer

IMPORTANT:
- Do NOT place answers after each question.
- Do NOT write "(Answer:)" beside questions.
- Show all answers only in the final answer section.
- Use proper spacing.
- Use markdown formatting.
- Questions must be specific to the topic.
""",
        "enhancements": f"""You are an educational content strategist. For the topic below, generate:
1. Important Keywords (10 relevant terms)
2. Learning Objectives (5 clear, measurable objectives)
3. Interview Questions (5 recruiter-style questions)
4. Exam Tips (5 specific, actionable tips)

Topic: {topic}

Use Markdown with clear section headers.""",
    }

    prompt = prompts.get(feature)
    if not prompt:
        return smart_fallback(feature, topic), "Template"

    if use_ollama:
        model = get_available_ollama_model()
        if model:
            result = call_ollama(prompt, model)
            if result and len(result.strip()) > 50:
                return result, f"Ollama ({model})"

    if groq_api_key:
        result = call_groq(prompt, groq_api_key)
        if result:
            return result, "Groq (llama3-8b)"

    return smart_fallback(feature, topic), "Smart Template"


# ══════════════════════════════════════════════════════════════════════════════
# SECTION 2 — PDF EXPORT
# ══════════════════════════════════════════════════════════════════════════════


def _markdown_to_plain(md: str) -> str:
    """Strip Markdown formatting and unsafe unicode for PDF (latin-1 only)."""
    text = re.sub(r"#{1,6}\s*", "", md)
    text = re.sub(r"\*\*(.*?)\*\*", r"\1", text)
    text = re.sub(r"\*(.*?)\*", r"\1", text)
    text = re.sub(r"`(.*?)`", r"\1", text)
    text = re.sub(r"\[([^\]]+)\]\([^\)]+\)", r"\1", text)
    for src, dst in {
        "\u2014": "-",
        "\u2013": "-",
        "\u2012": "-",
        "\u2019": "'",
        "\u2018": "'",
        "\u201c": '"',
        "\u201d": '"',
        "\u2022": "-",
        "\u00b7": "-",
        "\u2192": "->",
        "\u2190": "<-",
        "\u2713": "OK",
        "\u2714": "OK",
        "\u2705": "[YES]",
        "\u274c": "[NO]",
        "\u2717": "[NO]",
        "\u26a0": "(!)",
    }.items():
        text = text.replace(src, dst)
    text = text.encode("latin-1", errors="ignore").decode("latin-1")
    text = re.sub(r"^[-*]\s+", "- ", text, flags=re.MULTILINE)
    return text.strip()


def generate_pdf(title: str, content: str) -> Optional[bytes]:
    """
    Render title + Markdown content as a PDF.
    Returns PDF bytes on success, None if fpdf2 is not installed.
    """
    try:
        from fpdf import FPDF

        class PDF(FPDF):
            def header(self):
                self.set_font("Helvetica", "B", 12)
                self.set_text_color(30, 30, 80)
                self.cell(
                    0,
                    8,
                    "AI Student Learning Assistant",
                    align="C",
                    new_x="LMARGIN",
                    new_y="NEXT",
                )
                self.ln(2)

            def footer(self):
                self.set_y(-12)
                self.set_font("Helvetica", "I", 8)
                self.set_text_color(150, 150, 150)
                self.cell(0, 8, f"Page {self.page_no()}", align="C")

        pdf = PDF("P", "mm", "A4")
        pdf.set_margins(20, 20, 20)
        pdf.add_page()
        pdf.set_auto_page_break(auto=True, margin=25)

        # Title
        safe_title = title.encode("latin-1", errors="ignore").decode("latin-1")
        pdf.set_x(pdf.l_margin)
        pdf.set_font("Helvetica", "B", 14)
        pdf.set_text_color(20, 20, 100)
        pdf.multi_cell(0, 8, safe_title)
        pdf.ln(4)

        # Body
        for line in _markdown_to_plain(content).split("\n"):
            stripped = line.strip()
            if not stripped:
                pdf.ln(2)
                continue
            pdf.set_x(pdf.l_margin)
            if stripped.isupper() and len(stripped) < 60:
                pdf.set_font("Helvetica", "B", 11)
                pdf.set_text_color(30, 30, 100)
                pdf.multi_cell(0, 6, stripped)
            else:
                pdf.set_font("Helvetica", "", 10)
                pdf.set_text_color(40, 40, 40)
                pdf.multi_cell(0, 6, stripped)

        return bytes(pdf.output())
    except ImportError:
        return None
    except Exception:
        return None


# ══════════════════════════════════════════════════════════════════════════════
# SECTION 3 — STREAMLIT UI
# ══════════════════════════════════════════════════════════════════════════════

st.set_page_config(
    page_title="LearnMate AI",
    page_icon="🎓",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── Global CSS ────────────────────────────────────────────────────────────────
st.markdown(
    """
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');

html, body, [class*="css"] { font-family: 'Inter', sans-serif; }
#MainMenu, footer { visibility: hidden; }
.block-container { padding-top: 1.5rem; padding-bottom: 2rem; }

.hero {
    background: linear-gradient(135deg, #0f0c29 0%, #302b63 50%, #24243e 100%);
    border-radius: 16px;
    padding: 2.5rem 2rem;
    margin-bottom: 1.5rem;
    color: white;
    box-shadow: 0 8px 32px rgba(48,43,99,0.4);
}
.hero h1  { font-size: 2.2rem; font-weight: 700; margin: 0 0 0.4rem; letter-spacing: -0.5px; }
.hero p   { font-size: 1rem; opacity: 0.8; margin: 0; }
.hero .badge {
    display: inline-block;
    background: rgba(255,255,255,0.15);
    border: 1px solid rgba(255,255,255,0.25);
    border-radius: 20px;
    padding: 3px 12px;
    font-size: 0.78rem;
    margin-top: 0.8rem;
    margin-right: 6px;
}

.result-box {
    background: #fafbff;
    border: 1px solid #e2e8f0;
    border-left: 4px solid #6366f1;
    border-radius: 0 12px 12px 0;
    padding: 1.5rem 1.8rem;
    margin-top: 1rem;
}

.model-badge {
    display: inline-block;
    background: #ecfdf5;
    color: #065f46;
    border: 1px solid #6ee7b7;
    border-radius: 20px;
    padding: 2px 10px;
    font-size: 0.78rem;
    font-weight: 500;
    margin-bottom: 1rem;
}
.model-badge.template {
    background: #fefce8;
    color: #854d0e;
    border-color: #fde047;
}

.stat-pill {
    display: inline-block;
    background: #f1f5f9;
    border-radius: 20px;
    padding: 4px 14px;
    font-size: 0.82rem;
    color: #475569;
    margin-right: 6px;
    margin-top: 4px;
}

[data-testid="stSidebar"] {
    background: linear-gradient(180deg, #0f0c29 0%, #302b63 100%) !important;
}
[data-testid="stSidebar"] * { color: white !important; }
[data-testid="stSidebar"] .stSelectbox label,
[data-testid="stSidebar"] .stTextInput label {
    color: rgba(255,255,255,0.7) !important;
    font-size: 0.82rem !important;
    text-transform: uppercase;
    letter-spacing: 0.5px;
}

div[data-testid="stButton"] > button[kind="primary"] {
    background: linear-gradient(135deg, #6366f1, #8b5cf6) !important;
    border: none !important;
    border-radius: 10px !important;
    padding: 0.65rem 2rem !important;
    font-size: 1rem !important;
    font-weight: 600 !important;
    color: white !important;
    box-shadow: 0 4px 14px rgba(99,102,241,0.4) !important;
}

.stTabs [data-baseweb="tab-list"] {
    gap: 6px;
    background: #1e293b;
    border-radius: 12px;
    padding: 6px;
}

.stTabs [data-baseweb="tab"] {
    color: white !important;
    background: #334155;
    border-radius: 10px;
    padding: 10px 18px;
    font-weight: 600;
}

.stTabs [aria-selected="true"] {
    background: #8b5cf6 !important;
    color: white !important;
    box-shadow: 0 2px 8px rgba(139,92,246,0.5);
}
</style>
""",
    unsafe_allow_html=True,
)

# ── Session state defaults ────────────────────────────────────────────────────
for k, v in {
    "result": "",
    "result_title": "",
    "model_used": "",
    "generated": False,
}.items():
    if k not in st.session_state:
        st.session_state[k] = v

# ── Sidebar ───────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("## 🎓 LearnMate AI")
    st.markdown("---")

    ollama_model = get_available_ollama_model()
    if ollama_model:
        st.markdown(f"🟢 **Ollama** · `{ollama_model}` connected")
    else:
        st.markdown("🔴 **Ollama** · not detected")

    
    
    st.markdown("---")
    st.markdown("**Select Feature**")
    FEATURE_OPTIONS = {
        "📋 Summarize Text": "summarize",
        "💡 Explain Concept": "explain",
        "📚 Model Questions": "model_questions",
        "🧠 Generate Quiz": "quiz",
        "🚀 Learning Enhancements": "enhancements",
    }
    selected_label = st.selectbox(
        "Feature", list(FEATURE_OPTIONS.keys()), label_visibility="collapsed"
    )
    feature = FEATURE_OPTIONS[selected_label]

    st.markdown("---")
    st.caption("**AI priority:**")
    st.caption("1. Ollama (local LLM)")
    st.caption("2. Smart template fallback")
# ── Hero ──────────────────────────────────────────────────────────────────────
st.markdown(
    """
<div class="hero">
  <h1>🎓 LearnMate AI</h1>
  <p>Your Personal AI Study Companion</p>
  <span class="badge">📋 Summarize</span>
  <span class="badge">💡 Explain</span>
  <span class="badge">📚 Questions</span>
  <span class="badge">🧠 Quiz</span>
  <span class="badge">🚀 Enhancements</span>
</div>
""",
    unsafe_allow_html=True,
)

# ── Feature header ────────────────────────────────────────────────────────────
FEATURE_META = {
    "summarize": {
        "icon": "📋",
        "title": "Summarize Text",
        "desc": "Concise summary, key points, and exam revision notes.",
        "ph": "Paste a paragraph, chapter, or notes to summarise...",
    },
    "explain": {
        "icon": "💡",
        "title": "Explain Concept",
        "desc": "Definition, key concepts, applications, advantages, and examples.",
        "ph": "Enter a concept: 'Machine Learning', 'Photosynthesis', 'Newton's Laws'...",
    },
    "model_questions": {
        "icon": "📚",
        "title": "Model Questions",
        "desc": "5 short-answer + 5 long-answer + 5 viva questions for any topic.",
        "ph": "Enter a topic or subject to generate exam questions for...",
    },
    "quiz": {
        "icon": "🧠",
        "title": "Generate Quiz",
        "desc": "5 MCQs + 3 True/False + 2 Fill-in-the-Blank questions.",
        "ph": "Enter a topic to build a quiz around...",
    },
    "enhancements": {
        "icon": "🚀",
        "title": "Learning Enhancements",
        "desc": "Keywords, learning objectives, interview questions, and exam tips.",
        "ph": "Enter any topic to get full learning enhancement materials...",
    },
}
meta = FEATURE_META[feature]

col_icon, col_info = st.columns([1, 11])
with col_icon:
    st.markdown(
        f"<div style='font-size:2.5rem;padding-top:4px'>{meta['icon']}</div>",
        unsafe_allow_html=True,
    )
with col_info:
    st.markdown(f"### {meta['title']}")
    st.caption(meta["desc"])

# ── Input ─────────────────────────────────────────────────────────────────────
user_input = st.text_area(
    "Enter your topic or study material:",
    height=160,
    placeholder=meta["ph"],
    help="The more specific you are, the better the output.",
    key="user_input"
)
if user_input.strip():
    wc = len(user_input.split())
    cc = len(user_input)
    st.markdown(
        f'<span class="stat-pill">📝 {wc} words</span>'
        f'<span class="stat-pill">🔤 {cc} chars</span>',
        unsafe_allow_html=True,
    )

# ── Buttons ───────────────────────────────────────────────────────────────────
col_btn, col_clear = st.columns([3, 1])
with col_btn:
    generate = st.button(
        f"{meta['icon']} Generate {meta['title']}",
        type="primary",
        use_container_width=True,
    )
with col_clear:
    if st.button("🗑️ Clear", use_container_width=True):

        for key in [
            "user_input",
            "result",
            "result_title",
            "model_used",
            "generated"
        ]:
            if key in st.session_state:
                del st.session_state[key]

        st.rerun()

# ── Generation logic ──────────────────────────────────────────────────────────
if generate:
    if not user_input.strip():
        st.error("⚠️ Please enter a topic or study material before generating.")
    elif len(user_input.strip()) < 3:
        st.warning("⚠️ Input is too short. Enter a meaningful topic or text.")
    else:
        with st.spinner(f"Generating {meta['title']}..."):
           result, model_used = generate_response(
        feature=feature,
        topic=user_input.strip(),
        use_ollama=True,
) 
        st.session_state.result = result
        st.session_state.result_title = f"{meta['icon']} {meta['title']}"
        st.session_state.model_used = model_used
        st.session_state.generated = True

# ── Results display ───────────────────────────────────────────────────────────
if st.session_state.generated and st.session_state.result:
    st.markdown("---")

    model = st.session_state.model_used
    badge_class = (
        "template" if model in ("Smart Template", "Template", "template") else ""
    )
    badge_icon = "🤖" if not badge_class else "📄"
    st.markdown(
        f'<span class="model-badge {badge_class}">{badge_icon} Generated by: {model}</span>',
        unsafe_allow_html=True,
    )

    tab_fmt, tab_raw, tab_dl = st.tabs(
        ["📖 Formatted", "📋 Copy Text", "⬇️ Download PDF"]
    )

    with tab_fmt:
        formatted_result = st.session_state.result

        formatted_result = formatted_result.replace("\nQ", "\n\nQ")
        formatted_result = formatted_result.replace("A)", "\nA)")
        formatted_result = formatted_result.replace("B)", "\nB)")
        formatted_result = formatted_result.replace("C)", "\nC)")
        formatted_result = formatted_result.replace("D)", "\nD)")

        st.markdown(formatted_result)
    with tab_raw:
        st.markdown("**Copy the text below:**")
        st.code(st.session_state.result, language=None)
        st.caption("Use the copy icon in the top-right of the code block above.")

    with tab_dl:
        st.markdown("**Download your results as a PDF:**")
        topic_short = user_input[:60] + ("..." if len(user_input) > 60 else "")
        pdf_bytes = generate_pdf(
            f"{meta['title']} — {topic_short}", st.session_state.result
        )

        if pdf_bytes:
            st.download_button(
                label="⬇️ Download PDF",
                data=pdf_bytes,
                file_name=f"learning_assistant_{feature}.pdf",
                mime="application/pdf",
                use_container_width=True,
            )
        else:
            st.info(
                "PDF export requires **fpdf2**. Run:\n```\npip install fpdf2\n```\nthen restart the app."
            )
            st.download_button(
                label="⬇️ Download as .txt (fallback)",
                data=st.session_state.result.encode("utf-8"),
                file_name=f"learning_assistant_{feature}.txt",
                mime="text/plain",
                use_container_width=True,
            )

# ── Getting started tips (shown before first generation) ─────────────────────
if not st.session_state.generated:
    st.markdown("---")
    st.markdown("### 💡 Getting Started")
    c1, c2, c3 = st.columns(3)
    with c1:
        st.markdown("""**📥 What to enter**
- A concept name *(e.g. Recursion)*
- A full paragraph or notes
- A chapter title or subject
- Any topic you are studying""")
    with c2:
        st.markdown("""**🚀 Power tips**
- Be specific for better results
- Try all 5 features per topic
- Use PDF download to save notes
- Include context when possible""")
    with c3:
        st.markdown("""**🤖 Enable AI**
- Install Ollama locally
- Run: `ollama pull mistral`
- Ensure Ollama is running
- Start generating AI-powered content
""")

# ── Footer ────────────────────────────────────────────────────────────────────
st.markdown("---")
c1, c2, c3 = st.columns(3)
c1.caption("🎓 LearnMate AI")
c2.caption("Built with Streamlit · Ollama ")
c3.caption("Deploy free on Streamlit Cloud")
