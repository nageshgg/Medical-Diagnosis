"""
Research Agent - Searches PubMed and generates differential diagnoses.
"""

import os
import sys
import json
from groq import Groq
from dotenv import load_dotenv

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from tools.pubmed_search import search_pubmed, format_articles_for_agent

load_dotenv()
client = Groq()

SYSTEM_PROMPT = """You are a senior medical researcher and diagnostician.

Given a patient profile and medical literature, provide a differential diagnosis.

Return ONLY a valid JSON object:
{
  "differential_diagnoses": [
    {
      "condition": "Condition Name",
      "icd10_code": "X00.0",
      "likelihood": "High/Medium/Low",
      "confidence_percent": 75,
      "supporting_symptoms": ["symptom1"],
      "against_symptoms": ["symptom that doesn't fit"],
      "reasoning": "Brief clinical reasoning",
      "recommended_tests": ["test1"]
    }
  ],
  "red_flags": ["urgent symptom to watch for"],
  "urgency_level": "Emergency/Urgent/Semi-urgent/Routine",
  "literature_summary": "Brief summary of what the literature says",
  "sources_used": ["pubmed url1"]
}

Return top 3-5 diagnoses ranked by likelihood. Return ONLY valid JSON.
"""


def run_research_agent(patient_profile: dict) -> dict:
    symptoms = patient_profile.get("symptoms", [])
    chief_complaint = patient_profile.get("chief_complaint", "")
    search_query = f"{chief_complaint} {' '.join(symptoms[:3])} diagnosis"

    articles = search_pubmed(search_query, max_results=5)
    literature = format_articles_for_agent(articles)
    source_urls = [a["url"] for a in articles]

    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        max_tokens=2000,
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": f"""Patient Profile:
{json.dumps(patient_profile, indent=2)}

Relevant Medical Literature from PubMed:
{literature}

Available source URLs: {source_urls}

Provide a comprehensive differential diagnosis as JSON."""}
        ]
    )

    raw = response.choices[0].message.content.strip()
    if raw.startswith("```"):
        raw = raw.split("```")[1]
        if raw.startswith("json"):
            raw = raw[4:]

    try:
        result = json.loads(raw)
        result["pubmed_articles"] = articles
        return result
    except json.JSONDecodeError:
        return {
            "differential_diagnoses": [],
            "red_flags": [],
            "urgency_level": "Unknown",
            "literature_summary": raw,
            "sources_used": source_urls,
            "pubmed_articles": articles
        }