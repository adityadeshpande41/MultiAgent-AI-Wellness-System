import sys, os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import streamlit as st
from agents.orchestrator import run_agent

st.set_page_config(page_title="AI Wellness Assistant", page_icon="💪", layout="wide")

# Custom CSS for better chat appearance
st.markdown("""
<style>
    .stChatMessage {
        padding: 1rem;
        border-radius: 0.5rem;
        margin: 0.5rem 0;
    }
    
    .stChatMessage[data-testid="chat-message-user"] {
        background-color: #e3f2fd;
    }
    
    .stChatMessage[data-testid="chat-message-assistant"] {
        background-color: #f5f5f5;
    }
    
    .chat-input {
        position: sticky;
        bottom: 0;
        background: white;
        padding: 1rem 0;
    }
</style>
""", unsafe_allow_html=True)

# Main title
st.title("💬 AI Wellness Chat")
st.markdown("*Ask me about fitness 🏋️, nutrition 🍎, or health 🩺 - I'm here to help!*")

# User input
user = st.text_input("Your name", value="User")

# Add example prompts and clear button
col1, col2 = st.columns([3, 1])
with col1:
    st.markdown("**Try asking:** *I want to start working out*, *I'm feeling anxious*, *What's a healthy breakfast?*")
with col2:
    if st.button("🗑️ Clear Chat"):
        st.session_state.chat = []
        st.rerun()

# Initialize chat history
if "chat" not in st.session_state:
    st.session_state.chat = []

# Display chat messages with proper formatting
for who, txt in st.session_state.chat:
    if who == "You":
        with st.chat_message("user"):
            st.write(txt)
    else:
        with st.chat_message("assistant"):
            st.write(txt)

# Chat input at the bottom
msg = st.chat_input("Ask about workouts, meals, or health...")
if msg:
    # Add user message immediately
    with st.chat_message("user"):
        st.write(msg)
    
    # Get AI response
    with st.spinner("Thinking..."):
        ans = run_agent(user, msg)
    
    # Add AI response
    with st.chat_message("assistant"):
        st.write(ans)
    
    # Store in session state
    st.session_state.chat.append(("You", msg))
    st.session_state.chat.append(("AI", ans))
    
    # Rerun to update the display
    st.rerun()

# Add some helpful information in the sidebar
st.sidebar.title("🏋️ AI Wellness Assistant")
st.sidebar.markdown("""
### What I can help with:

**🏋️ Fitness**
- Workout routines
- Exercise form and techniques
- Training plans

**🍎 Nutrition**
- Meal planning
- Calorie information
- Healthy recipes

**🩺 Health**
- General wellness advice
- Stress management
- Sleep tips

### Test the Two-Option System:

**Ambiguous Questions** (should ask clarification):
- "I feel bad"
- "I have no energy" 
- "I want to improve"
- "I'm struggling"

**Unrelated Questions** (should get specialized message):
- "What is the color of the sky?"
- "What time is it?"
- "Tell me a joke"

**Clear Questions** (should route directly):
- "How many calories in pizza?"
- "I have a headache"
- "I want to start working out"
""")