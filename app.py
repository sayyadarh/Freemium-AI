import streamlit as st
import sqlite3
import time
import ollama

# --- 1. Helper Function with Try-Except Fallback ---
def explain_topic_with_ai(topic, subject):
    prompt = f"You are a helpful AI tutor for secondary school students studying {subject}. Explain {topic} simply and clearly with key points."
    
    try:
        response = ollama.chat(
            model="llama3.2",
            messages=[{"role": "user", "content": prompt}]
        )
        return response['message']['content']
    except Exception as e:
        # Fallback response so the app never crashes
        return (
            f"*(Offline Simulated Mode)*\n\n"
            f"### Key Concepts: {topic}\n"
            f"Great question regarding **{subject}**!\n\n"
            f"1. **Core Principle:** `{topic}` is a fundamental topic in {subject}.\n"
            f"2. **Key Focus:** Focus on definitions, key formulas/rules, and practical applications.\n"
            f"3. **Practice Tip:** Test yourself on past examination questions for this topic!\n\n"
            f"*(Note: Local Ollama model 'llama3.2' not active. Running on smart fallback mode.)*"
        )


# --- 2. Streamlit Page Configuration ---
st.set_page_config(
    page_title="Freemium AI - Offline RAG Tutor",
    page_icon="⚡",
    layout="centered"
)

# Custom CSS for styling
st.markdown("""
    <style>
    .welcome-card {
        background-color: #0E1117;
        padding: 2rem;
        border-radius: 12px;
        border: 1px solid #1E293B;
        text-align: center;
        margin-bottom: 2rem;
    }
    .stButton > button {
        width: 100%;
        border-radius: 8px;
        font-weight: 600;
    }
    </style>
""", unsafe_allow_html=True)

# --- 3. Session State Initialization ---
if "onboarded" not in st.session_state:
    st.session_state.onboarded = False
if "user_name" not in st.session_state:
    st.session_state.user_name = ""
if "selected_subject" not in st.session_state:
    st.session_state.selected_subject = "General Knowledge"
if "messages" not in st.session_state:
    st.session_state.messages = []

# --- 4. Interactive Onboarding Screen ---
if not st.session_state.onboarded:
    st.markdown("""
        <div class="welcome-card">
            <h1 style="color: #38BDF8; margin-bottom: 0.2rem;">⚡ Freemium AI</h1>
            <p style="color: #94A3B8; font-size: 1.1rem;">Your Offline-First AI Tutor & Study Companion</p>
        </div>
    """, unsafe_allow_html=True)

    with st.form("onboarding_form"):
        st.subheader("👋 Welcome! Let's set up your study session")
        
        name_input = st.text_input("What is your name?", placeholder="Enter your name...")
        
        subject_input = st.selectbox(
            "Select the subject you want to focus on today:",
            ["Chemistry", "Physics", "Mathematics", "Computer Studies", "Food and Nutrition", "General Knowledge"]
        )
        
        submitted = st.form_submit_button("🚀 Start Studying")
        
        if submitted:
            if name_input.strip() != "":
                st.session_state.user_name = name_input.strip()
                st.session_state.selected_subject = subject_input
                st.session_state.onboarded = True
                
                welcome_msg = (
                    f"Hello **{st.session_state.user_name}**! Welcome to your **{st.session_state.selected_subject}** "
                    "study room. I'm your AI tutor running completely offline. What topic or question would you like to explore today?"
                )
                st.session_state.messages.append({"role": "assistant", "content": welcome_msg})
                st.rerun()
            else:
                st.warning("Please enter your name to continue!")

# --- 5. Main AI Tutor Interface ---
else:
    with st.sidebar:
        st.title("👤 Student Profile")
        st.write(f"**Name:** {st.session_state.user_name}")
        st.write(f"**Subject:** {st.session_state.selected_subject}")
        st.markdown("---")
        
        if st.button("🔄 Change Subject / Restart"):
            st.session_state.onboarded = False
            st.session_state.messages = []
            st.rerun()
            
        st.caption("⚡ *Freemium AI runs offline using local database & Ollama RAG pipeline.*")

    st.title(f"📚 {st.session_state.selected_subject} Room")
    st.caption(f"Offline AI Tutor for **{st.session_state.user_name}**")

    # Display Chat History
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    # Chat Input
    if user_prompt := st.chat_input(f"Ask any question about {st.session_state.selected_subject}..."):
        st.session_state.messages.append({"role": "user", "content": user_prompt})
        with st.chat_message("user"):
            st.markdown(user_prompt)

        with st.chat_message("assistant"):
            with st.spinner("Processing offline request..."):
                response_text = explain_topic_with_ai(user_prompt, st.session_state.selected_subject)
                st.markdown(response_text)
                st.session_state.messages.append({"role": "assistant", "content": response_text})