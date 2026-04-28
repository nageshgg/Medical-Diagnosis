"""
OpenFDA drug interaction checker.
Uses the free OpenFDA API - no key required.
"""

import requests


def check_drug_interactions(medications: list) -> dict:
    base_url = "https://api.fda.gov/drug"
    results = {}

    for drug in medications:
        drug = drug.strip()
        if not drug:
            continue
        try:
            ae_resp = requests.get(f"{base_url}/event.json", params={
                "search": f'patient.drug.medicinalproduct:"{drug}"',
                "count": "patient.reaction.reactionmeddrapt.exact",
                "limit": 5,
            }, timeout=10)

            top_reactions = []
            if ae_resp.status_code == 200:
                for item in ae_resp.json().get("results", [])[:5]:
                    top_reactions.append({"reaction": item.get("term", "Unknown"), "count": item.get("count", 0)})

            label_resp = requests.get(f"{base_url}/label.json", params={
                "search": f'openfda.brand_name:"{drug}"+openfda.generic_name:"{drug}"',
                "limit": 1,
            }, timeout=10)

            warnings = "No warnings data found."
            interactions = "No interaction data found."

            if label_resp.status_code == 200:
                data = label_resp.json()
                if data.get("results"):
                    label = data["results"][0]
                    w = label.get("warnings", label.get("warnings_and_cautions", []))
                    i = label.get("drug_interactions", [])
                    if w:
                        warnings = (w[0] if isinstance(w, list) else str(w))[:400]
                    if i:
                        interactions = (i[0] if isinstance(i, list) else str(i))[:400]

            results[drug] = {
                "top_adverse_reactions": top_reactions,
                "warnings": warnings,
                "drug_interactions": interactions,
            }
        except Exception as e:
            results[drug] = {"error": str(e)}

    return results


def format_drug_data_for_agent(drug_data: dict) -> str:
    if not drug_data:
        return "No medications provided."
    lines = []
    for drug, data in drug_data.items():
        lines.append(f"=== {drug.upper()} ===")
        if "error" in data:
            lines.append(f"  Error: {data['error']}")
            continue
        for r in data.get("top_adverse_reactions", []):
            lines.append(f"  - {r['reaction']} ({r['count']} reports)")
        lines.append(f"  Warnings: {data.get('warnings', 'N/A')[:300]}")
        lines.append(f"  Interactions: {data.get('drug_interactions', 'N/A')[:300]}")
        lines.append("")
    return "\n".join(lines)