import sqlite3
import ollama

db_path = "cs_subject.db"


def get_context(query):
    """Searches cs_subject.db for matching textbook content."""
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # Search for matching keywords in the textbook data
    cursor.execute(
        "SELECT content FROM topics WHERE content LIKE ? LIMIT 5",
        (f"%{query}%",),
    )
    rows = cursor.fetchall()
    conn.close()

    context_text = ""
    for row in rows:
        context_text += row[0] + "\n"
    return context_text


def ask_ai(user_question):
    """Retrieves context and queries the local Llama model."""
    context = get_context(user_question)

    prompt = f"""
You are an offline educational assistant. 
Use the following lesson context from the textbook to answer the question briefly.

Context:
{context if context.strip() else 'No direct textbook match found. Answer using standard core educational knowledge.'}

Question: {user_question}
"""

    response = ollama.chat(
        model="llama3.2:1b", messages=[{"role": "user", "content": prompt}]
    )
    return response["message"]["content"]


# --- Interactive Terminal Chat Loop ---
print("==================================================")
print("  Offline Educational AI Tutor Running (Type 'exit' to quit)")
print("==================================================\n")

while True:
    user_input = input("You: ")
    if user_input.lower().strip() in ["exit", "quit"]:
        print("Closing tutor engine. Goodbye!")
        break

    if not user_input.strip():
        continue

    print("\nThinking offline...")
    answer = ask_ai(user_input)
    print(f"\nAI Tutor:\n{answer}\n")
    print("-" * 50)