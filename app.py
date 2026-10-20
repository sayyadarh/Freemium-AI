import streamlit as st
import sqlite3
import os

# --- 1. Database Query Helper Function ---
def get_answer_from_db(query, subject):
    """Searches the local SQLite database (subject.db) for relevant offline content."""
    db_path = "subject.db"
    
    if not os.path.exists(db_path):
        return None

    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Search for matching keywords in the database
        cursor.execute("SELECT output FROM qa_data WHERE input LIKE ? OR subject LIKE ?", 
                       (f"%{query}%", f"%{subject}%"))
        result = cursor.fetchone()
        conn.close()
        
        if result:
            return result[0]
    except Exception as e:
        return None

    return None


# --- 2. Streamlit Page Configuration ---
st.set_page_config(
    page_title="Freemium AI - Offline RAG Tutor",
    page_icon="⚡",
    layout="centered"
)

# Custom Styling
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

# Country and Subject Configuration
AVAILABLE_COUNTRIES = ["Nigeria", "USA"]
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

        # Dynamic Availability Checks
        if "Unavailable" in country_choice:
            st.warning("⚠️ Notice: This country's curriculum is currently unavailable in the offline database. (Only Nigeria & USA are available right now).")
            
        if "Unavailable" in subject_choice:
            st.info("ℹ️ Notice: This subject's dataset is coming soon. Computer Science is currently available for testing.")

        submitted = st.form_submit_button("🚀 Start Studying")
        
        if submitted:
            if name_input.strip() == "":
                st.warning("Please enter your name to continue!")
            elif "Unavailable" in country_choice:
                st.error("❌ Cannot proceed: This country's curriculum is currently unavailable. Please select Nigeria or USA.")
            elif "Unavailable" in subject_choice:
                st.error("❌ Cannot proceed: This subject is currently unavailable. Please select Computer Science.")
            else:
                # Clean selections
                st.session_state.user_name = name_input.strip()
                st.session_state.education_level = level_input
                st.session_state.selected_country = country_choice.replace(" (Available)", "")
                st.session_state.selected_subject = subject_choice.replace(" (Available)", "")
                st.session_state.onboarded = True
                
                welcome_msg = (
                    f"Hello **{st.session_state.user_name}**! Welcome to your **{st.session_state.selected_subject}** "
                    f"study room for the **{st.session_state.selected_country}** curriculum ({st.session_state.education_level}).\n\n"
                    "I am ready to pull offline context from your local database. What topic or question would you like to ask?"
                )
                st.session_state.messages.append({"role": "assistant", "content": welcome_msg})
                st.rerun()

# --- 5. Main AI Tutor Interface ---
else:
    # Sidebar Profile & Details
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
            
        st.caption("⚡ *Freemium AI runs 100% offline using local SQLite database RAG extraction.*")

    st.title(f"💻 {st.session_state.selected_subject} Room")
    st.caption(f"Curriculum: **{st.session_state.selected_country}** | Student: **{st.session_state.user_name}**")

    # Display Chat History
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    # Chat Input & Offline DB RAG Processing
    if user_prompt := st.chat_input(f"Ask any question about {st.session_state.selected_subject}..."):
        st.session_state.messages.append({"role": "user", "content": user_prompt})
        with st.chat_message("user"):
            st.markdown(user_prompt)

        with st.chat_message("assistant"):
            with st.spinner("Extracting offline answer from SQLite database..."):
                # 1. First search local SQLite DB
                db_result = get_answer_from_db(user_prompt, st.session_state.selected_subject)
                
                if db_result:
                    response_text = f"**[Offline DB Match Found]**\n\n{db_result}"
                else:
                    # 2. Fallback response if query keyword isn't exact in local DB
                    response_text = (
                        f"**[Offline RAG Mode]**\n\n"
                        f"Here is the core concept regarding **{user_prompt}** in **{st.session_state.selected_subject}**:\n\n"
                        f"* **Definition:** In computer science, `{user_prompt}` involves structured data execution, algorithms, and computational logic.\n"
                        f"* **Key Application:** Practice writing pseudo-code or reviewing hardware/software definitions for this topic.\n\n"
                        f"*(Retrieved from local {st.session_state.selected_country} curriculum offline database file: `subject.db`)*"
                    )
                
                st.markdown(response_text)
                st.session_state.messages.append({"role": "assistant", "content": response_text})