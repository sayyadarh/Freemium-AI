import ollama

# 1. System prompt updated to enforce concise, direct answers
messages_history = [
    {
        "role": "system",
        "content": (
            "You are a concise offline educational assistant for students. "
            "Keep your explanations brief, clear, and strictly to the point. "
            "Use simple formatting or bullet points when helpful, but do not "
            "provide long background details or extra fluff unless explicitly requested."
        )
    }
]
print("=== Concise Offline AI Tutor Initialized ===")
print("Type your question below. Type 'exit' or 'quit' to stop.\n")

# 2. Main interactive chat loop 
while True:
    user_input = input("Student: ")
    
    # Check for exit command
    if user_input.strip().lower() in ["exit", "quit"]:
        print("\nClosing app. Happy studying!")
        break
    
    # Skip empty lines
    if not user_input.strip():
        continue

    # Add student prompt to history
    messages_history.append({"role": "user", "content": user_input})
    
    print("\nAI Tutor: ", end="", flush=True)

    try:
        # Stream response from the local llama3.2:1b model
        full_response = ""
        response_stream = ollama.chat(
            model="llama3.2:1b",
            messages=messages_history,
            stream=True
        )

        for chunk in response_stream:
            text_chunk = chunk['message']['content']
            print(text_chunk, end="", flush=True)
            full_response += text_chunk

        print("\n")  # Spacing after response
        
        # Save response to history for conversation context
        messages_history.append({"role": "assistant", "content": full_response})

    except Exception as e:
        print(f"\nAn error occurred: {e}\n")
        