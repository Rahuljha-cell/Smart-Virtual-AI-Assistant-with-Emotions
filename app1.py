# ---------------------- Install Instructions ----------------------
# pip install -r requirements.txt

# ---------------------- NLTK Downloads ----------------------
import nltk
nltk.download('punkt')
nltk.download('omw-1.4', quiet=True)
nltk.download('wordnet', quiet=True)

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
    "Surprise": "😲", "Neutral": "🤖", "confused": "😕"
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
        .User-msg {
            background-color: #DCF8C6;
            padding: 10px;
            border-radius: 8px;
            margin-bottom: 8px;
            color: #000000;
        }
        .ARIA-msg {
            background-color: #E8EAF6;
            padding: 10px;
            border-radius: 8px;
            margin-bottom: 8px;
            color: #333333; /* Fixed: readable text */
        }
    </style>
""", unsafe_allow_html=True)


# ---------------------- Title ----------------------
st.markdown("<div class='title'>🤖 ARIA: Smart Emotional Chat Assistant</div>", unsafe_allow_html=True)
st.markdown("<div class='subtitle'>Your friendly ARIA: Smart Emotional Chat Assistant that understands your emotions.</div>", unsafe_allow_html=True)

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
        history.append(HumanMessagePromptTemplate.from_template(chat['User']))
        history.append(AIMessagePromptTemplate.from_template(chat['ARIA']))
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
    f"""
You are a Smart Virtual AI Assistant with Emotional Intelligence. Your goal is to emotionally support users using calm, polite, and empathetic communication, just like a caring human mentor.

✨ Key Instructions:
- Always reply in the **same language and script** the user uses:
  • If the user speaks in **English**, reply in **English**
  • If the user writes in **Hindi script**, reply in **Hindi script**
  • If the user speaks in **Hinglish** (Hindi written using English letters), you must **also reply in Hinglish**
- **Do not switch the language or script** unless the user switches it first
- Respond in a warm, friendly, and supportive tone
- Responses should be **brief (2–3 sentences)** and emotionally comforting




🧠 Emotional Context:
The user is currently feeling **{dominant_emotion}**. Your tone and words should reflect empathy for this emotional state.

📝 Examples:
- User: "Main thoda upset hun aaj"  
  → You: "Aisa hota hai kabhi kabhi... main samajh sakta hun ki aap kaisa feel kar rahe ho."

- User: "I'm super excited about my new job!"  
  → You: "That's amazing! Starting something new is always thrilling — congrats!"

- User: "Mujhe nhi samjh aa raha kya karun ab"  
  → You: "Chinta mat karo, main hoon na. Hum saath milkar sochte hain kya best hoga."

Remember: your job is to reflect the user's language and emotion **exactly** as they use it — Hinglish must be responded to in Hinglish, without translating it into pure Hindi or English.
"""
)





        full_prompt = [system_prompt] + get_history()
        full_prompt.append(HumanMessagePromptTemplate.from_template(text))

        response = generate_response(full_prompt)

        st.session_state['chat_history'].append({
            'User': text,
            'ARIA': f"{emoji} {response}"
        })

# ---------------------- Chat History ----------------------
st.markdown("## 🗂️ Chat History")
st.markdown("<div class='chat-container'>", unsafe_allow_html=True)

for chat in reversed(st.session_state['chat_history']):
    st.markdown(f"<div class='User-msg'><strong>👤 You:</strong> {chat['User']}</div>", unsafe_allow_html=True)
    st.markdown(f"<div class='ARIA-msg'><strong>{chat['ARIA'].split()[0]} ARIA:</strong> {' '.join(chat['ARIA'].split()[1:])}</div>", unsafe_allow_html=True)

st.markdown("</div>", unsafe_allow_html=True)

# ---------------------- Clear Option ----------------------
if st.button("🗑️ Clear Chat"):
    st.session_state['chat_history'] = []
