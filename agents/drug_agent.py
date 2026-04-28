"""
Drug Agent - Checks medications and flags interaction risks.
"""

import os
import sys
import json
from groq import Groq
from dotenv import load_dotenv

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from tools.fda_checker import check_drug_interactions, format_drug_data_for_agent

load_dotenv()
client = Groq()

SYSTEM_PROMPT = """You are a clinical pharmacist with expertise in drug interactions and medication safety.

Given a patient's medication list and FDA data, analyze medication safety.

Return ONLY a valid JSON object:
{
  "medication_analysis": [
    {
      "medication": "Drug Name",
      "known_interactions": ["interacts with Drug X causing Y"],
      "relevant_warnings": "key warning text",
      "top_adverse_effects": ["effect1"],
      "severity": "Safe/Caution/Warning/Danger"
    }
  ],
  "cross_interactions": [
    {
      "drug_a": "Drug 1",
      "drug_b": "Drug 2",
      "interaction": "Description",
      "severity": "Mild/Moderate/Severe"
    }
  ],
  "contraindications_with_diagnoses": [
    {
      "medication": "Drug",
      "diagnosis": "Condition",
      "concern": "Why this is a problem"
    }
  ],
  "overall_medication_safety": "Safe/Review Needed/Immediate Review Required",
  "pharmacist_notes": "Overall assessment and recommendations"
}

Return ONLY valid JSON.
"""


def run_drug_agent(patient_profile: dict, research_results: dict) -> dict:
    medications = patient_profile.get("current_medications", [])

    if not medications:
        return {
            "medication_analysis": [],
            "cross_interactions": [],
            "contraindications_with_diagnoses": [],
            "overall_medication_safety": "No medications to review",
            "pharmacist_notes": "Patient has no current medications listed."
        }

    fda_data = check_drug_interactions(medications)
    fda_formatted = format_drug_data_for_agent(fda_data)
    diagnoses = [d.get("condition", "") for d in research_results.get("differential_diagnoses", [])]

    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        max_tokens=2000,
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": f"""Patient Medications: {medications}
Patient Allergies: {patient_profile.get('allergies', [])}
Existing Conditions: {patient_profile.get('existing_conditions', [])}
Possible Diagnoses: {diagnoses}

FDA Drug Data:
{fda_formatted}

Analyze medication safety and interactions. Return as JSON."""}
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
            "medication_analysis": [],
            "cross_interactions": [],
            "contraindications_with_diagnoses": [],
            "overall_medication_safety": "Review Needed",
            "pharmacist_notes": raw
        }