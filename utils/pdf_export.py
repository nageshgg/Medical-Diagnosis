"""
PDF Report Generator - Exports final diagnosis report as PDF.
"""

from fpdf import FPDF
from datetime import datetime
import os


class MedicalReportPDF(FPDF):
    def header(self):
        self.set_font("Helvetica", "B", 14)
        self.set_text_color(30, 60, 114)
        self.cell(0, 10, "AI Medical Diagnostic Report", align="C", new_x="LMARGIN", new_y="NEXT")
        self.set_font("Helvetica", "", 9)
        self.set_text_color(150, 150, 150)
        self.cell(0, 6, "AI-Generated - For Review by Licensed Physician Only", align="C", new_x="LMARGIN", new_y="NEXT")
        self.ln(4)
        self.set_draw_color(30, 60, 114)
        self.line(10, self.get_y(), 200, self.get_y())
        self.ln(6)

    def footer(self):
        self.set_y(-15)
        self.set_font("Helvetica", "I", 8)
        self.set_text_color(150, 150, 150)
        self.cell(0, 10, f"Page {self.page_no()} | {datetime.now().strftime('%Y-%m-%d %H:%M')} | NOT FOR CLINICAL USE", align="C")

    def section_title(self, title: str):
        self.set_font("Helvetica", "B", 12)
        self.set_text_color(30, 60, 114)
        self.set_fill_color(240, 245, 255)
        self.cell(0, 8, f"  {title}", fill=True, new_x="LMARGIN", new_y="NEXT")
        self.ln(2)
        self.set_text_color(0, 0, 0)

    def body_text(self, text: str):
        self.set_font("Helvetica", "", 10)
        self.set_text_color(40, 40, 40)
        self.multi_cell(0, 6, str(text))
        self.ln(2)

    def key_value(self, key: str, value: str):
        self.set_font("Helvetica", "B", 10)
        self.set_text_color(60, 60, 60)
        self.cell(50, 6, f"{key}:")
        self.set_font("Helvetica", "", 10)
        self.set_text_color(40, 40, 40)
        self.multi_cell(0, 6, str(value))


def generate_pdf_report(patient_profile, research_results, drug_results, critic_results, final_report, output_dir="outputs/reports") -> str:
    os.makedirs(output_dir, exist_ok=True)
    report_id = final_report.get("report_id", "REPORT")
    filename = f"{output_dir}/{report_id}.pdf"

    pdf = MedicalReportPDF()
    pdf.add_page()

    # Header info
    pdf.set_font("Helvetica", "B", 11)
    pdf.cell(0, 7, f"Report ID: {report_id}", new_x="LMARGIN", new_y="NEXT")
    pdf.set_font("Helvetica", "", 10)
    pdf.cell(0, 6, f"Generated: {final_report.get('generated_at', 'N/A')}", new_x="LMARGIN", new_y="NEXT")
    pdf.ln(4)

    # Urgency banner
    urgency = final_report.get("urgency", "Unknown")
    colors = {"Emergency": (220, 50, 50), "Urgent": (220, 130, 50), "Semi-urgent": (200, 170, 50), "Routine": (50, 150, 50)}
    color = colors.get(urgency, (100, 100, 100))
    pdf.set_fill_color(*color)
    pdf.set_text_color(255, 255, 255)
    pdf.set_font("Helvetica", "B", 13)
    pdf.cell(0, 10, f"  URGENCY: {urgency.upper()}", fill=True, new_x="LMARGIN", new_y="NEXT")
    pdf.set_text_color(0, 0, 0)
    pdf.ln(4)

    # Executive Summary
    pdf.section_title("Executive Summary")
    pdf.body_text(final_report.get("executive_summary", "N/A"))

    # Patient Profile
    pdf.section_title("Patient Profile")
    pdf.key_value("Chief Complaint", patient_profile.get("chief_complaint", "N/A"))
    pdf.key_value("Symptoms", ", ".join(patient_profile.get("symptoms", [])))
    pdf.key_value("Duration", patient_profile.get("duration", "N/A"))
    pdf.key_value("Severity", f"{patient_profile.get('severity', 'N/A')}/10")
    pdf.key_value("Conditions", ", ".join(patient_profile.get("existing_conditions", [])) or "None")
    pdf.key_value("Medications", ", ".join(patient_profile.get("current_medications", [])) or "None")
    pdf.key_value("Allergies", ", ".join(patient_profile.get("allergies", [])) or "None")
    pdf.ln(2)

    # Diagnoses
    pdf.section_title("Differential Diagnoses")
    for dx in final_report.get("final_diagnoses", []):
        pdf.set_font("Helvetica", "B", 11)
        pdf.cell(0, 7, f"  {dx.get('rank', '?')}. {dx.get('condition', 'Unknown')} - {dx.get('confidence', 'N/A')}% confidence", new_x="LMARGIN", new_y="NEXT")
        pdf.set_font("Helvetica", "", 10)
        pdf.set_x(20)
        pdf.multi_cell(0, 6, f"ICD-10: {dx.get('icd10', 'N/A')}\nReasoning: {dx.get('reasoning', 'N/A')}")
        if dx.get("next_steps"):
            pdf.set_x(20)
            pdf.multi_cell(0, 6, f"Next Steps: {', '.join(dx['next_steps'])}")
        pdf.ln(2)

    # Medication Safety
    pdf.section_title("Medication Safety")
    pdf.body_text(drug_results.get("pharmacist_notes", "No medication concerns."))
    for i in drug_results.get("cross_interactions", []):
        pdf.set_font("Helvetica", "", 10)
        pdf.multi_cell(0, 6, f"  * {i.get('drug_a')} + {i.get('drug_b')}: {i.get('interaction')} [{i.get('severity')}]")

    # Critic Review
    pdf.section_title("Peer Review")
    pdf.key_value("Quality", critic_results.get("overall_quality", "N/A"))
    pdf.body_text(critic_results.get("critic_verdict", "N/A"))

    # Actions
    pdf.section_title("Recommended Actions")
    for action in final_report.get("recommended_immediate_actions", []):
        pdf.body_text(f"  * {action}")

    # Disclaimer
    pdf.add_page()
    pdf.section_title("Important Disclaimer")
    pdf.set_font("Helvetica", "B", 10)
    pdf.set_text_color(180, 0, 0)
    pdf.multi_cell(0, 7, final_report.get("disclaimer",
        "This report is AI-generated and must be reviewed by a qualified physician. "
        "For educational and research purposes only. Do not use for self-diagnosis or treatment."))

    pdf.output(filename)
    return filename