"""
Report Agent - Synthesizes all agent outputs into a final medical report.
"""

import os
import json
from groq import Groq
from dotenv import load_dotenv
from datetime import datetime

load_dotenv()
client = Groq()

SYSTEM_PROMPT = """You are a senior physician writing a final diagnostic report.

Synthesize all the analysis from the medical team into a clear, professional report.
Consider the critic agent's feedback and adjust accordingly.

Return ONLY a valid JSON object:
{
  "executive_summary": "2-3 sentence overview for the doctor",
  "patient_summary": "Brief patient presentation",
  "final_diagnoses": [
    {
      "rank": 1,
      "condition": "Most Likely Diagnosis",
      "confidence": 75,
      "icd10": "X00.0",
      "reasoning": "Why this is most likely",
      "next_steps": ["test1", "test2"]
    }
  ],
  "urgency": "Emergency/Urgent/Semi-urgent/Routine",
  "urgency_reasoning": "Why this urgency level",
  "recommended_immediate_actions": ["action1"],
  "recommended_tests": ["test1"],
  "medication_summary": "Summary of medication concerns",
  "specialist_referrals": ["Refer to cardiologist for..."],
  "follow_up": "Recommended follow-up timeline",
  "key_questions_for_patient": ["Question the doctor should ask"],
  "disclaimer": "AI-generated report. Must be reviewed by qualified physician before clinical use."
}

Return ONLY valid JSON.
"""


def run_report_agent(patient_profile: dict, research_results: dict, drug_results: dict, critic_results: dict) -> dict:
    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        max_tokens=3000,
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": f"""Synthesize this multi-agent medical analysis into a final report:

PATIENT: {json.dumps(patient_profile, indent=2)}

RESEARCH FINDINGS:
- Urgency: {research_results.get('urgency_level')}
- Top Diagnoses: {[d.get('condition') for d in research_results.get('differential_diagnoses', [])[:3]]}
- Red Flags: {research_results.get('red_flags', [])}

MEDICATION SAFETY:
- Overall: {drug_results.get('overall_medication_safety')}
- Notes: {drug_results.get('pharmacist_notes', '')[:300]}

CRITIC REVIEW:
- Quality: {critic_results.get('overall_quality')}
- Missed Diagnoses: {[d.get('condition') for d in critic_results.get('missed_diagnoses', [])]}
- Verdict: {critic_results.get('critic_verdict', '')}
- Urgency Reassessment: {critic_results.get('urgency_reassessment')}

Full Diagnoses: {json.dumps(research_results.get('differential_diagnoses', [])[:3], indent=2)}

Write the final integrated report as JSON."""}
        ]
    )

    raw = response.choices[0].message.content.strip()
    if raw.startswith("```"):
        raw = raw.split("```")[1]
        if raw.startswith("json"):
            raw = raw[4:]

    try:
        result = json.loads(raw)
        result["generated_at"] = datetime.now().isoformat()
        result["report_id"] = f"RPT-{datetime.now().strftime('%Y%m%d-%H%M%S')}"
        return result
    except json.JSONDecodeError:
        return {
            "executive_summary": raw[:500],
            "urgency": critic_results.get("urgency_reassessment", "Urgent"),
            "final_diagnoses": [],
            "disclaimer": "AI-generated report. Must be reviewed by qualified physician.",
            "generated_at": datetime.now().isoformat(),
            "report_id": f"RPT-{datetime.now().strftime('%Y%m%d-%H%M%S')}"
        }