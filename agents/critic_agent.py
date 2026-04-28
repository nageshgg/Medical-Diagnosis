"""
Critic Agent - Peer reviews all other agents and flags issues.
"""

import os
import json
from groq import Groq
from dotenv import load_dotenv

load_dotenv()
client = Groq()

SYSTEM_PROMPT = """You are a senior attending physician doing critical peer review of an AI diagnostic system.

Your job is to be skeptical, thorough, and catch anything the other agents missed or got wrong.

Return ONLY a valid JSON object:
{
  "overall_quality": "Excellent/Good/Acceptable/Poor",
  "diagnosis_critique": [
    {
      "diagnosis": "Condition Name",
      "critique": "What's right or wrong",
      "confidence_adjustment": "Increase/Decrease/Keep",
      "missed_consideration": "What was overlooked"
    }
  ],
  "missed_diagnoses": [
    {
      "condition": "Missed Condition",
      "reason_it_fits": "Why this should have been considered",
      "likelihood": "High/Medium/Low"
    }
  ],
  "medication_concerns": ["concern 1"],
  "red_flags_missed": ["critical finding overlooked"],
  "contradictions": ["contradiction between agents"],
  "overconfident_claims": ["claim needing more evidence"],
  "questions_to_investigate": ["What else should we know?"],
  "urgency_reassessment": "Emergency/Urgent/Semi-urgent/Routine",
  "critic_verdict": "Overall assessment in 2-3 sentences"
}

Be genuinely critical. Return ONLY valid JSON.
"""


def run_critic_agent(patient_profile: dict, research_results: dict, drug_results: dict) -> dict:
    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        max_tokens=2000,
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": f"""Review this AI medical analysis:

=== PATIENT PROFILE ===
{json.dumps(patient_profile, indent=2)}

=== RESEARCH AGENT (Differential Diagnoses) ===
Urgency: {research_results.get('urgency_level')}
Red Flags: {research_results.get('red_flags', [])}
Diagnoses: {json.dumps(research_results.get('differential_diagnoses', []), indent=2)}

=== DRUG AGENT (Medication Safety) ===
Overall Safety: {drug_results.get('overall_medication_safety')}
Cross Interactions: {json.dumps(drug_results.get('cross_interactions', []), indent=2)}
Contraindications: {json.dumps(drug_results.get('contraindications_with_diagnoses', []), indent=2)}

What did the agents get wrong, miss, or overstate? Return critique as JSON."""}
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
            "overall_quality": "Unknown",
            "diagnosis_critique": [],
            "missed_diagnoses": [],
            "medication_concerns": [],
            "red_flags_missed": [],
            "contradictions": [],
            "overconfident_claims": [],
            "questions_to_investigate": [],
            "urgency_reassessment": "Urgent",
            "critic_verdict": raw[:500]
        }