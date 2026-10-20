import sqlite3

from pypdf import PdfReader

# 1. Open and read your PDF file
pdf_path = "computer_studies_db.py.pdf"
reader = PdfReader(pdf_path)

extracted_lines = []

# Loop through every page in the PDF and extract text line by line
for page in reader.pages:
    text = page.extract_text()
    if text:
        # Clean up and split text into separate lines
        lines = [line.strip() for line in text.split("\n") if line.strip()]
        extracted_lines.extend(lines)

# 2. Connect to your SQLite database file
conn = sqlite3.connect("cs_subject.db")
cursor = conn.cursor()

# Drop the old table if it exists so we start fresh with the right columns
cursor.execute("DROP TABLE IF EXISTS topics")

# Create the correct table structure
cursor.execute(
    """
CREATE TABLE topics (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    content TEXT
)
"""
)

# 3. Loop through each extracted line and save it into SQLite
for line in extracted_lines:
    cursor.execute("INSERT INTO topics (content) VALUES (?)", (line,))

# Save changes and close the connection
conn.commit()
conn.close()

print(
    f"Done! Saved {len(extracted_lines)} lines from the PDF into cs_subject.db."
)