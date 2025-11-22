import os
from dotenv import load_dotenv

from google.genai.client import Client
from google.genai import types

load_dotenv()

API_KEY = "AIzaSyDBRE32l8dQvO5ndBt1taGBEDo60t_rsms"

client = Client(api_key=API_KEY)

# ---------------------------------------------------
# STRICT COMBINED PROMPT (JSON + HTML only)
# ---------------------------------------------------
MASTER_PROMPT = """
You are a multilingual educational assistant.

You will receive student information + a question.
Use the student profile to generate an answer suitable for their learning level.

# STEP 1 — Detect Target Language
Rules:
1. If the question clearly asks for a language → use that.
2. Otherwise, detect the language of the question.
3. If mixed languages without preference → default to English.

Return inside final JSON:
{
  "target_language": "<language>"
}

# STEP 2 — Generate Final Answer
Use student details (grade, medium, learning level, subject)
to tailor the explanation appropriately.

Your final output MUST be a single valid JSON object:

{
  "student": {
    "full_name": "<full name>",
    "grade": "<grade>",
    "medium": "<medium>",
    "school_name": "<school>",
    "learning_level": "<level>",
    "subject": "<subject>"
  },
  "languageDetection": {
    "target_language": "<language>"
  },
  "response": "<plain answer in that language>",
  "html": "<p>HTML formatted answer</p>"
}

STRICT RULES:
- Output ONLY valid JSON.
- NO markdown.
- NO backticks.
- NO extra comments.
- MUST be one single JSON object.
"""

def run_agent(payload_text: str):
    response = client.models.generate_content(
        model="gemini-2.5-flash",
        contents=[
            types.Part(text=MASTER_PROMPT),
            types.Part(text=payload_text),
        ]
    )
    return response.text.strip()


def get_llm_result(payload):
    result = run_agent(payload)
    return result

def main():
    print("\n--- Enter Student Details ---")
    full_name = input("Full Name: ")
    grade = input("Grade: ")
    medium = input("Medium (English/Tamil/etc.): ")
    school_name = input("School Name: ")
    learning_level = input("Learning Level (Beginner/Intermediate/Advanced): ")
    subject = input("Subject: ")

    user_question = input("\nEnter your question: ")

    # Combine everything into one text block
    payload = f"""
        Student Info:
        Full Name: {full_name}
        Grade: {grade}
        Medium: {medium}
        School Name: {school_name}
        Learning Level: {learning_level}
        Subject: {subject}

        Question: {user_question}
    """

    print("\nProcessing…")
    result = run_agent(payload)

    print("\n=========== FINAL JSON OUTPUT ===========")
    print(result)
    print("=========================================\n")


if __name__ == "__main__":
    main()