# ---------------------- NLTK Safe Download ----------------------
# ---------------------- NLTK Safe Download ----------------------
import nltk
import os
import ssl

try:
    _create_unverified_https_context = ssl._create_unverified_context
except AttributeError:
    pass
else:
    ssl._create_default_https_context = _create_unverified_https_context

# Force download punkt tokenizer & wordnet
nltk.download("punkt")
nltk.download("wordnet")
nltk.download("omw-1.4")


# ---------------------- Imports ----------------------
import streamlit as st
import text2emotion as te
import together
from langchain_core.prompts import (
    SystemMessagePromptTemplate, HumanMessagePromptTemplate,
    AIMessagePromptTemplate
)

# ---------------------- Together AI Setup ----------------------
together.api_key = "your_together_api_key_here"  # 🔒 Replace with your actual key

def generate_response(prompt_text: str) -> str:
    response = together.Complete.create(
        prompt=prompt_text,
        model="meta-llama/Llama-3-8b-chat-hf",
        max_tokens=256,
        temperature=0.7,
        top_p=0.7,
        stop=["</s>"]
    )
    return response['output']['choices'][0]['text'].strip()

# ---------------------- Emotion Emoji ----------------------
emotion_emojis = {
    "Happy": "😄", "Sad": "😢", "Angry": "😠", "Fear": "😨",
    "Surprise": "😲", "Neutral": "🤖", "Cry": "😭"
}

# ---------------------- Streamlit UI ----------------------
st.set_page_config(page_title="EmoChat AI", page_icon="🤖")
st.markdown("""
    <style>
        body { font-family: 'Segoe UI', sans-serif; }
        .title { text-align: center; color: #4A90E2; font-size: 2.5em; margin-bottom: 0; }
        .subtitle { text-align: center; color: #888; font-size: 1.1em; margin-top: 0; }
        .chat-container {
            max-height: 400px;
            overflow-y: auto;
            padding: 10px;
            background-color: #f7f7f7;
            border-radius: 10px;
            margin-top: 10px;
        }
        .user-msg {
            background-color: #DCF8C6;
            padding: 10px;
            border-radius: 8px;
            margin-bottom: 8px;
            color: #000000;
        }
        .assistant-msg {
            background-color: #E8EAF6;
            padding: 10px;
            border-radius: 8px;
            margin-bottom: 8px;
            color: #333333;
        }
    </style>
""", unsafe_allow_html=True)

st.markdown("<div class='title'>🤖 Smart Virtual AI Assistant with Emotions</div>", unsafe_allow_html=True)
st.markdown("<div class='subtitle'>Your emotional intelligence-powered AI companion</div>", unsafe_allow_html=True)

# ---------------------- Session State ----------------------
if "chat_history" not in st.session_state:
    st.session_state['chat_history'] = []

# ---------------------- Chat History Helpers ----------------------
def get_history():
    history = []
    for chat in st.session_state['chat_history']:
        history.append(HumanMessagePromptTemplate.from_template(chat['user']))
        history.append(AIMessagePromptTemplate.from_template(chat['assistant']))
    return history

# ---------------------- Input Form ----------------------
with st.form("llm-form"):
    text = st.text_area("💬 Enter your question below", height=100)
    submit = st.form_submit_button("🎤 Ask")

# ---------------------- Chat Response ----------------------
if submit and text.strip():
    with st.spinner("Analyzing emotions and generating response..."):
        emotions = te.get_emotion(text)
        dominant_emotion = max(emotions, key=emotions.get) if emotions else "Neutral"
        emoji = emotion_emojis.get(dominant_emotion, "🤖")

        st.success(f"Detected Emotion: {dominant_emotion} {emoji}")

        system_prompt = SystemMessagePromptTemplate.from_template(
            f"You are an emotionally intelligent AI Assistant for Working Professionals and students. "
            f"The user is currently feeling **{dominant_emotion}**. "
            f"Respond briefly and kindly, with empathy. Explain things like a polite smart assistant."
        )

        full_prompt = [system_prompt] + get_history()
        full_prompt.append(HumanMessagePromptTemplate.from_template(text))

        combined_prompt = "\n".join([p.template for p in full_prompt])
        response = generate_response(combined_prompt)

        st.session_state['chat_history'].append({
            'user': text,
            'assistant': f"{emoji} {response}"
        })

# ---------------------- Chat History UI ----------------------
st.markdown("## 🗂️ Chat History")
st.markdown("<div class='chat-container'>", unsafe_allow_html=True)

for chat in reversed(st.session_state['chat_history']):
    st.markdown(f"<div class='user-msg'><strong>👤 You:</strong> {chat['user']}</div>", unsafe_allow_html=True)
    st.markdown(f"<div class='assistant-msg'><strong>{chat['assistant'].split()[0]} Assistant:</strong> {' '.join(chat['assistant'].split()[1:])}</div>", unsafe_allow_html=True)

st.markdown("</div>", unsafe_allow_html=True)

# ---------------------- Clear Option ----------------------
if st.button("🗑️ Clear Chat"):
    st.session_state['chat_history'] = []
