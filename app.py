import sqlite3
import ollama

# 1. Fetch a topic from your SQLite database
def get_topic_from_db(topic_id):
    conn = sqlite3.connect("cs_subject.db")
    cursor = conn.cursor()
    
    cursor.execute("SELECT name FROM topics WHERE id = ?", (topic_id,))
    result = cursor.fetchone()
    
    conn.close()
    
    if result:
        return result[0]
    return None

# 2. Query Llama 3.2 to explain the topic
def explain_topic_with_ai(topic_name):
    prompt = f"You are a friendly computer science tutor. Explain the concept of '{topic_name}' in simple terms for a secondary school student."
    
    response = ollama.chat(
        model="llama3.2",
        messages=[{"role": "user", "content": prompt}]
    )
    
    return response["message"]["content"]

# --- Main Program Execution ---
if __name__ == "__main__":
    # Get the topic with ID 1 ('Data Structures')
    topic = get_topic_from_db(1)
    
    if topic:
        print(f"--- Fetching explanation for: {topic} ---\n")
        explanation = explain_topic_with_ai(topic)
        print(explanation)
    else:
        print("Topic not found in database.")