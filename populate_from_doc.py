import sqlite3
from docx import Document

DB_NAME = "subject.db"
DOC_NAME = "curriculum_notes.docx"


def populate_db():
  conn = sqlite3.connect(DB_NAME)
  cursor = conn.cursor()

  # Drop old table to start clean
  cursor.execute("DROP TABLE IF EXISTS computer_studies")

  cursor.execute("""
        CREATE TABLE computer_studies (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            country TEXT NOT NULL,
            topic TEXT NOT NULL,
            category TEXT NOT NULL,
            content TEXT NOT NULL
        )
    """)

  doc = Document(DOC_NAME)
  current_country = "Nigeria"
  topic = "Computer System"
  is_keyword_section = False

  for para in doc.paragraphs:
    text = para.text.strip()
    if not text:
      continue

    text_upper = text.upper()
    if "NIGERIA" in text_upper:
      current_country = "Nigeria"
      is_keyword_section = False
      continue
    elif "UNITED STATES" in text_upper or "AMERICA" in text_upper:
      current_country = "USA"
      is_keyword_section = False
      continue
    elif text_upper.startswith("TOPIC:"):
      continue

    # Clean up Word bullet characters like '' or '-'
    cleaned_text = text.lstrip("-•* \t")
    if not cleaned_text:
      continue

    if "keyword" in text.lower():
      is_keyword_section = True
      category = "Keywords"
    elif is_keyword_section:
      category = "Keywords"
    else:
      category = "Definition"

    cursor.execute(
        """
            INSERT INTO computer_studies (country, topic, category, content)
            VALUES (?, ?, ?, ?)
        """,
        (current_country, topic, category, cleaned_text),
    )

  conn.commit()
  conn.close()
  print(
      f"Success! Database '{DB_NAME}' updated with clean text and correct"
      " categories."
  )


if __name__ == "__main__":
  populate_db()