import sqlite3

# 1. Open or create the database file
conn = sqlite3.connect("cs_subject.db")
cursor = conn.cursor()

# 2. Create a simple table
cursor.execute("CREATE TABLE IF NOT EXISTS topics (id INTEGER PRIMARY KEY, name TEXT)")

# 3. Add a topic
cursor.execute("INSERT INTO topics (name) VALUES ('Data Structures')")
conn.commit() # Saves the changes

# 4. Read the data back
cursor.execute("SELECT * FROM topics")
print(cursor.fetchall())

# 5. Close the connection
conn.close()