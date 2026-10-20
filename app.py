import streamlit as st
import sqlite3
import os
import ollama

# --- 1. Precise Word-Matching SQLite Engine & RAG ---
def init_db():
    """Ensures subject.db and the qa_data table always exist with an expanded study dataset."""
    db_path = "subject.db"
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS qa_data (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            subject TEXT,
            input TEXT,
            output TEXT
        )
    ''')
    
    cursor.execute("SELECT COUNT(*) FROM qa_data")
    count = cursor.fetchone()[0]
    
    expanded_data = [
        ("Computer Science", "what is a computer", "A computer is an electronic device that accepts data as input, processes it according to stored instructions, and produces information as output. It consists of both hardware and software."),
        ("Computer Science", "define hardware", "Hardware refers to the physical, tangible parts of a computer system that you can touch and see. Examples include the Central Processing Unit (CPU), monitor, keyboard, mouse, and hard drive."),
        ("Computer Science", "what is software", "Software is a set of instructions, data, or programs used to operate computers and execute specific tasks. It is the intangible part of the computer, such as operating systems and applications."),
        ("Computer Science", "what is an operating system", "An operating system (OS) is system software that manages computer hardware, software resources, and provides common services for computer programs, such as Windows, macOS, Linux, and Android."),
        ("Computer Science", "what are input devices", "Input devices are hardware components used to feed data and control signals into a computer. Common examples include the keyboard, mouse, scanner, microphone, and digital camera."),
        ("Computer Science", "what are output devices", "Output devices are hardware components that display or reproduce processed data from the computer to the user. Examples include the monitor (screen), printer, speakers, and projector."),
        ("Computer Science", "what is the cpu", "The Central Processing Unit (CPU) is known as the 'brain' of the computer. It fetches instructions from memory, decodes them, and executes calculations or processing tasks."),
        ("Computer Science", "what is memory", "Computer memory is used to store data and instructions temporarily or permanently. Primary memory includes RAM (Random Access Memory, volatile) and ROM (Read-Only Memory, non-volatile)."),
        ("Computer Science", "what is the internet", "The internet is a global system of interconnected computer networks that use the standard Internet Protocol (TCP/IP) to link devices worldwide, enabling data sharing and communication.")
    ]
    
    if count == 0:
        cursor.executemany("INSERT INTO qa_data (subject, input, output) VALUES (?, ?, ?)", expanded_data)
        conn.commit()
    else:
        for item in expanded_data:
            cursor.execute("SELECT COUNT(*) FROM qa_data WHERE LOWER(input) = ?", (item[1].lower(),))
            if cursor.fetchone()[0] == 0:
                cursor.execute("INSERT INTO qa_data (subject, input, output) VALUES (?, ?, ?)", (item[0], item[1], item[2]))
                conn.commit()
                
    conn.close()

def get_answer_from_db(query, subject):
    """Performs precise keyword scoring to ensure zero mismatched answers."""
    init_db()
    db_path = "subject.db"

    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        q_clean = query.lower().strip()
        
        # 1. Exact match check
        cursor.execute("SELECT output FROM qa_data WHERE LOWER(input) = ? AND LOWER(subject) LIKE ?", (q_clean, f"%{subject.lower()}%"))
        result = cursor.fetchone()
        if result:
            conn.close()
            return result[0]
            
        # 2. Smart Scoring: Find the database question with the highest keyword overlap
        cursor.execute("SELECT input, output FROM qa_data WHERE LOWER(subject) LIKE ?", (f"%{subject.lower()}%",))
        rows = cursor.fetchall()
        conn.close()
        
        stop_words = {"what", "is", "a", "an", "the", "how", "can", "to", "define", "explain", "tell", "me", "about", "are", "do", "does"}
        q_words = set(w for w in q_clean.split() if w not in stop_words)
        
        best_match_output = None
        highest_score = 0
        
        for db_input, db_output in rows:
            db_words = set(w for w in db_input.lower().split() if w not in stop_words)
            common_words = q_words.intersection(db_words)
            score = len(common_words)
            
            if score > highest_score:
                highest_score = score
                best_match_output = db_output
                
        if highest_score > 0:
            return best_match_output

    except Exception as e:
        return None

    return None

def generate_rag_response(user_prompt, subject):
    """Fetches exact database record and instructs Ollama to be concise and interactive."""
    db_context = get_answer_from_db(user_prompt, subject)
    
    if db_context:
        prompt = (
            f"You are Freemium AI, a friendly offline tutor for {subject}. "
            f"The student asked: '{user_prompt}'. "
            f"Here is the verified database definition: {db_context}\n\n"
            f"Instructions:\n"
            f"1. Give a DIRECT, concise, and precise answer based strictly on the definition.\n"
            f"2. Keep it short (2-3 sentences max) so it's not overwhelming.\n"
            f"3. End with a friendly, interactive follow-up question asking if they want to explore related topics (like hardware, software, or components)."
        )
        try:
            response = ollama.chat(
                model="llama3.2",
                messages=[{"role": "user", "content": prompt}]
            )
            return response['message']['content']
        except Exception:
            return db_context
    else:
        return f"I couldn't find a direct match for **'{user_prompt}'** in our offline database. Try asking about *what is a computer*, *define hardware*, or *what is the CPU*!"


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
                
                welcome_msg = f"Hello **{st.session_state.user_name}**! Welcome to your **{st.session_state.selected_subject}** study room for the **{st.session_state.selected_country}** curriculum ({st.session_state.education_level}).\n\nI am ready. Try asking about *what is a computer*, *define hardware*, or *what is the CPU*!"
                
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
            with st.spinner("Querying local SQLite database..."):
                response_text = generate_rag_response(user_prompt, st.session_state.selected_subject)
                st.markdown(response_text)
                st.session_state.messages.append({"role": "assistant", "content": response_text})