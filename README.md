# VornisAI - AI Chatbot module

## Run locally
    python -m venv .venv
    .venv\Scripts\activate        # Mac/Linux: source .venv/bin/activate
    pip install -r requirements.txt
    copy .env.example .env        # add your ANTHROPIC_API_KEY
    streamlit run app.py

## Files
- `vornis_chatbot.py` - chat UI + tool-calling loop (chatbot owner)
- `tools.py` - adapter to the other modules (teammates edit this)
- `app.py` - tiny test host

## Integrating into the main app
    from vornis_chatbot import render_vornis_chatbot
    render_vornis_chatbot()
