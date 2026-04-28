"""
Intake Agent - Collects and structures patient information.
"""

import os
import json
from groq import Groq
from dotenv import load_dotenv

load_dotenv()
client = Groq()

SYSTEM_PROMPT = """You are a medical intake specialist AI assistant.

From the patient input, extract and return ONLY a valid JSON object:
{
  "chief_complaint": "main reason for visit in one sentence",
  "symptoms": ["symptom1", "symptom2"],
  "duration": "how long symptoms have been present",
  "severity": 5,
  "existing_conditions": ["condition1"],
  "current_medications": ["med1"],
  "allergies": ["allergy1"],
  "age": null,
  "gender": null,
  "additional_notes": "any other relevant info"
}

severity is 1-10. Use null for unknown fields. Return ONLY valid JSON, no other text.
"""


def run_intake_agent(patient_input: str) -> dict:
    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        max_tokens=1000,
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": f"Patient description:\n{patient_input}\n\nExtract structured medical info as JSON."}
        ]
    )

    raw = response.choices[0].message.content.strip()
    if raw.startswith("```"):
        raw = raw.split("```")[1]
        if raw.startswith("json"):
            raw = raw[4:]

    try:
        return json.loads(raw)
    except json.JSONDecodeError:
        return {
            "chief_complaint": patient_input[:200],
            "symptoms": [patient_input],
            "duration": "unknown",
            "severity": 5,
            "existing_conditions": [],
            "current_medications": [],
            "allergies": [],
            "age": None,
            "gender": None,
            "additional_notes": ""
        }