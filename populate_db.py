import sqlite3

# 1. Connect to your database
conn = sqlite3.connect("cs_subject.db")
cursor = conn.cursor()

# 2. Make sure the table exists
cursor.execute(
    """
CREATE TABLE IF NOT EXISTS topics (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    subject TEXT,
    topic TEXT,
    definition TEXT
    
)
"""
)

# 3. List of Computer Studies topics to insert
computer_studies_data = [
    (
        "Computer Studies",
        "Fundamentals of Computing",
        "The study of algorithms, data structures, and computer hardware/software design.",
    ),
    (
        "Computer Studies",
        "Input and Output Devices",
        "Hardware components used to enter data into a computer and display results.",
    ),
    (
        "Computer Studies",
        "Computer Networks",
        "A collection of interconnected computers that share resources and communication.",
    ),
    (
        "Computer Studies",
        "Database Management Systems",
        "Software used to create, manage, and manipulate structured data safely.",
    ),
    (
        "Computer Studies",
        "Operating Systems",
        "System software that manages computer hardware, software resources, and common services.",
    ),
    (
        "Computer Studies",
        "Cybersecurity & Data Safety",
        "Practices and tools designed to protect networks, devices, and data from unauthorized access.",
    ),
]

# 4. Insert all rows into the database
cursor.executemany(
    "INSERT INTO topics (subject, topic, definition) VALUES (?, ?, ?)",
    computer_studies_data,
)

# 5. Save and close
conn.commit()
conn.close()

print("Successfully uploaded Computer Studies topics to SQLite database!")