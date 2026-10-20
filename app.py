import streamlit as st
import sqlite3
import os
import ollama

# --- 1. Smart Offline RAG Engine ---
def get_answer_from_db(query, subject):
    """Searches SQLite database using multi-keyword matching for natural language queries."""
    db_path = "subject.db"
    
    if not os.path.exists(db_path):
        return None

    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Clean query: remove filler words to extract core concepts
        stop_words = ["what", "is", "a", "an", "the", "how", "can", "to", "define", "explain", "tell", "me", "about"]
        words = [w.lower() for w in query.split() if w.lower() not in stop_words]
        
        # If words list is empty, use raw query
        search_terms = words if words else [query.lower()]
        
        # Build dynamic SQL query to match any significant keyword
        conditions = []
        params = []
        for term in search_terms:
            conditions.append("LOWER(input) LIKE ? OR LOWER(output) LIKE ?")
            params.extend([f"%{term}%", f"%{term}%"])
            
        sql_query = f"SELECT output FROM qa_data WHERE ({' OR '.join(conditions)}) AND LOWER(subject) LIKE ?"
        params.append(f"%{subject.lower()}%")
        
        cursor.execute(sql_query, params)
        result = cursor.fetchone()
        conn.close()
        
        if result:
            return result[0]
    except Exception as e:
        return None

    return None

def generate_rag_response(user_prompt, subject):
    """Retrieves context from SQLite DB and uses Ollama to formulate a natural response."""
    # Step 1: Retrieve context from local database
    db_context = get_answer_from_db(user_prompt, subject)
    
    # Step 2: Construct prompt for Ollama
    if db_context:
        prompt = (
            f"You are Freemium AI, an offline secondary school tutor for {subject}. "
            f"Answer the student's question using ONLY the following verified database reference context:\n\n"
            f"Reference Context: {db_context}\n\n"
            f"Student Question: {user_prompt}\n"
            f"Provide a clear, natural, and educational explanation."
        )
    else:
        prompt = f"Explain '{user_prompt}' simply for a secondary school student studying {subject}."

    # Step 3: Try generating via local Ollama instance
    try:
        response = ollama.chat(
            model="llama3.2",
            messages=[{"role": "user", "content": prompt}]
        )
        return response['message']['content']
    except Exception as e:
        # Fallback if Ollama model isn't pulled/running yet
        if db_context:
            return f"**[Offline Database Match]**\n\n{db_context}"
        else:
            return (
                f"*(Offline RAG Fallback Mode)*\n\n"
                f"Regarding **'{user_prompt}'** in **{subject}**: This is a fundamental concept involving structured logic and core definitions. "
                f"(Make sure your local Ollama model `llama3.2` is pulled via terminal with `ollama pull llama3.2` for full AI generation!)"
            )


# --- 2. Streamlit Page Configuration ---
st.set_page_config(
    page_title="Freemium AI - Offline RAG Tutor",
    page_icon="⚡",
    layout="centered"
)

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
if "education_level" not in st.session_state:
    st.session_state.education_level = "Secondary School"
if "selected_country" not in st.session_state:
    st.session_state.selected_country = "Nigeria"
if "selected_subject" not in st.session_state:
    st.session_state.selected_subject = "Computer Science"
if "messages" not in st.session_state:
    st.session_state.messages = []

ALL_COUNTRIES = [
    "Nigeria (Available)",
    "USA (Available)",
    "Ghana (Unavailable)",
    "Kenya (Unavailable)",
    "South Africa (Unavailable)",
    "United Kingdom (Unavailable)",
    "Canada (Unavailable)"
]

ALL_SUBJECTS = [
    "Computer Science (Available)",
    "Chemistry (Unavailable)",
    "Physics (Unavailable)",
    "Mathematics (Unavailable)",
    "Food and Nutrition (Unavailable)"
]

# --- 4. Interactive Onboarding Screen ---
if not st.session_state.onboarded:
    st.markdown("""
        <div class="welcome-card">
            <h1 style="color: #38BDF8; margin-bottom: 0.2rem;">⚡ Freemium AI</h1>
            <p style="color: #94A3B8; font-size: 1.1rem;">Your Offline-First AI Tutor & Study Companion</p>
        </div>
    """, unsafe_allow_html=True)

    with st.form("onboarding_form"):
        st.subheader("👋 Welcome! Let's set up your profile")
        
        name_input = st.text_input("1. What is your name?", placeholder="Enter your full name...")
        
        level_input = st.selectbox(
            "2. Level of Education:",
            ["Primary School / Kindergarten", "Junior Secondary School", "Senior Secondary School", "Tertiary / Undergraduate"]
        )

        country_choice = st.selectbox(
            "3. Select your Country:",
            ALL_COUNTRIES
        )

        subject_choice = st.selectbox(
            "4. Select Subject to Study:",
            ALL_SUBJECTS
        )

        if "Unavailable" in country_choice:
            st.warning("⚠️ Notice: This country's curriculum is currently unavailable. (Only Nigeria & USA are available).")
            
        if "Unavailable" in subject_choice:
            st.info("ℹ️ Notice: This subject dataset is coming soon. Computer Science is currently available.")

        submitted = st.form_submit_button("🚀 Start Studying")
        
        if submitted:
            if name_input.strip() == "":
                st.warning("Please enter your name to continue!")
            elif "Unavailable" in country_choice:
                st.error("❌ Cannot proceed: This country's curriculum is currently unavailable.")
            elif "Unavailable" in subject_choice:
                st.error("❌ Cannot proceed: This subject is currently unavailable.")
            else:
                st.session_state.user_name = name_input.strip()
                st.session_state.education_level = level_input
                st.session_state.selected_country = country_choice.replace(" (Available)", "")
                st.session_state.selected_subject = subject_choice.replace(" (Available)", "")
                st.session_state.onboarded = True
                
                welcome_msg = (
                    f"Hello **{st.session_state.user_name}**! Welcome to your **{st.session_state.selected_subject}** "
                    f"study room for the **{st.session_state.selected_country}** curriculum ({st.session_state.education_level}).\n\n"
                    "I am ready. Ask me anything like *"What is a computer?"* or *"Define hardware"*!"
                )
                st.session_state.messages.append({"role": "assistant", "content": welcome_msg})
                st.rerun()

# --- 5. Main AI Tutor Interface ---
else:
    with st.sidebar:
        st.title("👤 Student Profile")
        st.write(f"**Name:** {st.session_state.user_name}")
        st.write(f"**Level:** {st.session_state.education_level}")
        st.write(f"**Country:** {st.session_state.selected_country} 🟢")
        st.write(f"**Subject:** {st.session_state.selected_subject} 🟢")
        st.markdown("---")
        
        if st.button("🔄 Change Settings / Restart"):
            st.session_state.onboarded = False
            st.session_state.messages = []
            st.rerun()
            
        st.caption("⚡ *Freemium AI runs 100% offline using SQLite DB & Ollama RAG.*")

    st.title(f"💻 {st.session_state.selected_subject} Room")
    st.caption(f"Curriculum: **{st.session_state.selected_country}** | Student: **{st.session_state.user_name}**")

    # Display Chat History
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    # Chat Input & RAG Execution
    if user_prompt := st.chat_input(f"Ask any question about {st.session_state.selected_subject}..."):
        st.session_state.messages.append({"role": "user", "content": user_prompt})
        with st.chat_message("user"):
            st.markdown(user_prompt)

        with st.chat_message("assistant"):
            with st.spinner("Retrieving offline RAG context..."):
                response_text = generate_rag_response(user_prompt, st.session_state.selected_subject)
                st.markdown(response_text)
                st.session_state.messages.append({"role": "assistant", "content": response_text})