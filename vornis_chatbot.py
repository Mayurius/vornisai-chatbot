"""
vornis_chatbot.py - AI Chatbot module for VornisAI (Streamlit).

The chatbot can call three tools that map to your other modules:
    get_planet_data              -> Planetary Analysis
    compare_planets              -> Comparison
    predict_mission_feasibility  -> ML Mission Feasibility Model

Usage:
    from vornis_chatbot import render_vornis_chatbot
    render_vornis_chatbot()

Env vars: ANTHROPIC_API_KEY (required), CHATBOX_MODEL (optional).
"""

import json
import os

import anthropic
import streamlit as st

from tools import TOOLS, TOOL_FUNCTIONS

MODEL = os.getenv("CHATBOX_MODEL", "claude-sonnet-5-5")
MAX_TOOL_ROUNDS = 5
MAX_HISTORY = 30

SYSTEM_PROMPT = """You are Vornis AI, the assistant inside VornisAI, a platform for \
planetary analysis, planet comparison and ML-based mission feasibility prediction.

- Use your tools whenever the user asks about specific planets, comparisons, or \
whether a mission is feasible. Do not guess numbers that a tool can provide.
- Explain results in clear language, state units, and mention that feasibility \
scores are model estimates, not guarantees.
- If a tool returns an error or the planet is unknown, say so plainly.
- For general space-science questions you may answer directly. Keep answers concise."""

# --------------------------------------------------------------------------
# 2. CHAT UI + TOOL LOOP
# --------------------------------------------------------------------------


@st.cache_resource
def _client() -> anthropic.Anthropic:
    key = os.getenv("ANTHROPIC_API_KEY")
    if not key:
        st.error("ANTHROPIC_API_KEY is not set. Add it in Railway > Variables.")
        st.stop()
    return anthropic.Anthropic(api_key=key)


def _run_tool(name: str, args: dict) -> str:
    fn = TOOL_FUNCTIONS.get(name)
    if not fn:
        return json.dumps({"error": f"Unknown tool {name}"})
    try:
        return json.dumps(fn(**args))
    except Exception as e:  # never let a tool crash the chat
        return json.dumps({"error": f"{type(e).__name__}: {e}"})


def render_vornis_chatbot(key: str = "vornis_chat") -> None:
    ui_key, api_key = f"{key}_ui", f"{key}_api"
    st.session_state.setdefault(ui_key, [])   # what the user sees
    st.session_state.setdefault(api_key, [])  # full API history incl. tool blocks

    top = st.columns([5, 1])
    top[0].subheader("Vornis AI Assistant")
    if top[1].button("Clear", key=f"{key}_clear"):
        st.session_state[ui_key], st.session_state[api_key] = [], []
        st.rerun()

    if not st.session_state[ui_key]:
        st.caption("Try: 'Compare Mars and Venus' or 'Is a Mars lander feasible?'")

    for m in st.session_state[ui_key]:
        with st.chat_message(m["role"]):
            st.markdown(m["content"])

    prompt = st.chat_input("Ask about planets, comparisons, or mission feasibility...", key=f"{key}_input")
    if not prompt:
        return

    st.session_state[ui_key].append({"role": "user", "content": prompt})
    st.session_state[api_key].append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        placeholder = st.empty()
        shown = ""
        try:
            for _ in range(MAX_TOOL_ROUNDS):
                with _client().messages.stream(
                    model=MODEL,
                    max_tokens=1024,
                    system=SYSTEM_PROMPT,
                    tools=TOOLS,
                    messages=st.session_state[api_key][-MAX_HISTORY:],
                ) as stream:
                    for text in stream.text_stream:
                        shown += text
                        placeholder.markdown(shown + "▌")
                    final = stream.get_final_message()

                st.session_state[api_key].append({"role": "assistant", "content": final.content})
                if final.stop_reason != "tool_use":
                    break

                results = []
                for block in final.content:
                    if block.type == "tool_use":
                        with st.status(f"Running {block.name}...", expanded=False) as status:
                            out = _run_tool(block.name, block.input)
                            st.code(out, language="json")
                            status.update(label=f"Used {block.name}", state="complete")
                        results.append({"type": "tool_result", "tool_use_id": block.id, "content": out})
                st.session_state[api_key].append({"role": "user", "content": results})
                shown += "\n\n" if shown else ""

            placeholder.markdown(shown)
        except anthropic.RateLimitError:
            shown = "Too many requests right now. Please try again shortly."
            placeholder.warning(shown)
        except anthropic.APIError as e:
            shown = "Sorry, I couldn't reach the AI service."
            placeholder.error(f"{shown} ({type(e).__name__})")

    st.session_state[ui_key].append({"role": "assistant", "content": shown})


if __name__ == "__main__":
    st.set_page_config(page_title="Vornis AI", page_icon="🪐")
    render_vornis_chatbot()
