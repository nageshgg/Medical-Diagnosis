"""
LangGraph Workflow - Orchestrates all agents in sequence.
"""

import os
import sys

# Fix imports — always resolve from project root
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)

from typing import TypedDict, Optional
from langgraph.graph import StateGraph, END

from agents.intake_agent import run_intake_agent
from agents.research_agent import run_research_agent
from agents.drug_agent import run_drug_agent
from agents.critic_agent import run_critic_agent
from agents.report_agent import run_report_agent


# ── State ─────────────────────────────────────────────────────────────────────

class MedicalState(TypedDict):
    patient_input: str
    patient_profile: Optional[dict]
    research_results: Optional[dict]
    drug_results: Optional[dict]
    critic_results: Optional[dict]
    final_report: Optional[dict]
    current_step: str
    error: Optional[str]


# ── Nodes ─────────────────────────────────────────────────────────────────────

def intake_node(state: MedicalState) -> MedicalState:
    try:
        profile = run_intake_agent(state["patient_input"])
        return {**state, "patient_profile": profile, "current_step": "intake_complete"}
    except Exception as e:
        return {**state, "error": f"Intake failed: {e}", "current_step": "error"}


def research_node(state: MedicalState) -> MedicalState:
    try:
        results = run_research_agent(state["patient_profile"])
        return {**state, "research_results": results, "current_step": "research_complete"}
    except Exception as e:
        return {**state, "error": f"Research failed: {e}", "current_step": "error"}


def drug_node(state: MedicalState) -> MedicalState:
    try:
        results = run_drug_agent(state["patient_profile"], state["research_results"])
        return {**state, "drug_results": results, "current_step": "drug_complete"}
    except Exception as e:
        return {**state, "error": f"Drug check failed: {e}", "current_step": "error"}


def critic_node(state: MedicalState) -> MedicalState:
    try:
        results = run_critic_agent(state["patient_profile"], state["research_results"], state["drug_results"])
        return {**state, "critic_results": results, "current_step": "critic_complete"}
    except Exception as e:
        return {**state, "error": f"Critic failed: {e}", "current_step": "error"}


def report_node(state: MedicalState) -> MedicalState:
    try:
        report = run_report_agent(
            state["patient_profile"],
            state["research_results"],
            state["drug_results"],
            state["critic_results"]
        )
        return {**state, "final_report": report, "current_step": "complete"}
    except Exception as e:
        return {**state, "error": f"Report failed: {e}", "current_step": "error"}


# ── Graph ─────────────────────────────────────────────────────────────────────

def build_workflow():
    workflow = StateGraph(MedicalState)
    workflow.add_node("intake", intake_node)
    workflow.add_node("research", research_node)
    workflow.add_node("drug", drug_node)
    workflow.add_node("critic", critic_node)
    workflow.add_node("report", report_node)
    workflow.set_entry_point("intake")
    workflow.add_edge("intake", "research")
    workflow.add_edge("research", "drug")
    workflow.add_edge("drug", "critic")
    workflow.add_edge("critic", "report")
    workflow.add_edge("report", END)
    return workflow.compile()


def run_diagnosis(patient_input: str, progress_callback=None) -> dict:
    """
    Run the full multi-agent diagnosis pipeline.
    progress_callback: optional fn(step_key, message) for UI updates.
    """
    app = build_workflow()

    initial_state: MedicalState = {
        "patient_input": patient_input,
        "patient_profile": None,
        "research_results": None,
        "drug_results": None,
        "critic_results": None,
        "final_report": None,
        "current_step": "starting",
        "error": None,
    }

    step_messages = {
        "intake":    "🩺 Intake Agent collecting patient info...",
        "research":  "🔬 Research Agent searching PubMed literature...",
        "drug":      "💊 Drug Agent checking FDA medication data...",
        "critic":    "🔍 Critic Agent peer-reviewing analysis...",
        "report":    "📝 Report Agent writing final diagnosis...",
    }

    final_state = initial_state

    for step_output in app.stream(initial_state):
        for node_name, state in step_output.items():
            if progress_callback and node_name in step_messages:
                progress_callback(node_name, step_messages[node_name])
            final_state = state

    return final_state