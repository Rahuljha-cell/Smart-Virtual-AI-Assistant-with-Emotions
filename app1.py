# ---------------------- Install Instructions ----------------------
# pip install -r requirements.txt

# ---------------------- NLTK Downloads ----------------------
import nltk

# Safe downloads for NLTK data
try:
    nltk.data.find("tokenizers/punkt")
except LookupError:
    nltk.download("punkt")

try:
    nltk.data.find("corpora/wordnet")
except LookupError:
    nltk.download("wordnet")

try:
    nltk.data.find("corpora/omw-1.4")
except LookupError:
    nltk.download("omw-1.4")

# ---------------------- Imports ----------------------
import streamlit as st
import text2emotion as te
from langchain_ollama import ChatOllama
from langchain_core.prompts import (
    SystemMessagePromptTemplate, HumanMessagePromptTemplate,
    AIMessagePromptTemplate, ChatPromptTemplate
)

# ---------------------- Emotion Emoji ----------------------
emotion_emojis = {
    "Happy": "😄", "Sad": "😢", "Angry": "😠", "Fear": "😨",
    "Surprise": "😲", "Neutral": "🤖"
}

# ---------------------- CSS Styling ----------------------
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
            color: #333333
        }
    </style>
""", unsafe_allow_html=True)

# ---------------------- Title ----------------------
st.markdown("<div class='title'>🤖 Emotion-Aware Chat Assistant</div>", unsafe_allow_html=True)
st.markdown("<div class='subtitle'>Your friendly 5th-grade teacher chatbot that understands your mood</div>", unsafe_allow_html=True)

# ---------------------- Ollama Model Setup ----------------------
model = ChatOllama(model="llama3", base_url="http://localhost:11434/")

# ---------------------- Streamlit Session ----------------------
if "chat_history" not in st.session_state:
    st.session_state['chat_history'] = []

# ---------------------- Helper Functions ----------------------
def generate_response(full_prompt):
    messages = ChatPromptTemplate.from_messages(full_prompt).format_messages()
    response = model.invoke(messages)
    return response.content

def get_history():
    history = []
    for chat in st.session_state['chat_history']:
        history.append(HumanMessagePromptTemplate.from_template(chat['user']))
        history.append(AIMessagePromptTemplate.from_template(chat['assistant']))
    return history

# ---------------------- User Input Form ----------------------
with st.form("llm-form"):
    text = st.text_area("💬 Enter your question below", height=100)
    col1, col2 = st.columns([1, 5])
    with col2:
        submit = st.form_submit_button("🎤 Ask")

# ---------------------- Handle Input ----------------------
if submit and text.strip():
    with st.spinner("Analyzing emotions and generating response..."):
        emotions = te.get_emotion(text)
        dominant_emotion = max(emotions, key=emotions.get) if emotions else "Neutral"
        emoji = emotion_emojis.get(dominant_emotion, "🤖")

        st.success(f"Detected Emotion: {dominant_emotion} {emoji}")

        # Create new prompt with emotion context
        system_prompt = SystemMessagePromptTemplate.from_template(
            f"You are an emotionally intelligent AI teacher for 5th-grade students. "
            f"The user is currently feeling **{dominant_emotion}**. "
            f"Respond briefly and kindly, with empathy. Explain things like a friendly school teacher."
        )

        full_prompt = [system_prompt] + get_history()
        full_prompt.append(HumanMessagePromptTemplate.from_template(text))

        response = generate_response(full_prompt)

        st.session_state['chat_history'].append({
            'user': text,
            'assistant': f"{emoji} {response}"
        })

# ---------------------- Chat History ----------------------
st.markdown("## 🗂️ Chat History")
st.markdown("<div class='chat-container'>", unsafe_allow_html=True)

for chat in reversed(st.session_state['chat_history']):
    st.markdown(f"<div class='user-msg'><strong>👤 You:</strong> {chat['user']}</div>", unsafe_allow_html=True)
    st.markdown(f"<div class='assistant-msg'><strong>{chat['assistant'].split()[0]} Assistant:</strong> {' '.join(chat['assistant'].split()[1:])}</div>", unsafe_allow_html=True)

st.markdown("</div>", unsafe_allow_html=True)

# ---------------------- Clear Option ----------------------
if st.button("🗑️ Clear Chat"):
    st.session_state['chat_history'] = []
